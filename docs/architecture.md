# Architecture and trade-offs

## Current local implementation

The runnable path is deliberately small:

```text
Browser/curl :8000
        │
        ▼
FastAPI application ── SQLAlchemy async ── PostgreSQL 16
        │                         ▲
        ├── templates/static UI   │
        └── request log/metrics   └── separate Compose migrate service
```

See [`docs/diagrams/local-topology.md`](diagrams/local-topology.md). Compose
uses a named disposable database volume, a separate `migrate` service that
runs `alembic upgrade head`, and local-only fixture tokens. The app starts
after the migration service completes successfully.

## AWS target

```text
Route 53 (optional approved demo)
        │
ACM certificate → WAF/rate control → public HTTPS ALB
                                      │
                              private ECS Fargate
                                      │
                              isolated Aurora PostgreSQL
```

ECR supplies an immutable image digest. Secrets Manager supplies runtime
secrets. CloudWatch receives structured logs, metrics, alarms, and dashboards.
GitHub Actions receives short-lived AWS credentials through constrained OIDC.
The target is described in [`docs/diagrams/aws-target.md`](diagrams/aws-target.md)
and represented by non-applied Terraform under `infra/`.

The target statically maps Secrets Manager values into the application’s
`DATABASE_URL`, `ENVIRONMENT`, `OWNER_TOKENS`, and `ADMIN_TOKENS` settings; ALB
and ECS health checks use `/healthz`; and the OIDC trust is environment-only.
These are structural target checks, not cloud runtime evidence. The application
and Compose images use verified multi-platform pinned base images; hosted CI
execution and cloud behavior remain unverified.

## Decisions and trade-offs

| Decision | Benefit | Cost or limitation |
|---|---|---|
| PostgreSQL/Aurora instead of a key-value store | Relational lifecycle, ownership, and audit semantics | More operational surface than a single-table key-value design |
| Two AZ network tiers | Makes ALB/ECS/Aurora boundaries and failure domains visible | Adds subnet and NAT cost |
| One optional NAT gateway for demo target | Controls non-production cost | Less resilient than one NAT gateway per AZ; endpoints are the production alternative |
| WAF at the edge | Rate controls and managed web protections before ECS | Requires measured rules and false-positive review |
| `302` resolver target | Avoids preserving unsafe methods and supports no-store semantics | Clients do not cache it as aggressively as a permanent redirect |
| Tombstones | Prevents code resurrection and preserves lifecycle evidence | Requires retention/purge policy |
| OIDC deployment identity | Removes long-lived AWS keys from CI | Trust policy and environment protection must be tested together |
| Explicit destroy guards | Prevents accidental data/KMS deletion | Demo cleanup needs a separate reviewed operation |

## Delivery flow

```text
change → tests/lint/scan → immutable image digest → reviewed plan
       → protected promotion → smoke/rollback evidence
```

No cloud resource is created by the current repository state. Terraform
formatting, structural checks, and provider validation are locally verified;
Linux CI remains pending as independent hosted evidence, and cloud behavior is
not verified. See the ADRs for
network/NAT, Aurora, OIDC, destroy safety, and observability decisions.
