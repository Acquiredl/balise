# Balise

**Law 25 readiness assessment for Quebec SMBs, with reasoning you can actually read.**

*[Version française : README.fr.md](README.fr.md)*

Balise scans a company's public website and pairs it with a short intake questionnaire to assess readiness against Quebec's Law 25 privacy obligations. It produces a bilingual report (FR/EN) where every finding shows its evidence, its legal basis, and how strong that basis actually is. The whole assessment is also recorded in a machine-readable audit trail.

> Balise is a readiness self-assessment tool. It is not legal advice, and it never renders a compliance verdict.

## Why it's different

Most automated Law 25 tools check the surface of your website: is there a cookie banner, is there a privacy policy. The thing is, most of Law 25 lives elsewhere. The incident register, the privacy impact assessments for every US-hosted SaaS vendor, the processor contracts, the biometric declarations. Balise assesses both layers:

- **Module A, external scan:** privacy policy presence and content, privacy officer publication, tracker and consent indicators, French-language exposure.
- **Module B, organizational intake:** incident register, PIAs, transfer agreements, vendor contracts, biometrics, automated decisions, minors, portability, and more.

29 checks total, every one traced to a statutory section or regulator guidance, and every reference human-verified against the official consolidated text on LegisQuébec.

Three design rules we hold ourselves to:

1. **Authority tiers.** Every check is tagged by the strength of its legal basis: `STATUTE` (explicit legal text), `CAI` (regulator expectation) or `FIRM` (convergent interpretation). Contested points get reported at their true strength, never inflated. The compliance market is full of confident claims that don't survive a read of the actual law, and we would rather be precise than loud. The receipts are in [docs/methodology.md](docs/methodology.md).
2. **No compliance score.** Reports show readiness posture by domain, never a single percentage. The reasoning behind that refusal is in the docs too.
3. **A legible audit trail.** If your business automates decisions, Law 25 expects you to be able to explain them. Balise is itself an automated assessor, so it has the same problem, and it ships with the answer built in: every finding's evidence and reasoning is recorded in tamper-evident JSONL and annexed to the report. The tool is a working example of the traceability it asks about.

## Usage

```bash
pip install -e .
balise scan https://www.example.com --out ./engagement-001
# with the organizational questionnaire:
balise scan https://www.example.com --intake intake/filled.yaml --out ./engagement-001
```

Deterministic checks run with zero configuration. Judgment-type checks (plain-language analysis, disclosure coverage) use an optional LLM engine. Without it, those checks honestly report `unknown` instead of guessing.

```bash
pip install -e ".[semantic]"
```

## Honest limitations

Some things this version does not do yet, so you don't find out the hard way:

- Tracker analysis is static. Balise sees which tracker scripts ship in the page and whether a consent platform is present, but it does not run a browser to confirm what fires before consent. Findings say so explicitly.
- The law's diffusion duty (making the privacy policy actually reach people, not just publishing it) can't be observed from a website scan. It's covered through the intake instead.
- Module B answers are self-reported. Balise records them as such and never pretends it verified the paperwork.

## Security posture

See [THREAT-MODEL.md](THREAT-MODEL.md): SSRF-guarded fetching, prompt-injection containment for untrusted site content, local-only client data, tamper-evident audit records.

## Status

v0.1. Working scanner and report pipeline. Statutory references verified against LegisQuébec (verification gate closed 2026-08-23, see [docs/VERIFICATION.md](docs/VERIFICATION.md)). Still early, and it will evolve with the project.

## License

MIT. Questions or feedback, open an issue. Happy to talk.
