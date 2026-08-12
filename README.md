# Secure URL Shortener Platform on AWS

An original URL-shortening service and delivery platform for demonstrating
secure application hosting, managed data, observability, and controlled AWS
operations.

## Status

This repository is a local planning and implementation scaffold. It has no
live deployment, public endpoint, production data, or claim of cloud
execution.

## Audience

Cloud architects, platform engineers, security reviewers, and hiring teams
looking for evidence of practical AWS delivery and operational discipline.

## Scope

- Build an original URL-shortening API and small web interface.
- Run the service locally with Docker Compose and deterministic data.
- Define an AWS target using private ECS Fargate tasks, an HTTPS ALB, Aurora
  Serverless v2, Secrets Manager, ECR, CloudWatch, and WAF.
- Use GitHub Actions with OIDC and immutable image references for delivery.
- Include application, infrastructure, security, observability, and destroy
  path tests.

## Target direction

Public traffic should terminate at an HTTPS ALB protected by WAF and route to
private ECS Fargate tasks. Aurora Serverless v2 is the planned persistence
layer; Secrets Manager owns runtime secrets, ECR owns images, and CloudWatch
owns logs, metrics, alarms, and dashboards. Route 53 and ACM are included only
when a bounded cloud demonstration is approved.

## Evidence boundaries

All diagrams and statements will identify whether they are planned, locally
verified, or cloud verified. No endpoint, account, cost, uptime, or production
claim is valid until explicitly measured and recorded. State files, credentials,
database dumps, and cloud-generated artifacts stay out of Git.

## Historical attribution

The historical [yourls-cf](https://github.com/abdalrahmanattya/yourls-cf) and
[test-yourls](https://github.com/abdalrahmanattya/test-yourls) repositories are
reference material for infrastructure lessons and failure modes only. This is
an original successor and will not copy YOURLS code, credentials, generated
state, or deployment workflows.

## Planned documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [Development](docs/development.md)
- [Initial decision record](docs/decisions/001-original-service-and-aws-boundaries.md)
