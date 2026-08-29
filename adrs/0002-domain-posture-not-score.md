# ADR 0002 — Readiness posture by domain, never a single compliance score

**Status:** accepted (2026-08-22)

## Context

The nearest comparable tool publishes a single 0–100 compliance score, with a pass mark on it. A single number is marketable but functions as an implied legal verdict — precisely what a readiness self-assessment must not render, and what the liability line ("not legal advice") cannot survive.

## Decision

Reports summarize **readiness posture per domain** (transparency, governance, incidents, vendors & transfers, special categories) using the per-check statuses. No aggregate percentage, no "compliant/non-compliant" verdict, anywhere.

## Consequences

- Consistent with the disclaimer instead of at war with it; a report can be shown to a lawyer or insurer without embarrassment.
- Loses the punchy single number, which is the first thing a skim-reader looks for. Mitigation: the domain-posture visual is itself distinctive, and the depth story ("scanners check your website; Balise checks your obligations") is the lead.

## Trade-off

Some readers want the number. If feedback keeps demanding one, revisit — but any future score must be labeled a coverage metric (how much is documented), never a compliance metric.
