# AWS target topology

Status: Terraform formatting/structural/provider validation and multi-platform
image compatibility were verified in hosted run `31580237125`; cloud behavior
is not verified or deployed.

```mermaid
flowchart TB
    U[Internet client] --> R53[Route 53 optional DNS]
    R53 --> ALB[Public HTTPS ALB]
    ACM[ACM certificate] -. attached certificate .-> ALB
    WAF[AWS WAF managed rules and rate control] -. associated .-> ALB
    ALB --> ECS[Private ECS Fargate service]
    ECS --> DB[(Aurora PostgreSQL Serverless v2\nprivate isolated subnets)]
    SM[Secrets Manager\nDATABASE_URL / OWNER_TOKENS / ADMIN_TOKENS] -. task injection .-> ECS
    ECS --> CW[CloudWatch logs metrics alarms]
    ECR[ECR immutable image] -. task image source .-> ECS
    OIDC[GitHub OIDC\nprotected environment] -. future contract only .-> DEPLOY[Scoped deployment role]
    DEPLOY -. future promotion .-> ECR
    DEPLOY -. future ECS update .-> ECS
    TF[Reviewed Terraform plan] --> NET[Two-AZ VPC, endpoints, and security groups]
```

The non-applied Terraform target makes the ALB the only public application
entry point, keeps ECS and Aurora private, and protects database/KMS deletion
behind explicit lifecycle controls. Route 53 records are intentionally outside
this Terraform root. A deployment also requires an ACM certificate, the three
Secrets Manager task keys shown above, `/healthz` target checks, and an
environment-only OIDC trust. Those target contracts are statically checked but
not cloud verified; the hosted CI image and Linux validation evidence is already
retained in run `31580237125`.
