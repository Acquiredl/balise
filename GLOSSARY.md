# Glossary — Balise

Ubiquitous language for this repo. Terms are used exactly as defined here, in code, docs, and reports.

| Term | Definition |
|---|---|
| **Check** | One assessable item with a stable id (`A1`–`A10`, `B1`–`B22`), a legal hook, an authority tier, and a mode (deterministic / semantic / intake). The check id is the foreign key of the whole system: intake, report, sommaire, advice copy, insurer appendix, and verification trail all key on it. |
| **Module A** | External scan — checks assessable from the public website alone, no client input. |
| **Module B** | Intake assessment — organizational checks answered through the questionnaire (`intake/`). |
| **Authority tier** | Strength of a check's legal basis: `STATUTE` (explicit text of CQLR c. P-39.1 or LCCJTI), `CAI` (regulator guidance/expectation), `FIRM` (convergent law-firm interpretation, unsettled). Findings inherit the tier; contested points are never reported as settled law. |
| **Legal hook** | The statutory section or guidance document a check traces to (e.g., `s. 8.2`, `LCCJTI ss. 44-45`, `CAI Guidelines 2023-1`). Every check has one; `docs/VERIFICATION.md` gates their accuracy. |
| **Status** | Outcome of one check: `met` / `partial` / `not_met` / `not_applicable` / `unknown`. `unknown` is honest, never hidden — it means the evidence or the semantic engine wasn't available. |
| **Finding** | A check result bound to its evidence, reasoning, status, tier, and suggested next step. The unit that appears in reports and the verification trail. |
| **Verification trail** | Hash-chained JSONL record (format `balise-audit-trail/1`, `docs/VERIFICATION-TRAIL.md`) of every finding's evidence and reasoning: a genesis record binds the chain to its assessment and declares the record count; each record seals the previous record's hash. Guarantees are tiered and never blurred: edits, deletions, reordering and truncation are caught from the file alone; wholesale regeneration is caught against the head fingerprint in the delivered documents, and against the package's seals. Balise's signature feature; the deliverables regenerate from it without rescanning. |
| **Package** | The delivered whole of an assessment: rapport, sommaire, trail, `evidence/` archive, and the manifest — verifiable offline by anyone holding it (`balise verify`). |
| **Manifest** | The package's packing list (`manifest.json`, format `balise-assessment/1`), written last: trail head, shipped-bytes hashes of the post-close artifacts, and the declared seal set. Its own hash is the package's single sealing surface; nothing references it, and it never carries a self-hash. |
| **Seal** | An outer commitment applied to the manifest's shipped bytes. Two kinds: the **anchor** (OpenTimestamps → Bitcoin) says *when* and cannot be forged into the past; the **issuer signature** (Ed25519, key in the operator's password manager, fingerprint published in `docs/SIGNING.md`) says *who*. Declared in the manifest before applying, so a stripped seal is `SEAL-MISSING`, never a silent downgrade. |
| **Source reference** | A finding's record of an examined artifact: `{url, retrieved_at, sha256, content_type}`. The url and time are testimony; the sha256 binds the archived copy in `evidence/`, never the live site. What makes the `artifact_inspected` grade concrete; intake findings have none. The chain is the evidence index: the archive must hold exactly the referenced set. |
| **Assessment id** | Permanent assessment identifier (UUID), minted at run start, committed in the trail genesis, printed in both report headers. Everything in the package points back to it. |
| **Readiness posture** | Domain-level summary (transparency / governance / incidents / vendors-and-transfers / special-categories). Deliberately NOT a single percentage score — see ADR 0002. |
| **Assessment** | One run of Balise against one enterprise: a scan, optionally an intake, and the resulting report + verification trail. The unit a package delivers. |
| **Semantic engine** | The pluggable LLM component that runs judgment-type checks (plain-language analysis, coverage). Optional at runtime; absent → affected checks report `unknown`. See ADR 0003. |
| **Disclaimer** | The mandatory readiness-not-legal-advice notice. Present on every report, both languages, non-removable. |
| **Sommaire** | The visual client summary (`sommaire-balise.html`): stat tiles, per-domain posture bars, priority cards. The briefing; the rapport stays the verbose record. |
| **Client copy** | The authored owner-voice text in `advice.py` (plain title, why-it-matters, first action, priority) — the single source for the sommaire's cards and the rapport's exec opener. Legal voice (registry titles/hooks) is a separate surface; renderers may not invent words in either voice. |
| **Aperçu (mini-scan)** | Quick look from `balise scan --mini`: deterministic Module A checks only, rendered with full evidence treatment plus an honest count of what a full run adds. No engine, no intake, no package. |
| **Insurer appendix** | Report annex mapping findings to recurring cyber-insurance application themes, with an explicit not-assessed boundary for purely technical controls. Grounded in four real application forms (research 2026-08-23). |
| **Scope notice** | The loud public-body warning when the subject looks like a municipality/ministry: Balise assesses the private-sector regime (P-39.1), not the Loi sur l'accès. Born from pilot-000's roleplay subject. |
