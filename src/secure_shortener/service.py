import secrets
import string
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Link

ALPHABET = string.ascii_letters + string.digits + "_-"


def new_code(size: int = 8) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(size))


def link_status(link: Link, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    if link.deleted_at:
        return "deleted"
    expiry = link.expires_at
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=UTC)
    if expiry and expiry <= now:
        return "expired"
    if link.disabled_at:
        return "disabled"
    return "active"


async def create_link(
    session: AsyncSession,
    destination: str,
    owner_id: str,
    code: str | None,
    expires_at: datetime | None,
) -> Link:
    for _ in range(5):
        candidate = code or new_code()
        link = Link(
            code=candidate, owner_id=owner_id, destination=destination, expires_at=expires_at
        )
        session.add(link)
        try:
            await session.commit()
            await session.refresh(link)
            return link
        except IntegrityError as exc:
            await session.rollback()
            if code:
                raise ValueError("code already exists") from exc
    raise ValueError("could not allocate a unique code")


async def get_link(session: AsyncSession, code: str) -> Link | None:
    return await session.scalar(select(Link).where(Link.code == code))


async def record_click(session: AsyncSession, link: Link) -> None:
    now = datetime.now(UTC)
    await session.execute(
        update(Link)
        .where(Link.id == link.id)
        .values(click_count=Link.click_count + 1, last_accessed_at=now)
    )
    await session.commit()


async def update_link(
    session: AsyncSession,
    link: Link,
    destination: str | None,
    expires_at: datetime | None,
    enabled: bool | None,
) -> Link:
    now = datetime.now(UTC)
    current = link_status(link, now)
    if current in {"deleted", "expired"}:
        raise ValueError("link cannot be re-enabled or extended in its current state")
    values: dict[str, object] = {}
    if destination is not None:
        values["destination"] = destination
    if expires_at is not None:
        existing_expiry = link.expires_at
        if existing_expiry and existing_expiry.tzinfo is None:
            existing_expiry = existing_expiry.replace(tzinfo=UTC)
        if existing_expiry and expires_at > existing_expiry:
            raise ValueError("expiry may only be shortened")
        if expires_at <= now:
            raise ValueError("expiresAt must be in the future")
        values["expires_at"] = expires_at
    if enabled is True:
        values["disabled_at"] = None
    elif enabled is False:
        values["disabled_at"] = now
    if not values:
        raise ValueError("at least one update field is required")
    await session.execute(update(Link).where(Link.id == link.id).values(**values))
    await session.commit()
    await session.refresh(link)
    return link


async def tombstone_link(session: AsyncSession, link: Link) -> None:
    await session.execute(
        update(Link).where(Link.id == link.id).values(deleted_at=datetime.now(UTC))
    )
    await session.commit()
