# Product requirements

## Product intent

Build a small URL-shortening service that makes cloud-platform engineering
judgment visible: safe destination handling, explicit link lifecycle, bounded
management access, disposable local operations, and a reviewable AWS target.

The product is a portfolio case study, not a claim of a running SaaS platform.

## User outcomes

- A local user can create a short link for a validated HTTP(S) destination.
- A public resolver can redirect without exposing management data.
- An authorized owner or administrator can inspect and change link state.
- Expiry, disable, and deletion have predictable, testable semantics.
- Operators can start, reset, back up, restore, diagnose, and roll back a
  disposable local environment without cloud credentials.

## Platform outcomes

- Docker Compose runs the application and PostgreSQL locally.
- Alembic owns schema history; tests prove the migrated schema works.
- The AWS target uses a public HTTPS ALB/WAF, private ECS Fargate tasks, and
  isolated Aurora PostgreSQL Serverless v2.
- Secrets are generated/stored through Secrets Manager; images are immutable
  ECR digests; logs, metrics, alarms, and dashboards use CloudWatch.
- Delivery uses GitHub Actions OIDC, protected environments, reviewed plans,
  and a tested rollback/destroy boundary.

## Security requirements

- Only HTTP(S) destinations with publicly routable resolved addresses are
  accepted; validation must reject local, private, link-local, reserved,
  unspecified, and metadata-service targets.
- Public resolution must not fetch or follow the destination server-side.
- Creation and management require owner/admin authorization in the hardened
  contract; public HTML must not expose an administrative link listing.
- Delete is a tombstone operation and codes are never reused.
- Logs omit authorization headers, tokens, full destinations, and database
  values.
- Rate limits and abuse controls produce a documented `429` response.
- The local API rate limits creation and resolution; the HTML form uses
  same-origin Origin validation plus separate creation and failed-auth rate
  limits. Distributed and edge rate limiting remain cloud concerns.

## Evidence requirements

Every claim is labelled `locally verified`, `statically validated`, or `not
deployed/cloud verified`. No endpoint, cost, availability, performance, or
production statement is promoted without a retained measurement.

The AWS target additionally requires a supplied ACM certificate, `/healthz`
health checks, explicit application environment/secret wiring, an
environment-only OIDC trust, and a CI-compatible multi-platform image before
any deployment approval.

## Current implementation

The local service implements the versioned `/v1` management contract. Owners
and administrators authenticate with bearer identities; owners are scoped to
their links. `POST` returns `201` and a `Location` header, reads and updates
return `200`, deletion returns `204` and creates a tombstone, and unknown,
disabled, expired, or deleted links return the documented `404`/`410` states.
Public resolution returns `302` with `Cache-Control: no-store`; abuse limits
return `429` with `Retry-After`. See
[`docs/portfolio/api-surface.md`](portfolio/api-surface.md) and
[`docs/evidence/evidence-matrix.md`](evidence/evidence-matrix.md) for the
evidence boundary.

## Non-goals

- Multi-tenant SaaS scale, billing, analytics, or enterprise identity.
- Content moderation or malware classification.
- Reusing third-party application code or historical credentials.
- A live AWS endpoint before approval, cost limits, and cloud evidence exist.
