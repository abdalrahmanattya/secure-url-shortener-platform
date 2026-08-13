# Delivery and identity boundaries

Status: hosted CI is verified by run `31584503885`; AWS deployment remains
unimplemented and has not been performed.

```mermaid
flowchart LR
    Dev[Developer push or pull request] --> GH[GitHub Actions CI]
    GH --> Checks[Tests, PostgreSQL integration, policy scans]
    GH --> Image[Container smoke, Trivy scan, SBOM upload]
    Checks --> Evidence[Retained CI evidence]
    Image --> Evidence
    Contract[Manual future release contract] -. validates only .-> Environment[Protected environment]
    Environment -. future OIDC assumption, not implemented .-> AWS[AWS ECR/ECS promotion]
```

The current CI workflow does not request AWS OIDC credentials, push to ECR, or
update ECS. The dispatchable release workflow is contract-only: it validates an
immutable image digest and protected environment variables. The target design
separates application task, ECS execution, and future deployment identities; the
service does not issue bearer tokens and validates identity supplied by an
external or local fixture issuer.
