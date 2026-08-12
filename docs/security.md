# Security Boundaries

- Keep ECS tasks and Aurora in private subnets; expose only the intended ALB
  path.
- Enforce HTTPS with ACM and redirect or reject plaintext traffic.
- Use WAF rules and rate controls appropriate to a public redirect service.
- Use separate task, execution, deployment, and read-only review roles.
- Store database and application secrets in Secrets Manager; do not pass
  historical credentials or literal values through workflows.
- Use ECR scanning, dependency checks, container hardening, and infrastructure
  policy checks before a deployment is eligible.
- Use GitHub Actions OIDC with short-lived, least-privilege AWS roles; never
  use long-lived access keys in repository secrets.
- Enable database encryption, backups, deletion protection during cloud work,
  and an explicitly reviewed destroy procedure for non-production resources.
- Redact URLs, headers, tokens, and database values from logs and test output.

The historical `yourls-cf` and `test-yourls` repositories are treated as
unsafe source material. Their credentials, state, workflows, and generated
artifacts are not imported.
