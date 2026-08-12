# AWS target topology

Status: Terraform formatting/structural checks locally verified; provider
validation and cloud behavior are not yet verified or deployed.

```mermaid
flowchart TB
    U[Internet client] --> R53[Route 53 optional]
    R53 --> ACM[ACM certificate]
    ACM --> WAF[AWS WAF managed rules and rate control]
    WAF --> ALB[Public HTTPS ALB]
    ALB --> ECS[Private ECS Fargate service]
    ECS --> DB[(Aurora PostgreSQL Serverless v2\nprivate isolated subnets)]
    ECS --> SM[Secrets Manager]
    ECS --> CW[CloudWatch logs metrics alarms]
    ECR[ECR immutable image] --> ECS
    OIDC[GitHub OIDC\nprotected environment] --> DEPLOY[Scoped deployment role]
    DEPLOY --> ECR
    DEPLOY --> ECS
    DEPLOY --> TF[Reviewed Terraform plan]
    TF --> NET[Two-AZ VPC and security groups]
```

The non-applied Terraform target makes the ALB the only public application
entry point, keeps ECS and Aurora private, and protects database/KMS deletion
behind explicit lifecycle controls. A deployment also requires an ACM
certificate, application-compatible Secrets Manager environment wiring,
`/healthz` target checks, and an environment-only OIDC trust. Those target
contracts are statically checked but not cloud verified. The image pin must
also be compatible with the CI build platform.
