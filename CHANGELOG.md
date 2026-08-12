# Changelog

## [0.1.0] — Unreleased candidate

This is a local candidate release, not a deployed release.

### Added

- FastAPI URL-shortening service with SQLAlchemy async persistence.
- PostgreSQL Compose topology with a separate successful `migrate` service and
  Alembic initial migration.
- Destination validation, `/healthz` and `/readyz`, owner/admin bearer
  authorization, a create-only local UI, and `/v1` lifecycle management.
- Public `302` resolution with `410` inactive/tombstone semantics, request IDs,
  JSON error envelopes, and local rate limiting.
- Non-root application image and deterministic local reset/seed tooling.
- Non-applied AWS Terraform target for ALB/WAF, private ECS, Aurora, ECR,
  Secrets Manager, CloudWatch, KMS, and GitHub OIDC boundaries.
- OpenAPI contract, threat model, evidence matrix,
  Mermaid architecture diagrams, and operational runbooks.
- Pinned dependency lock and credential-free specification/infrastructure
  checks.

### Evidence boundary

- Application and specification checks have local evidence: `15 passed, 2
  skipped` for the application suite and `4 passed, 2 skipped` for the
  specification suite.
- Infrastructure formatting, structural checks, and provider-backed Terraform
  validation passed locally.
- No AWS resources, public endpoint, production data, or cloud credentials are
  part of this candidate release.

### Next gate

Hosted GitHub Actions run `31580237125` verified the five CI jobs, including
PostgreSQL integration, Gitleaks, Terraform/Trivy checks, container scanning,
and SBOM upload. Exercise local recovery as useful operational evidence, then
complete the separately approved cloud proof before calling the service
production-ready.
