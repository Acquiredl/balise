# ADR-0005: Consultancy first; no server-side PI in v0.x; self-serve is a gated future phase

**Status:** `accepted` (2026-08-24)
**Date:** 2026-08-24
**Deciders:** operator

## Context

Two product architectures were competing implicitly. Operator-run consultancy: the intake is a conversation, the assessment runs on the operator's machine, client PI never leaves it. Self-serve SaaS: the public site hosts the questionnaire, processes answers server-side, and emits the report. The second model was attractive ("lock down one server instead of a PC") but changes the security posture, the Law 25 obligations, and the product identity in one move: a public web service accepting PI is a production PII target with a 24/7 front door, triggers a mandatory PIA as an information system involving PI, flips the privacy-by-default check (s. 9.1) onto us, and silently deletes the intake conversation — a product surface the pilot showed catches real comprehension failures. It is also the competitor's model, which this project positions against.

## Decision

> v0.x is consultancy-first. **Client personal information never resides on public-facing infrastructure.** The public site stays PI-free by construction: any online questionnaire is a static, client-side page that builds the intake file in the visitor's browser and is downloaded by them — nothing POSTed, nothing stored server-side. Full self-serve is a named future phase, not a drift, gated on: revenue proof, a dedicated PIA and security review for the service, Quebec/Canada-hosted infrastructure, and the s. 9.1 defaults obligation being engineered in from the start.

## Consequences

**What gets easier:**
- The attack surface stays an encrypted, backed-up operator machine instead of a production web service run by a solo operator.
- Our own Law 25 posture stays small and passable by our own assessment.
- The intake conversation — a differentiator, not an overhead — survives; the client-side pre-fill page shortens it rather than replacing it.

**What gets harder or more constrained:**
- No fully-automated paid product in v0.x; throughput is bounded by operator hours (priced accordingly).
- The pre-fill page must stay genuinely static; any convenience feature that makes it transmit or retain answers violates this ADR, not just a checklist line.

**Revisit when:** the self-serve phase's gates are met. At that point the right architecture is the inverse: hardened, provider-encrypted, Canada-hosted infrastructure holds the data and the operator machine becomes an access client.

## Alternatives considered

- **Self-serve SaaS now** — rejected: security burden and statutory obligations of a PII service before first revenue; erases the conversation; converges on the competitor's shape.
- **Hybrid with server-side storage "just for convenience"** — rejected: any server-side PI puts the whole VPS in scope; the client-side page delivers the UX without the custody.

## References

- ADR-0004 (what is sold: the operator layer). Registry: B2 (PIA trigger), B21 (s. 9.1 defaults — flips applicable in the self-serve phase). Pilot protocol step 7 (ops-security gate).
