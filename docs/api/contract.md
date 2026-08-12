# API contract

The normative contract is [`openapi.yaml`](openapi.yaml). This page records
the decisions that are easy to miss when implementing it.

## Public resolution semantics

`GET /r/{code}` is unauthenticated and returns `302 Found` with `Location` and
`Cache-Control: no-store`. The resolver does not fetch, inspect, or follow the
destination. Unknown codes return `404`; expired, disabled, and tombstoned
codes return `410`. Response bodies must not disclose ownership, destination,
or whether a previously valid code existed.

## Management semantics

Management endpoints require an opaque bearer token issued outside this
service. The API only validates the presented identity and enforces ownership;
it is not an identity provider. Owners and explicitly authorized administrators
may read, update, disable, and soft-delete links.

`DELETE` creates a tombstone and never releases the code for reuse. A disabled
link can be re-enabled by its owner; an expired or deleted link cannot be
re-enabled. Expiry can be shortened but not extended after it has passed;
state-conflicting updates return `409`.

## Validation and privacy

- Only `http` and `https` destinations are accepted.
- Destination URLs are limited to 2,048 characters and must have a host.
- Loopback, link-local, private, unspecified, and metadata-service addresses
  are rejected after DNS resolution; redirects must not become an SSRF proxy.
- Codes are 6–32 characters from `[A-Za-z0-9_-]`.
- Logs contain request ID, route, outcome, latency, and code hash—not full
  destination URLs, authorization headers, tokens, or database values.
- `ownerId` is pseudonymous and must not be an email address.
