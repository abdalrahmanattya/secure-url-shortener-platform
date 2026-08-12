# Delivery and identity boundaries

Status: design evidence only; no cloud deployment has been performed.

```mermaid
sequenceDiagram
    participant Dev as Engineer
    participant GH as GitHub Actions
    participant OIDC as GitHub OIDC
    participant STS as AWS STS
    participant ECR as ECR
    participant ECS as ECS service
    participant CW as CloudWatch

    Dev->>GH: Pull request and reviewed change
    GH->>GH: Test, lint, scan, build digest
    GH->>OIDC: Request short-lived identity
    OIDC-->>STS: Repository/ref/environment claims
    STS-->>GH: Scoped deployment credentials
    GH->>ECR: Push immutable image digest
    GH->>ECS: Reviewed promotion to digest
    ECS->>CW: Structured logs and metrics
    ECS-->>GH: Deployment health and rollback signal
```

The application task role, ECS execution role, deployment role, and read-only
review role are separate target identities. The service does not issue bearer
tokens; it validates identity supplied by an external or local fixture issuer.
