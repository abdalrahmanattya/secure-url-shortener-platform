# Runbook: local PostgreSQL backup and restore

Status: command path documented; execute only against the disposable Compose
database and record a redacted checksum outside Git.

## Backup

```sh
backup="$(mktemp -t secure-shortener-backup).sql"
docker compose exec -T db pg_dump -U shortener -d shortener --no-owner --no-privileges > "$backup"
shasum -a 256 "$backup"
```

Keep the path outside the repository. Inspect the export metadata without
printing destination values, tokens, or credentials. Remove it after the
exercise with an explicit, exact path.

## Restore

1. Stop application writes with `docker compose stop app`.
2. Confirm the target is the disposable Compose database.
3. Reset the local database volume using [`reset.md`](reset.md), then start only
   the database: `docker compose up -d db`.
4. Restore the reviewed file:

```sh
docker compose exec -T db psql -U shortener -d shortener < /exact/path/backup.sql
```

5. Start the app, run health/readiness and API checks, and confirm a known demo
   link behaves as expected.
6. Remove the temporary backup when the recovery record is complete.

Cloud snapshots, retention, RPO, and RTO remain planned target evidence and
require separate approval.
