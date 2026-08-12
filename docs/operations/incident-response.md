# Runbook: local incident response

Use this for the disposable Compose environment. For AWS, stop and obtain the
required approval before touching resources, logs, credentials, or workflows.

1. Record UTC time, local commit, request/correlation ID, symptom, and route.
2. Classify the event: availability, unauthorized management, open redirect,
   SSRF validation, data exposure, database failure, or supply chain.
3. Stop the app or isolate the affected fixture/link if continued traffic could
   cause harm: `docker compose stop app`.
4. Preserve only redacted logs and container status outside Git:
   `docker compose logs --no-color app db > /exact/path/incident.log`.
5. Never copy authorization headers, tokens, full destination URLs, or data
   exports into the incident record.
6. Reproduce with a deterministic fixture and record the failing test/check.
7. Apply the smallest local correction, rerun the relevant checks, and record
   root cause, mitigation, residual risk, and a regression test.
8. Resume only after health/readiness, security, and lifecycle checks are
   green; use rollback or reset when data integrity is uncertain.
