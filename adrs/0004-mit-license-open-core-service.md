# ADR-0004: MIT license; the product is the operator, not the code

**Status:** `accepted` (2026-08-24)
**Date:** 2026-08-24
**Deciders:** operator

## Context

Balise is public under MIT. As the commercial offer took shape (assessment tiers, a maintenance subscription, remediation routing), the question surfaced: if anyone can fork the code, what exactly is being sold, and should the license restrict commercial wrapping (AGPL-style)?

## Decision

> The license stays MIT. What is sold is everything the repository cannot contain: the intake conversation conducted by a person, accountability for a delivered report (the trail's fingerprint sealed in the deliverable by a named operator on a date), currency (the verification-gate discipline that re-opens when the statute or the CAI moves), and remediation routing. The open code is the trust asset: a fully inspectable methodology is a claim no closed competitor can make.

## Consequences

**What gets easier:**
- The strongest honest-broker claim available: anyone can read exactly how every finding is produced.
- MSP/agency channel adoption has zero licensing friction.
- The repository does portfolio work independently of revenue.

**What gets harder or more constrained:**
- A third party can SaaS-wrap Balise and undercut the automated tier. Accepted: the automated scan is deliberately the cheapest rung; value is loaded into the human tiers, which do not fork.
- A fork's check catalog decays the moment guidance moves (first observed 2026-08-24: the CAI's 2025 recruitment guidelines entered the registry only through a verification-gate sitting). Staying current is the recurring product; the fork is a snapshot.

**Revisit if:**
- A well-resourced actor commercializes a wrapped Balise at scale in Quebec, or the registry's verified content becomes the primary target of extraction. AGPL or a split license (MIT engine, source-available registry) returns to the table then.

## Alternatives considered

- **AGPL** — rejected: deters the MSP channel this project wants, and the actual moat (conversation, accountability, currency) needs no license to defend.
- **Closed registry, open engine** — rejected for now: the verified check catalog IS the credibility demonstration; hiding it guts the inspectability claim.

## References

- ADR-0001 (authority tiers), docs/VERIFICATION.md (the currency mechanism), docs/AUDIT-TRAIL.md (accountability mechanism).
