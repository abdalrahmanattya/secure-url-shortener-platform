# Requirements

## Product intent

Demonstrate an end-to-end secure service path from local development to a
carefully bounded AWS target. The product is intentionally small so that
security, reliability, delivery, and operating evidence remain visible.

## Functional requirements

- Create a short URL for a validated destination.
- Resolve a short URL with predictable redirect behaviour.
- Provide ownership or administrative boundaries without pretending to be a
  full identity product.
- Expose health and readiness endpoints.
- Record redirect metadata only to the minimum extent needed for the demo.
- Support deterministic local fixtures and a documented reset path.

## Platform requirements

- Docker Compose must run the complete local service without cloud credentials.
- The AWS target uses private ECS Fargate tasks behind an HTTPS ALB.
- Use Aurora Serverless v2 for managed relational persistence, with explicit
  capacity and cost limits.
- Store secrets in Secrets Manager and images in ECR.
- Protect the edge with WAF; use ACM and Route 53 only for an approved,
  bounded cloud demonstration.
- Emit structured logs, metrics, alarms, and dashboards through CloudWatch.
- Use GitHub Actions OIDC, environment approval, immutable image versions,
  and a tested destroy path.

## Quality requirements

- Unit, API contract, integration, container, infrastructure, and security
  checks are automated where practical.
- No secrets, state files, database dumps, or cloud metadata are committed.
- The service runs as non-root and receives only the permissions it needs.
- Tests and documentation distinguish local evidence from cloud evidence.

## Non-goals

- Reusing or repackaging YOURLS or the historical project code.
- Building a public multi-tenant SaaS product.
- Claiming live AWS availability, performance, or cost before measurement.
- Supporting arbitrary analytics, billing, or enterprise identity features.

## Acceptance evidence

A reviewer should be able to run the local stack, inspect the threat model,
follow the delivery path, understand the AWS boundaries, and see exactly which
claims remain planned.
