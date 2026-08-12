# ADR 002: Use two-AZ tiers with one optional shared NAT gateway

- Status: Accepted for the non-applied target
- Date: 2026-08-12

## Decision

Create public ALB subnets, private ECS subnets, and isolated Aurora subnets in
two availability zones. Use private VPC endpoints by default for the AWS APIs
needed by ECS runtime operations. A NAT gateway is disabled by default and is
available only when an explicitly approved external dependency requires it.
Production high availability would normally use one NAT gateway per AZ or
retain the endpoint-only design after confirming every runtime dependency.

ECS tasks never receive public IPs. The endpoint-only default covers image
pulls, logging, secret retrieval, KMS, STS, and DNS. ECS security-group egress
does not permit arbitrary internet destinations; enabling NAT alone does not
widen that policy.
