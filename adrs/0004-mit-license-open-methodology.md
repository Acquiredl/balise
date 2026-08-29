# ADR-0004: MIT license; the methodology is the artifact

**Status:** `accepted` (2026-08-24) · revised 2026-08-29
**Date:** 2026-08-24
**Deciders:** operator

## Context

Balise is public under MIT. The check catalog is the part that took the most work and decays the fastest: every statutory reference in it was read against the consolidated text by a human, and the whole thing goes stale the moment the statute or the regulator moves. That raised the licensing question directly — should the license restrict wrapping (AGPL-style) to protect the catalog?

## Decision

> The license stays MIT, catalog included. Balise's only real claim is that a reader can follow every finding back to the law themselves, so the methodology has to be readable end to end by anyone, with no condition attached to reading it. A license restricting reuse would be protecting an artifact whose entire value is that it is open to inspection.

## Consequences

**What gets easier:**
- The strongest honest-broker claim available: anyone can read exactly how every finding is produced, and disagree with it in public.
- Zero friction for anyone who wants to run it, fork it, or lift a check into their own work.
- The repository stands on its own as a worked example, independent of anything built on top of it.

**What gets harder or more constrained:**
- A fork's check catalog decays the moment guidance moves (first observed 2026-08-24: the CAI's 2025 recruitment guidelines entered the registry only through a verification-gate sitting). Staying current is a discipline, not a license term — a fork is a snapshot, and nothing in MIT changes that.

**Revisit if:**
- The verified catalog becomes the target of bulk extraction and republication with the verification story stripped off. A split license (MIT engine, source-available registry) returns to the table then.

## Alternatives considered

- **AGPL** — rejected: adds friction for every honest reader and fork in order to defend against a case that has not happened, and the thing worth defending (currency) is not something a license confers.
- **Closed registry, open engine** — rejected: the verified check catalog IS the credibility demonstration; hiding it guts the inspectability claim the whole tool rests on.

## References

- ADR-0001 (authority tiers), `docs/VERIFICATION.md` (the currency mechanism), `docs/VERIFICATION-TRAIL.md` (the accountability mechanism).
