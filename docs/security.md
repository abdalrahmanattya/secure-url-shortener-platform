# Security boundaries

## Implemented locally

- Destination validation accepts only HTTP(S) URLs and rejects credentials in
  the destination plus local/private/link-local/reserved addresses resolved at
  creation time.
- Management endpoints use constant-time bearer comparison and owner/admin
  authorization for the local fixture identities.
- Link deletion is a tombstone; disabled, expired, and deleted links resolve
  as `410`, while unknown codes remain `404`.
- Public resolution returns `302` with `Cache-Control: no-store`; local
  resolver and management creation paths have bounded in-memory rate limits.
- Error responses use a bounded JSON envelope with a request ID, while logs
  omit authorization headers, tokens, full destinations, and database values.
- The container runs as a non-root user.
- Database credentials are Compose-only demo values and are not a cloud secret.
- Request logs use JSON-safe serialization and do not intentionally log bearer
  headers or database values.

These are local implementation observations, not a production security
certification. The local UI is create-only, requires an owner token, validates a
same-origin `Origin` when supplied, and has separate creation and failed-auth
rate-limit buckets. It remains a local demonstration surface; deployment-level
CSRF, abuse measurement, and distributed rate limiting are not claimed. The
Bearer scheme is explicitly enforced before token comparison. Cloud WAF,
identity, secret wiring, and operational controls remain target design rather
than deployed evidence.

## Target controls

- Public traffic must terminate at an HTTPS ALB/WAF; without an approved ACM
  certificate the Terraform apply cannot complete. HTTP redirects to HTTPS and
  ECS/Aurora remain private.
- WAF rate controls and application limits protect creation, resolution, and
  management paths.
- Secrets Manager owns runtime secrets; ECR publishes scanned immutable digests.
- Separate ECS task, execution, deployment, and read-only review roles enforce
  least privilege.
- GitHub OIDC is constrained in the target Terraform to the exact repository,
  audience, and protected environment subject; this is structural evidence,
  not a cloud trust-policy verification. No long-lived AWS access keys are
  used.
- Aurora and KMS are encrypted, backed up, and protected by explicit deletion
  controls.
- Logs redact tokens, authorization headers, full destinations, and database
  values; request IDs remain available for diagnosis.

The target ECS task receives `DATABASE_URL`, `OWNER_TOKENS`, and `ADMIN_TOKENS`
from Secrets Manager in Terraform; `ENVIRONMENT` is a normal task environment
value. This is static target evidence, not cloud-verified runtime behavior.

## Abuse cases

The detailed threat model is [`docs/threat-model.md`](threat-model.md). The
important boundary is that a shortener must not become an SSRF helper or a
silent public admin console:

- Do not fetch destination URLs during validation or resolution.
- Reject non-global resolved addresses and DNS-resolution failures.
- Do not expose full destination lists to unauthenticated clients.
- Enforce owner/admin authorization before create, read, update, disable, or
  delete operations.
- Preserve deleted codes as tombstones and return the documented inactive state.

## Security evidence boundary

Static Terraform checks and local unit/contract checks are evidence of code and
configuration properties only. They do not prove AWS IAM behavior, WAF
effectiveness, database recovery, or production resilience. Those require an
approved cloud demonstration and retained measurements.
