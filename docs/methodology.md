# Balise — Assessment Methodology (v0.1)

**Date:** 2026-08-22

## Summary

The domain artifact for Balise: what it checks, how each check traces to law, how findings are scored and reported. Built from primary-source research (CAI guidance + statute triangulated through ≥3 convergent sources) and a survey of what existing automated tools actually check. On ratification, this seeds the repo at Stage 2.

**Verification obligation before shipping:** LegisQuébec and CanLII blocked automated access, so statutory section numbers were triangulated, not read from the consolidated statute. A human spot-verify of every section reference against CQLR c. P-39.1 on LegisQuébec is a **hard pre-ship gate**.

## Positioning (from the combined research)

**Balise is the organizational-depth readiness assessment with legible reasoning.** Three deliberate contrasts with the field:

1. **Depth vs surface.** The automated tools in this space check the website surface: policy present, banner present, officer named. Most Law 25 obligations are organizational — incident registry, PIAs, vendor contracts, biometrics. Balise = external scan **plus** structured intake covering the organizational layer.
2. **Honest broker vs fear marketing.** No AMP or penal fine against any enterprise has been verified through Aug 2026; "first sanctions in 2026" claims are marketing with zero named cases behind them. Balise reports obligation gaps, incident preparedness, and insurance-questionnaire alignment, and never invokes an imminent fine. Where the surrounding copy runs on fear, a claim that survives being checked is worth more than a loud one.
3. **Legible reasoning vs black-box score.** Every finding carries its evidence, its legal hook, and its **authority tier** (see below). The tool's own transparency mirrors s. 12.1's explainability demand — Balise eats its own cooking.

**Liability line (hard):** readiness self-assessment, not legal advice. Disclaimer on every report; recommendations phrased as obligations-to-review, not legal conclusions; no "you are compliant" verdicts — readiness posture only.

## The authority-tier system (core differentiator)

Every check is tagged with the strength of its legal basis:

- **[STATUTE]** — explicit statutory text (CQLR c. P-39.1 or LCCJTI).
- **[CAI]** — regulator guidance/expectation (e.g., Guidelines 2023-1 on consent).
- **[FIRM]** — convergent law-firm interpretation, not settled text or case law.

Findings inherit the tag. This prevents the tool from overstating contested points, which is the whole reason the tier system exists.

**Encoded corrections to common market errors:**
- **No "72-hour" breach deadline.** The statutory standard is notification "with diligence" (ss. 3.6). The 72h figure is GDPR contamination propagated by vendor marketing; Balise explicitly flags it as a misconception.
- **Cookie opt-in is scored as [CAI] expectation, not [STATUTE].** CAI Guidelines 2023-1 read s. 8.1 as off-by-default for tracking/profiling; s. 9.1 explicitly carves browser cookies out of privacy-by-default; no case law. Best practice: EU-style opt-in banner — reported as regulator expectation.
- **s. 17 adequacy analysis for US-hosted SaaS** has no whitelist and no prescribed depth — reported as a proportionality judgment with [FIRM]-level methodology.

## Module A — External scan (website-checkable, no client input)

| # | Check | Legal hook | Tier |
|---|---|---|---|
| A1 | Privacy policy exists on website | s. 8.2 | STATUTE |
| A2 | Policy in clear/plain language; covers purposes, rights, third-party recipients, out-of-Quebec communication | ss. 8, 8.2 + CAI drafting guide | STATUTE + CAI |
| A3 | Privacy officer title + contact published | s. 3.1 | STATUTE |
| A4 | Governance-policy information published | s. 3.2 | STATUTE |
| A5 | Non-essential trackers firing before consent; banner with accessible refuse option | s. 8.1 + Guidelines 2023-1 | CAI (contested) |
| A6 | Tracking/geolocation/profiling tech disclosed + activation means stated | s. 8.1 | STATUTE |
| A7 | French version of site, policy, and ToS (French-first for adhesion contracts) | Charter s. 52, s. 55 | STATUTE + FIRM (policies-in-scope is firm interpretation) — dual flag: Law 25 plain-language + OQLF exposure ($3–30K/offence) |
| A8 | Consent wording on PI-collecting forms: purpose-granular, separate presentation | s. 14 | STATUTE |
| A9 | Policy amendment-notice practice | s. 8.2 | STATUTE |

## Module B — Intake questionnaire (organizational layer)

| # | Domain | Legal hook | Tier | Notes |
|---|---|---|---|---|
| B1 | Confidentiality-incident register (exists, 8 prescribed elements, 5-yr retention) + response process | ss. 3.5–3.8 + Regulation | STATUTE | "With diligence" standard, not 72h |
| B2 | PIAs for new/overhauled systems involving PI | s. 3.3 | STATUTE | |
| B3 | PIAs + written agreements for out-of-Quebec communication (incl. every US-hosted SaaS vendor) | s. 17 | STATUTE (depth: FIRM) | **Empirically the biggest unmet paper obligation for SMBs** |
| B4 | Processor/vendor contracts with confidentiality clauses | s. 18.3 | STATUTE | |
| B5 | Internal governance policies: lifecycle roles, retention/destruction, complaint process | s. 3.2 | STATUTE | |
| B6 | **Biometric systems** (time-clocks, facial-recognition access): express consent + CAI declaration 60 days pre-service | LCCJTI ss. 44–45 | STATUTE | **Highest-yield question: the CAI's only active enforcement area** (Transcontinental 2024, Metro 2025 — cease/destroy orders) |
| B7 | Automated-decision disclosure (scoring, filtering) | s. 12.1 | STATUTE | |
| B8 | Minors under 14: parental-authority consent at collection | s. 4.1 | STATUTE | E-commerce relevance |
| B9 | Data-portability request handling (structured, commonly used format; collected-not-inferred PI) | s. 27 | STATUTE | Wave 3 (Sept 2024) |
| B10 | Sensitive-information handling: express consent for use/communication | ss. 12–13 | STATUTE | |
| B11 | Staff privacy training/awareness | CAI guidance expectation | CAI | Not an explicit statutory mandate — tagged honestly |

## Scoring and report

- **Per-check status:** met / partial / not-met / not-applicable / unknown. Never a binary "compliant" verdict.
- **Priority model:** P1 = [STATUTE] + enforcement-active (B6 biometrics; B1 incidents) or externally visible (A1, A3, A7); P2 = [STATUTE] paper obligations (B3 s.17 PIAs, B4, B5); P3 = [CAI]/[FIRM]-tier and lower-likelihood items. Conservative-middle: prioritization reflects *both* legal clarity and observed enforcement, and says so.
- **Readiness posture by domain** (transparency / governance / incidents / vendors & transfers / special categories) — deliberately **not** a single percentage score. A single "82% compliant" number implies a legal conclusion; domain posture doesn't. The scanners that publish one are stating a verdict they have no standing to state.
- **Report:** bilingual (FR canonical, EN mirror). Each finding = evidence → obligation → authority tier → gap → suggested next step. Full reasoning trace appended (the verification trail).
- **Insurer appendix:** findings mapped to the recurring cyber-insurance questionnaire themes (incident procedures, MFA/backups adjacent, documented audit) — shaped so the report is usable at the broker's "prove it" moment, which is where an SMB most often needs this paperwork.

## Outcomes / Decisions

- v0.1 drafted from Stage 1 research, 2026-08-22. Ratified by the operator.
- Pre-ship hard gate recorded: human verification of statutory references against LegisQuébec.
- On ratification → Stage 2: repo scaffold (`balise` on Acquiredl), `/kickoff` + METACOG.md, build.
