import hashlib
import hmac
import json
import logging
import re
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, Form, Header, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import engine, get_session
from .schemas import CreateLinkRequest, LinkResponse, ReadinessResponse, UpdateLinkRequest
from .service import create_link, get_link, link_status, record_click, tombstone_link, update_link

templates = Jinja2Templates(directory="templates")
logger = logging.getLogger("secure_shortener")
logging.basicConfig(level=logging.INFO, format="%(message)s")
REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,100}$")
CODE = r"^[A-Za-z0-9_-]{6,32}$"
rate_events: dict[str, deque[float]] = defaultdict(deque)
metrics = {"requests_total": 0, "redirects_total": 0, "errors_total": 0, "rate_limited_total": 0}


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.identities()
    yield
    await engine.dispose()


app = FastAPI(
    title="Secure URL Shortener", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None
)
app.mount("/static", StaticFiles(directory="static"), name="static")


def request_id(request: Request) -> str:
    candidate = request.headers.get("x-request-id", "")
    return candidate if REQUEST_ID.fullmatch(candidate) else str(uuid.uuid4())


def error_response(request: Request, code: str, message: str, http_status: int) -> JSONResponse:
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=http_status, content={"error": code, "message": message[:300], "requestId": rid}
    )


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    code = {
        401: "unauthenticated",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        410: "gone",
        429: "rate_limited",
    }.get(exc.status_code, "bad_request")
    response = error_response(request, code, str(exc.detail), exc.status_code)
    if exc.headers:
        response.headers.update(exc.headers)
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, _: RequestValidationError):
    return error_response(request, "validation_error", "request validation failed", 422)


@app.exception_handler(Exception)
async def unexpected_error(request: Request, _: Exception):
    metrics["errors_total"] += 1
    return error_response(request, "internal_error", "an internal error occurred", 500)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request.state.request_id = request_id(request)
    start = time.perf_counter()
    metrics["requests_total"] += 1
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    route_code = request.path_params.get("code")
    logger.info(
        json.dumps(
            {
                "event": "request",
                "method": request.method,
                "path": request.url.path,
                "codeHash": hashlib.sha256(route_code.encode()).hexdigest()[:12]
                if route_code
                else None,
                "status": response.status_code,
                "durationMs": round((time.perf_counter() - start) * 1000, 2),
                "requestId": request.state.request_id,
            }
        )
    )
    return response


class Identity:
    def __init__(self, owner_id: str, admin: bool = False):
        self.owner_id = owner_id
        self.admin = admin


async def authenticate(authorization: str | None = Header(default=None)) -> Identity:
    scheme, _, presented = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not presented:
        raise HTTPException(
            401, "valid bearer authentication is required", headers={"WWW-Authenticate": "Bearer"}
        )
    owners, admins = settings.identities()
    for identity, expected in [*admins.items(), *owners.items()]:
        if hmac.compare_digest(presented, expected):
            return Identity(identity, identity in admins)
    raise HTTPException(
        401, "valid bearer authentication is required", headers={"WWW-Authenticate": "Bearer"}
    )


def check_rate_limit(key: str) -> None:
    now = time.monotonic()
    events = rate_events[key]
    while events and events[0] <= now - settings.rate_window_seconds:
        events.popleft()
    if len(events) >= settings.local_rate_limit:
        metrics["rate_limited_total"] += 1
        raise HTTPException(
            429, "rate limit exceeded", headers={"Retry-After": str(settings.rate_window_seconds)}
        )
    events.append(now)


def as_response(link) -> LinkResponse:
    return LinkResponse(
        code=link.code,
        shortUrl=f"/r/{link.code}",
        destination=link.destination,
        createdAt=link.created_at,
        expiresAt=link.expires_at,
        enabled=not bool(link.disabled_at),
        status=link_status(link),
        ownerId=link.owner_id,
    )


def authorize(link, identity: Identity) -> None:
    if not identity.admin and link.owner_id != identity.owner_id:
        raise HTTPException(403, "caller is not authorized for this link")


def lifecycle_error(link) -> None:
    current = link_status(link)
    if current in {"deleted", "expired", "disabled"}:
        raise HTTPException(410, "link is no longer active")


@app.get("/healthz")
async def health():
    return {"status": "ok"}


@app.get("/readyz", response_model=ReadinessResponse)
async def readiness(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(503, "database unavailable") from exc
    return {"status": "ready", "dependencies": {"database": "ok"}}


@app.get("/internal/metrics", dependencies=[Depends(authenticate)])
async def metrics_endpoint():
    return Response(
        "".join(f"shortener_{key} {value}\n" for key, value in metrics.items()),
        media_type="text/plain; version=0.0.4",
    )


@app.post("/v1/links", response_model=LinkResponse, status_code=201)
async def create(
    payload: CreateLinkRequest,
    request: Request,
    identity: Identity = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
):
    check_rate_limit(f"create:{identity.owner_id}")
    try:
        link = await create_link(
            session, str(payload.destination), identity.owner_id, payload.code, payload.expires_at
        )
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    response = JSONResponse(
        status_code=201, content=as_response(link).model_dump(by_alias=True, mode="json")
    )
    response.headers["Location"] = f"/r/{link.code}"
    return response


@app.get("/v1/links/{code}", response_model=LinkResponse)
async def get_management(
    code: str = Path(..., pattern=CODE),
    identity: Identity = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
):
    link = await get_link(session, code)
    if not link:
        raise HTTPException(404, "link not found")
    authorize(link, identity)
    lifecycle_error(link)
    return as_response(link)


@app.patch("/v1/links/{code}", response_model=LinkResponse)
async def patch_management(
    payload: UpdateLinkRequest,
    code: str = Path(..., pattern=CODE),
    identity: Identity = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
):
    link = await get_link(session, code)
    if not link:
        raise HTTPException(404, "link not found")
    authorize(link, identity)
    if link_status(link) in {"expired", "deleted"}:
        raise HTTPException(410, "link is no longer active")
    try:
        link = await update_link(
            session,
            link,
            str(payload.destination) if payload.destination else None,
            payload.expires_at,
            payload.enabled,
        )
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return as_response(link)


@app.delete("/v1/links/{code}", status_code=204)
async def delete_management(
    code: str = Path(..., pattern=CODE),
    identity: Identity = Depends(authenticate),
    session: AsyncSession = Depends(get_session),
):
    link = await get_link(session, code)
    if not link:
        raise HTTPException(404, "link not found")
    authorize(link, identity)
    if link.deleted_at:
        raise HTTPException(410, "link is already deleted")
    await tombstone_link(session, link)


@app.get("/r/{code}")
async def resolve(
    code: str = Path(..., pattern=CODE), session: AsyncSession = Depends(get_session)
):
    check_rate_limit("resolve")
    link = await get_link(session, code)
    if not link:
        raise HTTPException(404, "link not found")
    lifecycle_error(link)
    await record_click(session, link)
    metrics["redirects_total"] += 1
    response = RedirectResponse(link.destination, status_code=302)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/ui/links", response_class=HTMLResponse)
async def create_ui(
    request: Request,
    destination: str = Form(...),
    token: str = Form(...),
    code: str | None = Form(default=None),
    session: AsyncSession = Depends(get_session),
):
    client_key = request.client.host if request.client else "unknown"
    check_rate_limit(f"ui-create:{client_key}")
    origin = request.headers.get("origin")
    expected_origin = f"{request.url.scheme}://{request.headers.get('host', request.url.netloc)}"
    if origin and (
        urlsplit(origin).scheme != request.url.scheme
        or urlsplit(origin).netloc != urlsplit(expected_origin).netloc
    ):
        raise HTTPException(403, "cross-origin form submission is not allowed")
    owners, _ = settings.identities()
    identity = next(
        (
            Identity(owner, False)
            for owner, expected in owners.items()
            if hmac.compare_digest(token, expected)
        ),
        None,
    )
    if identity is None:
        check_rate_limit(f"ui-auth:{client_key}")
        raise HTTPException(401, "valid owner token is required")
    try:
        payload = CreateLinkRequest(destination=destination, code=code or None)
        await create_link(
            session, str(payload.destination), identity.owner_id, payload.code, payload.expires_at
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return await home(request)
