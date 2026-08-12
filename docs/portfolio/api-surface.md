# API surface and contract boundary

This is the recruiter-facing summary of the executable local service. The
normative schemas and response descriptions are in
[`docs/api/openapi.yaml`](../api/openapi.yaml). The AWS design is not deployed.

## Service and management routes

| Method | Path | Auth | Success and lifecycle behavior |
|---|---|---|---|
| `GET` | `/healthz` | None | `200` when the process is serving |
| `GET` | `/readyz` | None | `200` with database dependency status; `503` when unavailable |
| `GET` | `/internal/metrics` | Owner/admin bearer | `200` plain-text process counters |
| `POST` | `/v1/links` | Owner/admin bearer | Creates an owned link; `201` and `Location: /r/{code}` |
| `GET` | `/v1/links/{code}` | Owner/admin bearer | Owner/admin metadata read; `200`, `404`, or `410` |
| `PATCH` | `/v1/links/{code}` | Owner/admin bearer | Update destination, expiry, or enabled state; `200`, `404`, or `409` |
| `DELETE` | `/v1/links/{code}` | Owner/admin bearer | Tombstones the link; `204`, `404`, or `410` |
| `GET` | `/r/{code}` | None | Public resolver; `302` and `Cache-Control: no-store`, or `404`/`410` |

Codes are 6–32 characters from letters, digits, `_`, and `-`. Unknown codes
return `404`. Disabled, expired, and deleted codes return `410`; deleted codes
remain tombstoned and cannot be reused. Rate-limited requests return `429`
with `Retry-After`.

## Identity and responses

The service validates opaque bearer tokens but does not issue tokens. A local
owner identity can create and manage its own links; an administrator can manage
all links. Missing or invalid credentials return `401`; an authenticated caller
without ownership returns `403`. Errors use the JSON shape
`{error, message, requestId}` and responses include the request ID header.

The Compose demo maps `owner-demo` to `local-owner-token` and `admin` to
`local-admin-token-change-me`. These are disposable fixtures and must not be
used outside local development.

## Local UI

`GET /` serves a create-only HTML form. `POST /ui/links` accepts a destination,
optional code, and local owner token. It does not list existing links or expose
administrative data. The JSON API is the canonical integration surface.

## Evidence boundary

The application and lifecycle tests are locally verified (`15 passed, 2
skipped`); specification checks are locally verified (`4 passed, 2 skipped`).
Terraform formatting, structural, and provider validation are locally verified.
No AWS resource, public endpoint, or cloud identity has been exercised.
