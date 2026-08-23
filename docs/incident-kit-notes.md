# Incident Kit — Design Notes (from verification gate, 2026-08-23)

Feature candidate surfaced while verifying the Regulation respecting confidentiality incidents (A-2.1, r. 3.1) against official text. Not yet built; captured for the post-probe backlog.

## One incident record, three generated artifacts

The Regulation prescribes three overlapping content lists:

| Artifact | Source | Elements |
|---|---|---|
| Register entry | Reg. s. 7 | 8 — covers ALL incidents ("whether or not" serious injury); ≥5-yr retention, kept up to date (s. 8) |
| CAI notice | Reg. s. 3 | 11 — written; supplemented "promptly" as new info arrives (s. 4) |
| Individual notice | Reg. s. 5 | 6 — public-notice alternative in 3 circumstances + rapid-action option (s. 6) |

Shared core across all three: description of the PI concerned, circumstances, incident date/period, awareness date, persons affected, risk-of-serious-injury reasoning, mitigation measures. A single structured incident record can generate all three artifacts — written once, dispatched in parallel.

**Sequencing rule (verified, s. 3.5):** CAI notice and individual notices are *parallel prompt duties*. There is no CAI-confirmation step before notifying individuals. Individual notice defers only where it would hamper an investigation by a body *legally responsible* for crime/offence prevention — never internal or hired investigations, and CAI notice never defers.

## Product shape

Balise report recommendation (B1 domain): ship pre-built templates — an 8-field register schema, an 11-element CAI notice template, a 6-element individual notice template — so a client's incident preparedness is generative, not aspirational. Fits the audit-trail thesis: the incident record is itself an evidence trail.
