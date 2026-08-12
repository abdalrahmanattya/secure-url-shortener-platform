# Development Workflow

## Local-first workflow

Start with Docker Compose, seed only deterministic demo data, and run the
service, database, health checks, and tests without AWS credentials. Keep
local state disposable and document the reset command before adding features.

## Planned checks

- Format, lint, type-check, and unit-test application code.
- Run API contract and database integration tests.
- Build and run the container as non-root.
- Scan dependencies and images for vulnerabilities.
- Validate infrastructure and policy without applying it.
- Exercise migration, backup/restore assumptions, smoke tests, and destroy
  path in isolated environments.

## Delivery direction

The eventual workflow will use GitHub Actions OIDC, immutable ECR image
references, protected environments, reviewable infrastructure plans, and a
post-deployment smoke test. It will not use long-lived access keys or mutable
deployment tags.

## Cloud work

Any AWS change requires explicit user approval, bounded cost, a reviewed plan,
and a tested rollback or destroy path. Until then, all cloud material is
design documentation only.
