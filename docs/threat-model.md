# Misuse and abuse threat model

Status: local threat model for the credential-free implementation. Application
controls marked local are supported by source/tests; cloud controls remain
design targets until measured in an approved environment.

## Assets and trust boundaries

| Asset/boundary | Security objective |
|---|---|
| Destination URL and link metadata | Confidentiality, integrity, controlled retention |
| Bearer identity and ownership decision | Prevent unauthorized management |
| Public resolver | Availability without becoming an SSRF/open-redirect proxy |
| Application container | Least privilege, non-root execution, bounded egress |
| Database | Encryption, backups, recovery, no credential leakage |
| ALB/WAF/cloud edge | TLS, rate controls, abuse filtering, safe exposure |
| CI/CD and image registry | Provenance, immutable promotion, no long-lived keys |

## Abuse cases and mitigations

| Threat | Mitigations in this contract/design | Residual risk/evidence needed |
|---|---|---|
| Open redirect used for phishing | Owner-token/API authorization, destination validation, API creation/resolution limits, same-origin UI Origin validation, 302/no-store | Moderation/reporting is out of scope; deployment-level abuse measurement remains. |
| SSRF via destination validation | Reject private/loopback/link-local/metadata ranges; resolver never fetches destination | DNS rebinding and dual-stack edge cases require implementation tests. |
| Brute-force code enumeration | 6–32 character codes, rate limiting, generic 404/410 responses | High-value codes may still be discoverable; measure entropy and request budgets. |
| Code squatting/collision | Server-generated entropy, unique constraint, 409 for requested collisions | Distribution and retry behavior require integration evidence. |
| Credential theft | Bearer fixtures are local-only and excluded from logs; external identity is a target boundary | ECS secret-to-environment wiring and token rotation require a reviewed cloud implementation. |
| Unauthorized link changes | Owner/admin authorization and 403 semantics | Ownership store and admin policy need tests; no enterprise IAM claim. |
| Destination leakage in logs | Redaction rule and code hash logging | Third-party middleware/access logs need inspection. |
| Resource exhaustion | URL limits plus local API/UI creation, failed-auth, and resolution limits; WAF is a target control | Exact budgets and WAF rules remain unmeasured. |
| Malicious destination availability attack | Resolver does not follow destination; bounded response | Downstream victim impact cannot be eliminated by a shortener. |
| Database compromise | Private subnets, encryption, Secrets Manager, least-privilege roles | Cloud backup/restore and key policy require approved verification. |
| Supply-chain compromise | Locked runtime dependencies, multi-platform pinned image digests, non-root image, local Trivy scan with 0 HIGH/CRITICAL | GitHub-hosted SBOM publication and provenance remain unverified. |
| CI/CD deployment abuse | Environment-only OIDC subject and immutable-image design | Trust behavior still needs approved GitHub/AWS verification. |
| Delete/expiry resurrection | Tombstone state and no code reuse; 410 semantics | Retention and purge schedule need an explicit operational decision. |

## Residual-risk boundary

This project does not promise content moderation, malware scanning, legal
compliance, anonymous abuse elimination, or enterprise identity. Those are
explicitly outside the first implementation and must not be implied by a
successful local test run.
