# Development and verification workflow

## Local setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
docker compose up --build -d
```

The application listens on `http://localhost:8000`; the database is reachable
inside Compose as `db:5432`. Compose runs the separate `migrate` service with
`alembic upgrade head` and starts `app` only after it completes successfully.

## Checks

```sh
./.venv/bin/pytest -q
./.venv/bin/python tests/infrastructure/test_static.py
./.venv/bin/pytest tests/specification -q
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra init -backend=false
terraform -chdir=infra validate
```

The current local evidence is `15 passed, 2 skipped` for the application suite
and `4 passed, 2 skipped` for the specification suite. Infrastructure formatting
and structural checks passed, including provider-backed Terraform validation.
Hosted CI remains useful for independent reproduction. Specification checks are credential-free and may run without
Docker. These results do not constitute cloud verification.

## Local evidence discipline

- `locally verified`: the command ran successfully against the local code.
- `statically validated`: a file/structure check passed without runtime
  execution; it does not imply provider execution or cloud behavior.
- `not deployed`: no AWS resource or public endpoint was exercised.
- `cloud verified`: reserved for an approved, measured AWS run with account,
  region, cost, and rollback evidence.

Do not commit `.env`, database files, Terraform state/plans, cloud metadata,
credentials, or generated exports.

## Delivery direction

The future delivery path is GitHub Actions quality/security checks, immutable
ECR image publication, constrained OIDC, protected environment approval,
reviewed Terraform plans, smoke tests, and a reversible promotion. Any AWS
change requires explicit approval, bounded cost, and a tested rollback/destroy
path.
