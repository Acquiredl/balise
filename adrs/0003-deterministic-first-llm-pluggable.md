# ADR 0003 — Deterministic checks first; the semantic engine is optional and pluggable

**Status:** accepted (2026-08-22)

## Context

Some checks are mechanical (a privacy-policy link exists; a tracker script is present in the initial payload; a French version exists). Others require judgment (is the policy in clear and plain language? does it cover the s. 8 disclosures?). Judgment checks need an LLM; mechanical checks must not, or the tool becomes slow, costly, non-reproducible, and un-runnable without an API key.

## Decision

- Every check declares a mode: `deterministic`, `semantic`, or `intake`.
- Deterministic checks run always, produce reproducible evidence (matched snippets, URLs), and never call a model.
- Semantic checks run through a pluggable engine (`semantic.py`). Engine absent or unconfigured → the check reports `unknown` with the reason stated. The report never silently degrades.
- Website content fed to the semantic engine is **untrusted input**: prompts treat it as data under analysis, the engine gets no tools, and outputs are schema-validated before becoming findings (see THREAT-MODEL.md).

## Consequences

- The tool demos meaningfully with zero configuration (Module A deterministic subset) — important for the free-scan funnel and for the public repo as a career artifact.
- Honest `unknown`s instead of hallucinated verdicts — consistent with ADR 0001's posture.
- Two code paths to maintain. Accepted: the split is also the security boundary.
