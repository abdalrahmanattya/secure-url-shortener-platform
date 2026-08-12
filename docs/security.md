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
certification. The local UI is create-only and requires an owner token, but its
form endpoint has no dedicated CSRF or rate-limit control and must remain
local-only until addressed. Cloud WAF, identity, secret wiring, and
operational controls remain target design rather than deployed evidence.

The bearer contract also requires explicit scheme enforcement; this is a
remaining application hardening gate before publication.

## Target controls

- Public traffic must terminate at an HTTPS ALB/WAF; without an approved ACM
  certificate the target intentionally returns `503` rather than serving HTTP
  application traffic. ECS and Aurora remain private.
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

The target ECS task provides the application’s `DATABASE_URL`, `ENVIRONMENT`,
`OWNER_TOKENS`, and `ADMIN_TOKENS` contract from Secrets Manager in Terraform.
This is static target evidence, not cloud-verified runtime behavior.

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
