# Runbook: local start

Status: command path documented; runtime evidence must be recorded per the
evidence matrix.

## Start

```sh
docker compose up --build -d
docker compose ps
curl --fail http://localhost:8000/healthz
curl --fail http://localhost:8000/readyz
```

Compose runs `migrate` with `alembic upgrade head` before starting `app`. If
readiness fails, inspect `docker compose logs migrate`, `docker compose logs
app`, and `docker compose logs db` before restarting. The expected local
responses are:

```json
{"status":"ok"}
{"status":"ready","dependencies":{"database":"ok"}}
```

## Exercise the current local path

```sh
curl --fail -X POST http://localhost:8000/v1/links \
  -H 'authorization: Bearer local-owner-token' \
  -H 'content-type: application/json' \
  -d '{"destination":"https://example.com/architecture","code":"arch-1"}'
curl --include --max-redirs 0 http://localhost:8000/r/arch-1
```

The local admin operations use the Compose-only bearer fixture shown in the
README. Do not use it in a shared or cloud environment.

## Stop

```sh
docker compose down
```

This keeps the named local database volume. Use `reset.md` only when deleting
disposable data is intentional.
