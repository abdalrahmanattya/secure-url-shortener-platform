# ADR 001: Build an Original Service with Explicit AWS Boundaries

- Status: Accepted for scaffold phase
- Date: 2026-08-12

## Context

The historical YOURLS repositories show useful hosting and infrastructure
lessons but include third-party application material and credential risks. A
portfolio successor should demonstrate the same class of platform problem
without presenting reused software as original work.

## Decision

Implement an original, intentionally small URL-shortening service. Support a
credential-free Docker Compose mode first, then document an AWS target based
on private ECS Fargate, HTTPS ALB/WAF, Aurora Serverless v2, Secrets Manager,
ECR, CloudWatch, and GitHub Actions OIDC. Keep public ingress, application,
data, deployment, and recovery boundaries explicit.

## Consequences

- The service can be demonstrated locally before cloud spend or credentials.
- The architecture has clear security and operational evidence targets.
- Aurora capacity, WAF policy, identity boundaries, and destroy safety need
  measured decisions during implementation.
