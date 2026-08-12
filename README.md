# Secure URL Shortener Platform

An original, local-first URL-shortening service with a deliberately visible
path from application code to secure AWS delivery.

**Status:** v0.1.0 candidate — local application implementation and Terraform
validation verified. **Deployment:** not deployed. **Data:** no production data.
**Credentials:** no cloud credentials required for local work.

This is a portfolio engineering case study for cloud architects, platform
engineers, and security reviewers. It demonstrates how a small product can
make security boundaries, operational decisions, and evidence quality visible.

## Why this project exists

A URL shortener looks simple until its boundaries are made explicit. It needs
to validate destinations without becoming an SSRF helper, protect management
operations, preserve link lifecycle state, survive database and deployment
failures, and expose enough telemetry to operate safely.

The implementation starts locally with FastAPI, SQLAlchemy, Alembic, and
PostgreSQL. The target AWS design places an HTTPS ALB and WAF in front of
private ECS Fargate tasks, with Aurora PostgreSQL Serverless v2, Secrets
Manager, ECR, and CloudWatch behind clear IAM and network boundaries.

## What is implemented locally

- FastAPI service with a small HTML interface.
- PostgreSQL 16 through Docker Compose.
- Alembic migration for the initial links table.
- HTTP/HTTPS destination validation with local/private address rejection.
- Authenticated owner/admin management using clearly local-only bearer
  fixtures in Compose.
- Versioned `/v1` management routes, owner scoping, error envelopes, request
  IDs, tombstone deletion, and `410` lifecycle responses.
- Public `302` resolution with `Cache-Control: no-store` and a local in-memory
  rate limit.
- Redirect click count and last-accessed metadata.
- Non-root application container with a defined container health-check intent.
- Disposable reset tooling for development; the seed helper remains a follow-up
  item until its current service-call signature is corrected.
- Contract, API, validation, and infrastructure-structure checks.

The current executable route surface is documented in
[`docs/portfolio/api-surface.md`](docs/portfolio/api-surface.md) and described
by the OpenAPI contract in [`docs/api/openapi.yaml`](docs/api/openapi.yaml).
The application is locally verified; the AWS design remains non-applied and
not deployed.

## Run it locally

Prerequisites: Docker Desktop and Python 3.13 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
docker compose up --build -d
curl --fail http://localhost:8000/healthz
curl --fail http://localhost:8000/readyz
```

The Compose database uses disposable local values only. Do not copy them into
an AWS environment or commit a `.env` file. Compose runs the separate
`migrate` service (`alembic upgrade head`) and starts `app` only after the
migration completes. To inspect startup:

```sh
docker compose logs -f app
```

To stop without deleting the local database volume:

```sh
docker compose down
```

For a destructive disposable reset, follow
[`docs/operations/reset.md`](docs/operations/reset.md).

## Current local API

The following examples describe the code that is currently runnable locally.
Compose maps `owner-demo` to `local-owner-token` and `admin` to
`local-admin-token-change-me`; these fixtures are intentionally unsuitable for
any shared or cloud environment.

Create a link:

```sh
export OWNER_TOKEN=local-owner-token
curl --fail -X POST http://localhost:8000/v1/links \
  -H "authorization: Bearer ${OWNER_TOKEN}" \
  -H 'content-type: application/json' \
  -d '{"destination":"https://example.com/docs","code":"docs-1"}'
```

Resolve it without following the redirect:

```sh
curl --include --max-redirs 0 http://localhost:8000/r/docs-1
```

Read link metadata as its owner:

```sh
curl --fail http://localhost:8000/v1/links/docs-1 \
  -H "authorization: Bearer ${OWNER_TOKEN}"
```

Disable or delete a link as its owner:

```sh
curl --fail -X PATCH http://localhost:8000/v1/links/docs-1 \
  -H "authorization: Bearer ${OWNER_TOKEN}" \
  -H 'content-type: application/json' \
  -d '{"enabled":false}'
curl --fail -X DELETE http://localhost:8000/v1/links/docs-1 \
  -H "authorization: Bearer ${OWNER_TOKEN}"
```

An active link resolves with `302` and `Cache-Control: no-store`. Unknown codes
return `404`; disabled, expired, and tombstoned codes return `410`. Management
requires an owner or administrator bearer identity, and deleting a link keeps a
tombstone so its code cannot be reused. Management and resolver rate limits
return `429` with `Retry-After` when exceeded.

## Engineering story

```text
validated destination
        │
        ▼
FastAPI service ── SQLAlchemy/Alembic ── PostgreSQL
        │
        ├── health/readiness + structured request log
        ├── local contract/API/security checks
        └── immutable image → reviewed AWS target (not deployed)
```

Detailed diagrams are in [`docs/diagrams/`](docs/diagrams/) and the decisions
behind the target are recorded in [`docs/decisions/`](docs/decisions/).

## Security and operations

- [Security boundaries](docs/security.md)
- [Misuse and abuse threat model](docs/threat-model.md)
- [Local start](docs/operations/local-start.md)
- [Backup and restore](docs/operations/backup-restore.md)
- [Incident response](docs/operations/incident-response.md)
- [Rollback](docs/operations/rollback.md)
- [Evidence matrix](docs/evidence/evidence-matrix.md)

No statement in this repository should be read as an uptime, cost, account,
performance, or production claim unless the evidence matrix labels it `cloud
verified` and links to a retained measurement.

## Publication-readiness snapshot

| Check | Current evidence |
|---|---|
| Specification documentation checks | Locally verified: 4 passed; 2 optional service checks skipped |
| Infrastructure structural checks | Locally verified: passed |
| Full application/API suite | Locally verified: 15 passed; 2 skipped |
| Terraform formatting and structural checks | Locally verified |
| Terraform provider validation | Locally verified |
| Workflow syntax and action pins | Locally verified |
| Docker build, runtime smoke, and vulnerability scan | Locally verified; Trivy reports 0 HIGH/CRITICAL |
| SBOM publication | GitHub-hosted CI evidence remains pending |
| AWS secret/environment wiring, HTTPS, health checks, and environment-only OIDC | Statically validated target design; not deployed |
| Explicit Bearer scheme enforcement | Locally verified; non-Bearer schemes are rejected before token comparison |
| AWS deployment | Not deployed |

The local API is suitable for review, but the repository is not yet ready for
cloud publication. The ECS environment/secret contract, HTTPS-only listener,
`/healthz` checks, and environment-only OIDC trust are now represented in the
Terraform target and covered by structural checks; they still require Linux
provider validation and cloud verification. The remaining repository gates are
GitHub-hosted CI/SBOM evidence and cloud verification remain separate gates. The
local UI has same-origin Origin validation plus distinct creation and failed-auth
rate limits; these controls still need deployment-level abuse measurements.

See [`CHANGELOG.md`](CHANGELOG.md) for the candidate release boundary and
[`docs/evidence/evidence-matrix.md`](docs/evidence/evidence-matrix.md) for the
full distinction between locally verified, statically validated, and not
deployed evidence.

## Project map

```text
src/secure_shortener/     FastAPI application, validation, persistence
migrations/               Alembic schema history
templates/ static/        Local demonstration UI
tests/                    API, validation, specification, infrastructure checks
infra/                    Non-applied Terraform AWS target
docs/api/                 OpenAPI API contract
docs/diagrams/            Local, AWS, delivery, and identity diagrams
docs/operations/           Recovery and operating runbooks
```

## Safety boundary

AWS changes, credentials, state backends, image publication, deployment,
rollback, and destroy operations require separate approval. No historical
application code, credentials, generated state, or deployment workflow is
used by this project.

## License

Released under the [MIT License](LICENSE).
