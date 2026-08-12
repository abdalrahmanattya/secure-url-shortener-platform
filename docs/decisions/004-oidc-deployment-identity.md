# ADR 004: Use repository- and environment-constrained GitHub OIDC

- Status: Accepted for the non-applied target
- Date: 2026-08-12

## Decision

The deployment role trusts the existing GitHub Actions OIDC provider only when
the token audience is `sts.amazonaws.com` and the subject matches the exact
repository/environment input. Branch or tag claims are not an alternate trust
path; the protected GitHub environment is the deployment boundary. The role policy separates
artifact reads, ECS deployment operations, and `iam:PassRole` limited to the
two ECS roles. The application task role has no permissions by default;
runtime secret injection belongs to the execution role.

The protected environment must enforce approved branches, reviewers, and
deployment policy in GitHub; those controls are not replaced by a branch claim
in the IAM trust policy.
