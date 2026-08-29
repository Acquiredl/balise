# ADR-0005: The assessment runs locally; no server-side PI in v0.x

**Status:** `accepted` (2026-08-24) · revised 2026-08-29
**Date:** 2026-08-24
**Deciders:** operator

## Context

Two architectures were competing implicitly. **Local-run:** the intake is a conversation, the assessment runs on the assessor's own machine, and the subject's personal information never leaves it. **Hosted service:** the public site hosts the questionnaire, processes answers server-side, and emits the report. The second was attractive ("lock down one server instead of a PC") but changes the security posture, the Law 25 obligations, and the tool's identity in a single move: a public web service accepting PI is a production PII target with a 24/7 front door, triggers a mandatory PIA as an information system involving PI, flips the privacy-by-default check (s. 9.1) onto us, and silently deletes the intake conversation — a surface the pilot showed catches real comprehension failures.

There is also a self-consistency problem. A tool that assesses other people's handling of personal information should not casually become a custodian of it.

## Decision

> v0.x runs locally. **Personal information never resides on public-facing infrastructure.** The public site stays PI-free by construction: any online questionnaire is a static, client-side page that builds the intake file in the visitor's browser and is downloaded by them — nothing POSTed, nothing stored server-side. A hosted service is a named future phase, not a drift, gated on: a dedicated PIA and security review for the service, Quebec/Canada-hosted infrastructure, and the s. 9.1 defaults obligation being engineered in from the start.

## Consequences

**What gets easier:**
- The attack surface stays an encrypted, backed-up machine instead of a production web service run by one person.
- Our own Law 25 posture stays small and passable by our own assessment.
- The intake conversation — the part that catches comprehension failures — survives; the client-side pre-fill page shortens it rather than replacing it.

**What gets harder or more constrained:**
- Throughput is bounded by whoever is running it. v0.x does not scale on its own, by design.
- The pre-fill page must stay genuinely static. Any convenience feature that makes it transmit or retain answers violates this ADR, not just a checklist line.

**Revisit when:** the hosted phase's gates are met. At that point the right architecture is the inverse: hardened, provider-encrypted, Canada-hosted infrastructure holds the data and the local machine becomes an access client.

## Alternatives considered

- **Hosted service now** — rejected: takes on the security burden and statutory obligations of a PII service before the assessment itself is proven, and erases the conversation that makes the intake work.
- **Hybrid with server-side storage "just for convenience"** — rejected: any server-side PI puts the whole VPS in scope; the client-side page delivers the UX without the custody.

## References

- ADR-0004 (MIT license; the methodology is the artifact). Registry: B2 (PIA trigger), B21 (s. 9.1 defaults — flips applicable in the hosted phase). Pilot protocol step 7 (ops-security gate).
