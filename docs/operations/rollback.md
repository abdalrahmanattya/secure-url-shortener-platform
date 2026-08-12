# Runbook: local rollback

1. Identify the last known-good local commit, lockfile, migration head, and
   image digest from the retained test record. Never use a mutable `latest` tag.
2. Stop the app and preserve redacted evidence:
   `docker compose stop app`.
3. Check out or rebuild the reviewed local version, then start the database and
   app with `docker compose up --build -d`.
4. Run `/healthz`, `/readyz`, specification checks, API checks, and the
   validation suite. Confirm the Compose `migrate` service completes before
   accepting application traffic.
5. If schema compatibility is uncertain, restore a verified disposable backup
   before starting application writes.
6. If recovery fails, keep the app stopped and escalate rather than guessing at
   data repair.

Cloud deployment rollback, ECS circuit-breaker behavior, and destroy are
separate approved operations and are not authorized by this local runbook.
