# ADR 0001 — Every finding carries an authority tier

**Status:** accepted (2026-08-22)

## Context

The Law 25 compliance market routinely overstates contested points as settled law: a "72-hour breach deadline" (GDPR contamination — the statute says "with diligence"), cookie opt-in presented as statutory command (it rests on CAI Guidelines 2023-1; s. 9.1 explicitly carves browser cookies out of privacy-by-default; no case law), and "first sanctions in 2026" marketing with zero named cases. None of the tools in this space distinguishes statute from guidance from interpretation.

## Decision

Every check — and therefore every finding — is tagged `STATUTE`, `CAI`, or `FIRM`, and reports state the tier in plain language. Contested items (A5 cookie consent, the s. 17 adequacy-analysis depth, Charter s. 52 coverage of privacy policies) are always reported at their true tier.

## Consequences

- The tool cannot overstate the law; this is the trust differentiator and the liability posture in one mechanism.
- Reports are slightly more nuanced to read — accepted; a reader who has to defend a position values knowing which findings will hold.
- The tier assignments themselves become load-bearing data → they are gated by `docs/VERIFICATION.md` (human check against LegisQuébec before any finding is relied on).

## Trade-off

Simpler tools can shout "YOU ARE NON-COMPLIANT, FINES UP TO $25M" louder than we can. We concede the fear-marketing channel deliberately — the honest-broker position compounds with the verification trail, and the fear claims are factually hollow (no verified AMP against any enterprise as of Aug 2026).
