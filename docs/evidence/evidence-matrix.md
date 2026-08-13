# Evidence matrix

This matrix is the source of truth for what a recruiter may safely infer from
the repository. Statuses are deliberately conservative:

- **Locally verified** — executed successfully against local code.
- **Statically validated** — checked from source/configuration without runtime
  or cloud execution.
- **Not deployed** — no AWS/public endpoint evidence exists.
- **Cloud verified** — reserved for an approved measured AWS run.

| Claim | Evidence | Status | Boundary/next proof |
|---|---|---|---|
| FastAPI service and Compose topology exist | `src/`, `compose.yaml`, `Dockerfile`, Compose/PostgreSQL lifecycle evidence | Locally verified | Keep disposable local runtime evidence separate from cloud evidence |
| Specification document has required paths/statuses | `tests/specification/test_contract.py` | Locally verified: 4 passed; 2 optional checks skipped | Retain a future PostgreSQL/API run record |
| Destination URL validation exists | `src/secure_shortener/validation.py`, `tests/test_validation.py` | Locally verified in the existing validation suite | Add deterministic DNS failure/dual-stack/length cases |
| Local persistence schema exists | `migrations/versions/001_create_links.py` | Alembic migration against real PostgreSQL verified in hosted CI run `31584503885` | Retain future migration/recovery evidence |
| API lifecycle behavior | `tests/test_api.py`, `scripts/seed.py`, Compose PostgreSQL | Locally verified against Compose PostgreSQL (create/302/click/admin/seed lifecycle) and SQLite suite: 15 passed; 2 skipped | Hosted CI currently covers migration/readiness, not the full PostgreSQL API lifecycle |
| Owner/admin auth and error envelope | `src/secure_shortener/main.py`, `tests/test_api.py` | Locally verified | Add cloud identity and redaction evidence only in an approved deployment |
| Bearer scheme enforcement | `src/secure_shortener/main.py` | Locally verified | Exact case-insensitive `Bearer` scheme is required before token comparison |
| `302` resolution, `410` lifecycle, tombstones, and code non-reuse | `src/secure_shortener/main.py`, `src/secure_shortener/service.py`, `tests/test_api.py` | Locally verified | Exercise recovery and retention policy |
| Local rate limiting and `Retry-After` | `src/secure_shortener/main.py` | Locally verified | Add measured abuse-control evidence in the target environment |
| Local HTML form authentication | `templates/index.html`, `src/secure_shortener/main.py` | Locally verified by source/tests; local-only | Same-origin Origin validation and separate creation/failed-auth limits are implemented; deployment measurement remains |
| Infrastructure safety structure | `tests/infrastructure/test_static.py` | Locally verified: passed | Keep Terraform evidence with the reviewed change |
| Terraform formatting and provider validation | `infra/` | Locally verified | Approved plan and cloud smoke test remain separate |
| Workflow syntax and action pins | `scripts/ci/validate-workflows.sh`, `.github/workflows/`, hosted run `31584503885` | Hosted CI verified | Preserve the retained run as CI evidence |
| AWS ECS environment and Secrets Manager contract | `infra/ecs.tf`, `infra/secrets.tf`, `src/secure_shortener/config.py` | Statically validated target design; not deployed | Verify secret injection in an approved cloud run |
| ALB/ECS health-check route | `infra/alb.tf`, `infra/ecs.tf`, `/healthz` application route | Statically validated target design; not deployed | Verify target health in an approved cloud run |
| HTTPS-only listener and certificate contract | `infra/alb.tf`, `infra/variables.tf` | Statically validated target design; not deployed | Supply an approved ACM certificate and verify TLS |
| Environment-only OIDC trust | `infra/iam.tf`, `infra/variables.tf` | Statically validated target design; not deployed | Verify GitHub/AWS trust behavior without exposing credentials |
| Image architecture and CI build platform | `Dockerfile`, `.github/workflows/ci.yml`, hosted run `31584503885` | Hosted CI verified on Linux with pinned multi-platform base image | Cloud runtime architecture remains unverified |
| Compose database image provenance | `compose.yaml` | Locally verified with a multi-platform pinned digest | Keep Compose use within disposable development unless separately approved |
| Non-root container behavior | `Dockerfile`, hosted container smoke job in `31584503885` | Hosted CI verified | Recheck after any base-image or runtime change |
| Dependency reproducibility | `requirements.lock`, hosted Python/container jobs in `31584503885` | Hosted CI verified | Continue reviewing dependency updates |
| Structured request logging | `src/secure_shortener/main.py` | Statically validated | Verify redaction and exception-path logging |
| Process metrics | `/internal/metrics` implementation | Statically validated | Replace process-local counters with deployment-grade metrics |
| Local backup/restore | `docs/operations/backup-restore.md` | Planned runbook | Execute against disposable Compose PostgreSQL |
| Local incident/rollback procedure | `docs/operations/incident-response.md`, `rollback.md` | Statically validated documentation | Run a failure exercise and retain redacted evidence |
| AWS ALB/WAF/ECS/Aurora design | `infra/`, `docs/diagrams/aws-target.md` | Statically validated target design | Approved plan and cloud smoke test |
| AWS secrets and OIDC design | `infra/secrets.tf`, `infra/iam.tf`, ADRs | Statically validated target design; not deployed | Verify environment-only trust and secret injection in an approved cloud run |
| Availability, cost, performance, uptime | None | Not deployed | Measure only in an approved bounded environment |

## Current release interpretation

This is a credible engineering work-in-progress: the repository contains a
locally verified service, hosted Linux CI evidence, locally and provider
validated target structure, and explicit evidence gates. It is not a claim of
production readiness. The next proof is a separately approved bounded cloud
demonstration with retained deployment, health, rollback, and recovery evidence.
