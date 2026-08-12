# ADR 006: Make edge and operations evidence first-class

- Status: Accepted for the non-applied target
- Date: 2026-08-12

## Decision

Terminate approved public traffic at an ALB protected by AWS WAF managed common
rules and an IP rate limit. HTTP redirects to HTTPS only when an ACM
certificate ARN is supplied; an incomplete certificate configuration returns
an explicit 503 rather than silently serving plaintext application traffic.

Use structured ECS logs, encrypted retention, ECS/ALB/Aurora alarms, a small
CloudWatch dashboard, ECS deployment circuit-breaker rollback, and CPU/memory
target tracking. These are planned controls until a cloud demonstration
produces measured evidence.
