# Runbook: local reset

This removes only disposable local Compose data. Confirm the target before
running it; never use these commands for an AWS database.

## Full disposable reset

```sh
docker compose down -v
docker compose up --build -d
curl --fail http://localhost:8000/readyz
```

The `migrate` service applies the Alembic head before `app` starts.

## Data-only reset while the database remains running

```sh
docker compose exec db psql -U shortener -d shortener \
  -c 'TRUNCATE TABLE links RESTART IDENTITY'
```

The application does not seed automatically. Use `scripts/seed.py` only from a
credential-free environment configured for the intended database; do not run
it against cloud resources.
