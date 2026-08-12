# Architecture Direction

## Local topology

```text
Browser / API client
  -> application container
  -> local relational database container
```

Docker Compose supplies repeatable startup, health checks, fixtures, logs,
and reset instructions. The local topology must remain useful without AWS
credentials.

## AWS target topology

```text
Route 53 (optional approved demo)
  -> ACM certificate
  -> internet-facing HTTPS ALB + AWS WAF
  -> private ECS Fargate service
  -> Aurora Serverless v2 in isolated data subnets
  -> Secrets Manager for runtime secrets

ECR -> immutable image
CloudWatch -> logs, metrics, alarms, dashboards
GitHub Actions OIDC -> reviewed deployment role
```

The final subnet, security-group, IAM, backup, and scaling design must be
validated before implementation. No database or cloud resource is created by
this scaffold.

## Delivery flow

```text
change -> tests and scans -> immutable image -> approved environment
       -> infrastructure/app promotion -> smoke test -> rollback or destroy
```

Image identity and infrastructure state must be reviewable without embedding
secrets or mutable `latest` references.
