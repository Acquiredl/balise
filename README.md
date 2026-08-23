# Balise

**Law 25 compliance-readiness assessment for Quebec SMBs — with reasoning you can actually read.**

*[Version française : README.fr.md](README.fr.md)*

Balise scans a company's public website and combines it with a structured intake questionnaire to assess readiness against Quebec's Law 25 privacy obligations. It produces a bilingual (FR/EN) report in which **every finding carries its evidence, its legal hook, and the authority tier of that legal basis** — plus a machine-readable audit trail of the entire assessment.

> Balise is a readiness self-assessment tool. It is **not legal advice**, and it never renders a compliance verdict.

## Why it's different

Automated Law 25 tools today check the website surface: is there a cookie banner, is there a privacy policy. Most of Law 25 lives elsewhere — the incident register, privacy impact assessments for every US-hosted SaaS vendor, processor contracts, biometric-system declarations. Balise assesses both layers:

- **Module A — external scan:** privacy policy presence and content, privacy-officer publication, tracker/consent behavior indicators, French-language exposure (Charter s. 52).
- **Module B — organizational intake:** incident register, PIAs, s. 17 transfer agreements, vendor contracts, biometrics (the CAI's only active enforcement area), automated decisions, minors, portability.

And three design rules no competitor follows:

1. **Authority tiers.** Every check is tagged `STATUTE` (explicit legal text), `CAI` (regulator expectation), or `FIRM` (convergent interpretation). Contested points — like cookie opt-in, which rests on CAI guidance rather than settled statute — are reported at their true strength, never inflated. There is no "72-hour breach deadline" in here, because there isn't one in the law (that's GDPR).
2. **No compliance score.** Reports show readiness posture by domain, never a single "82% compliant" number — a percentage is an implied legal verdict, and this tool doesn't render verdicts.
3. **A legible audit trail.** Every finding's evidence and reasoning is recorded to tamper-evident JSONL and annexed to the report. Law 25's own s. 12.1 demands explainability of automated decisions — an assessment tool should hold itself to the same standard.

## Usage

```bash
pip install -e .
balise scan https://www.example.com --out ./engagement-001
# with the organizational questionnaire:
balise scan https://www.example.com --intake intake/filled.yaml --out ./engagement-001
```

Deterministic checks run with zero configuration. Judgment-type checks (plain-language analysis, disclosure coverage) use an optional LLM engine — set `ANTHROPIC_API_KEY` and install the `semantic` extra; without it, those checks honestly report `unknown` instead of guessing.

```bash
pip install -e ".[semantic]"
```

## Security posture

See [THREAT-MODEL.md](THREAT-MODEL.md): SSRF-guarded fetching, prompt-injection containment for untrusted site content (no tools, schema-validated outputs, fail-closed), local-only client data, tamper-evident audit records.

## Status

v0.1 — working scanner and report pipeline; statutory references pending the human verification gate ([docs/VERIFICATION.md](docs/VERIFICATION.md)) before any client-facing use.

## License

MIT
