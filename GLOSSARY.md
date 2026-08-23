# Glossary — Balise

Ubiquitous language for this repo. Terms are used exactly as defined here, in code, docs, and reports.

| Term | Definition |
|---|---|
| **Check** | One assessable item with a stable id (`A1`–`A9`, `B1`–`B11`), a legal hook, an authority tier, and a mode (deterministic / semantic / intake). |
| **Module A** | External scan — checks assessable from the public website alone, no client input. |
| **Module B** | Intake assessment — organizational checks answered through the questionnaire (`intake/`). |
| **Authority tier** | Strength of a check's legal basis: `STATUTE` (explicit text of CQLR c. P-39.1 or LCCJTI), `CAI` (regulator guidance/expectation), `FIRM` (convergent law-firm interpretation, unsettled). Findings inherit the tier; contested points are never reported as settled law. |
| **Legal hook** | The statutory section or guidance document a check traces to (e.g., `s. 8.2`, `LCCJTI ss. 44-45`, `CAI Guidelines 2023-1`). Every check has one; `docs/VERIFICATION.md` gates their accuracy. |
| **Status** | Outcome of one check: `met` / `partial` / `not_met` / `not_applicable` / `unknown`. `unknown` is honest, never hidden — it means the evidence or the semantic engine wasn't available. |
| **Finding** | A check result bound to its evidence, reasoning, status, tier, and suggested next step. The unit that appears in reports and the audit trail. |
| **Audit trail** | Append-only JSONL record of every finding's evidence and reasoning for one assessment run. The product's signature feature; also embedded in the report annex. |
| **Readiness posture** | Domain-level summary (transparency / governance / incidents / vendors-and-transfers / special-categories). Deliberately NOT a single percentage score — see ADR 0002. |
| **Engagement** | One assessment of one enterprise: a scan, optionally an intake, and the resulting report + audit trail. |
| **Semantic engine** | The pluggable LLM component that runs judgment-type checks (plain-language analysis, coverage). Optional at runtime; absent → affected checks report `unknown`. See ADR 0003. |
| **Disclaimer** | The mandatory readiness-not-legal-advice notice. Present on every report, both languages, non-removable. |
