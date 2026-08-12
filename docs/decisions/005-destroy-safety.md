# ADR 005: Make data-plane destruction an explicit demo decision

- Status: Accepted for the non-applied target
- Date: 2026-08-12

## Decision

Aurora and the KMS key use Terraform destroy guards. Aurora deletion protection
and seven-day backups are enabled by default. A non-production demo may set
`allow_demo_destroy = true` together with the explicit deletion controls, but
the KMS key remains protected by a lifecycle guard and must be handled as a
separate reviewed operation.

The target does not include a destroy workflow. Any future destroy must verify
the AWS account, region, state lock, resource list, backup requirement, and cost
impact before approval.
