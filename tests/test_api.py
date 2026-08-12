from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from secure_shortener import main
from secure_shortener.db import Base, get_session


@pytest.fixture
async def client(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///" + str(tmp_path / "test.db"))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override():
        async with session_factory() as session:
            yield session

    main.app.dependency_overrides[get_session] = override
    main.settings.owner_tokens = "owner-a:owner-token,owner-b:other-token"
    main.settings.admin_tokens = "admin:admin-token"
    main.settings.local_rate_limit = 100
    main.rate_events.clear()
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as ac:
        yield ac
    main.app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_redirect_location_and_click_count(client):
    response = await client.post(
        "/v1/links",
        headers={"Authorization": "Bearer owner-token"},
        json={"destination": "https://example.com/docs", "code": "docs-1"},
    )
    assert response.status_code == 201
    assert response.headers["location"] == "/r/docs-1"
    redirect = await client.get("/r/docs-1", follow_redirects=False)
    assert redirect.status_code == 302
    assert redirect.headers["location"] == "https://example.com/docs"
    assert redirect.headers["cache-control"] == "no-store"
    details = await client.get("/v1/links/docs-1", headers={"Authorization": "Bearer owner-token"})
    assert details.status_code == 200
    assert details.json()["code"] == "docs-1"


@pytest.mark.asyncio
async def test_auth_ownership_and_admin(client):
    await client.post(
        "/v1/links",
        headers={"Authorization": "Bearer owner-token"},
        json={"destination": "https://example.com", "code": "owned-1"},
    )
    assert (await client.get("/v1/links/owned-1")).status_code == 401
    assert (
        await client.get("/v1/links/owned-1", headers={"Authorization": "Bearer other-token"})
    ).status_code == 403
    assert (
        await client.get("/v1/links/owned-1", headers={"Authorization": "Bearer admin-token"})
    ).status_code == 200
    assert (
        await client.get("/v1/links/owned-1", headers={"Authorization": "Token owner-token"})
    ).status_code == 401


@pytest.mark.asyncio
async def test_tombstone_and_code_never_reused(client):
    headers = {"Authorization": "Bearer owner-token"}
    await client.post(
        "/v1/links",
        headers=headers,
        json={"destination": "https://example.com", "code": "delete-1"},
    )
    assert (await client.delete("/v1/links/delete-1", headers=headers)).status_code == 204
    assert (await client.get("/r/delete-1")).status_code == 410
    assert (await client.get("/v1/links/delete-1", headers=headers)).status_code == 410
    assert (
        await client.post(
            "/v1/links",
            headers=headers,
            json={"destination": "https://example.com", "code": "delete-1"},
        )
    ).status_code == 409


@pytest.mark.asyncio
async def test_disable_expiry_and_patch_rules(client):
    headers = {"Authorization": "Bearer owner-token"}
    await client.post(
        "/v1/links",
        headers=headers,
        json={
            "destination": "https://example.com",
            "code": "state-1",
            "expiresAt": (datetime.now(UTC) + timedelta(minutes=1)).isoformat(),
        },
    )
    assert (
        await client.patch("/v1/links/state-1", headers=headers, json={"enabled": False})
    ).status_code == 200
    assert (await client.get("/r/state-1")).status_code == 410
    assert (
        await client.patch("/v1/links/state-1", headers=headers, json={"enabled": True})
    ).status_code == 200


@pytest.mark.asyncio
async def test_error_envelope_and_ui_does_not_list_links(client):
    response = await client.get("/r/unknown1", headers={"X-Request-ID": "audit-123"})
    assert response.status_code == 404
    assert response.json()["requestId"] == "audit-123"
    page = await client.get("/")
    assert page.status_code == 200
    assert "Current links" not in page.text


@pytest.mark.asyncio
async def test_ui_origin_and_token_controls(client):
    cross_origin = await client.post(
        "/ui/links",
        headers={"Origin": "https://attacker.example"},
        data={"destination": "https://example.com", "token": "owner-token"},
    )
    assert cross_origin.status_code == 403
    invalid_token = await client.post(
        "/ui/links", data={"destination": "https://example.com", "token": "wrong-token"}
    )
    assert invalid_token.status_code == 401
