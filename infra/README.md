# AWS infrastructure target

This directory defines a non-applied, production-shaped AWS target for the
secure URL shortener. It does not create resources, publish an image, or need
AWS credentials for formatting, static checks, or `terraform validate` with
the backend disabled.

## Image contract

Set `container_image_digest` to a complete `repository@sha256:<64 hex>` ECR
reference. Mutable tags, including `latest`, are rejected. The empty default
exists only to make the scaffold inspectable before an image release exists;
production validation fails unless a digest is supplied.

## Certificate contract

Set `certificate_arn` to an ACM certificate in the same region. HTTP always
redirects to HTTPS and the HTTPS listener uses the TLS 1.3 security policy.
The syntactically valid default ARN exists only for credential-free Terraform
validation; replace it with a real ACM certificate before any apply. Route 53
and domain records are intentionally outside this root.

## Validation without AWS

```sh
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra init -backend=false
terraform -chdir=infra validate
python3 tests/infrastructure/test_static.py
scripts/infrastructure/validate.sh
```

`terraform plan` and every apply/destroy command require a separately approved
AWS target, credentials, cost limit, reviewed state backend, and destroy plan.
The current Terraform configuration keeps Aurora and its KMS key under static
destroy guards; `allow_demo_destroy` controls the provider's demo-safe delete
settings but cannot bypass those lifecycle guards.
The S3 and DynamoDB backend is deliberately bootstrap-isolated; copy
`backend.hcl.example`, fill approved values outside Git, and initialize only
after those controls exist. The approved state bucket must have versioning,
server-side encryption, restricted access, and recovery controls; the lock
table must use point-in-time recovery and least-privilege access. Never put
credentials, account-specific state names, or state files in this repository.

## Egress model

The ALB can reach ECS only on TCP 8000. ECS can reach Aurora only on TCP 5432,
the VPC resolver on TCP/UDP 53, the AWS-managed S3 prefix list through the S3
gateway endpoint, and HTTPS on the private interface endpoints for ECR, Cloud
Watch Logs, Secrets Manager, KMS, and STS. Aurora has no egress rule. The
application does not fetch arbitrary destination URLs, so unrestricted internet
egress is not part of this target.
