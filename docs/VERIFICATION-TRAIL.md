# Verification trail (piste de vérification) — format and guarantees (v1)

The verification trail is the assessment's machine-readable record: one JSONL file, hash-chained, from which the rapport and sommaire can be regenerated without rescanning. This document freezes the format and states exactly what verification does and does not prove.

The design derives from the [loxodonta](https://github.com/Acquiredl/loxodonta) trail canon — loxodonta is a flight recorder for AI agents, and its decision records are the canon for trail designs derived from it. Three of them govern this format: ADR-0006 (the evidence-grade scale and the genesis provenance corollary), ADR-0007 (the package manifest as the single sealing surface, and the verdict vocabulary below), ADR-0008 (the issuer signature admitted for cross-party delivery, and the cage around what it claims). Where this document states a rule without arguing it, the argument lives there.

## Format: `balise-audit-trail/1`

The format identifier keeps its original name: it is frozen (hashes cover its bytes in every existing genesis record), and renaming it would orphan every trail issued before the public name changed to *verification trail*.

Line 1 is the **genesis record**; every following line is one **finding record**. Field names are **frozen**: hashes cover the field-name bytes, so renaming any field orphans every existing trail.

Genesis record fields: `format`, `ts`, `target`, `assessment_id` (permanent assessment identifier, minted at run start and printed in the report header; added 2026-08-25 — verifiers must not require it), `tool`, `engine` (the semantic model configured for the run, or `none`; added 2026-08-25 — verifiers must not require it, so pre-existing trails stay valid), `prompt_sha256` (fingerprint of the system prompt and authored questions), `catalog_sha256` (fingerprint of the full check catalog), `eval_suite` (fingerprint of the eval fixture pack the tool was held to, or `none` outside the repo) — the three fingerprints added 2026-08-25 under the same rule: verifiers must not require them — `records` (the exact number of finding records that follow), `prev` (always `null`), `sha256`. Together, `tool`, `engine` and the fingerprints answer "why did this assessment change": any change to the model, the prompts or the catalog is visible in the genesis of the trail it produced. The freeze rule bars renaming or removing fields; additive genesis metadata is permitted precisely because verification never depends on optional fields.

Finding record fields: `ts`, `check`, `legal_hook`, `tier`, `contested`, `status`, `evidence_grade` (added 2026-08-25; additive, verifiers must not require it — absent from pre-existing trails), `evidence`, `reasoning`, `reasoning_fr`, `sources` (added 2026-08-25; additive, verifiers must not require it — present only when the check examined an artifact), `prev` (the previous record's `sha256`), `sha256`.

## Source references and the evidence archive

A finding that examined an artifact carries `sources`: one reference per examined page, each `{url, retrieved_at, sha256, content_type}`. The honesty rule: `url` and `retrieved_at` are testimony, and the `sha256` binds the **archived copy** written into the assessment's `evidence/` folder at report time — never the live site. A source reference is what makes the `artifact_inspected` grade concrete: the exact bytes examined are on file, named by their hash (`evidence/<sha256>.html`), so anyone can re-check a quote against the artifact the finding actually rested on.

The chain is the evidence index: the expected contents of `evidence/` are derived by walking the finding records and collecting source references. The archive must contain exactly that set — matching hashes, no extras. A file in the archive that no finding references belongs to nothing and should be treated with suspicion. Intake findings carry no `sources`: the subject's answers are testimony (`self_reported`), and there is no examined artifact to archive.

## Canonical form

`sha256` is SHA-256 over the record's canonical JSON, minus the `sha256` field itself:

1. Keys sorted lexicographically.
2. Compact separators: `,` and `:`, no whitespace.
3. Raw UTF-8 (no ASCII escaping), no trailing newline.
4. No floats anywhere in the schema — timestamps are strings for exactly this reason (float serialization is not portable).

In Python: `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`. The rules are normative; the Python idiom is not.

## Evidence grades

Each finding record carries an `evidence_grade` saying what kind of evidence backs it. The grade qualifies the status, never changes it: it measures how independent the evidence is, not how correct the conclusion is. A grade-3 observation can still be misread; a grade-0 answer can still be true.

| Grade | Meaning | In Balise v0.1 |
|---|---|---|
| `self_reported` | The subject's word, unexamined | Every Module B finding: intake answers are recorded, not checked |
| `document_evidenced` | A supporting document was received | Not yet produced; reserved for client-document review |
| `artifact_inspected` | The artifact itself was examined | Every Module A finding: the fetched site is the artifact, whether a deterministic detector or a semantic check examined it |
| `independently_observed` | Recomputable by the verifier without trusting anyone | Not attached to findings; this is the grade of the chain-integrity claims themselves |

The report renders the grade on every finding ("Nature de la preuve" / "Evidence basis") so a reader sees at a glance which findings rest on the enterprise's word and which were observed.

## Verification (`report.verify_audit_trail`)

Walks the file once and checks: each record's recomputed canonical hash equals its stored `sha256`; each record's `prev` equals the previous record's hash (genesis: `null`); the genesis `format` matches; and the genesis `records` count equals the number of finding records present.

## Guarantee tiers — stated honestly

1. **Unconditional (the file alone):** any edited field, deleted record, reordering, or truncated tail is detected. Truncation is caught by the genesis record count.
2. **Against the delivered report:** the trail's final hash (its *head*) is printed in the rapport and the sommaire. A wholesale-regenerated trail verifies internally, but its head will not match the fingerprint in the documents the client holds — the client's copy serves as their head record. Pass that fingerprint as `expect_head` to check this tier. This establishes consistency between the trail and the documents a client already holds; it does not by itself establish which version was originally delivered — that is tier 3's gap, and it stays open until the head is sealed externally.
3. **Against a party who controls both the trail and the delivered documents:** closed by the seals (see below). The manifest binds the whole package; the OpenTimestamps anchor pins the manifest to a Bitcoin block (a regenerated package can only carry a young anchor), and the issuer signature says who issued it. An unsealed package still has only tiers 1–2, and `balise verify` says so on its face.

Two scope notes. The trail proves the **integrity of the record**, not the correctness of the findings: a finding wrong at write time is faithfully chained wrong. And the chain cannot prove a check was *never* recorded beyond the genesis count — completeness within a run is the genesis record's job; completeness across runs is the operator's.

## The package: manifest and `balise verify`

A full assessment ships as a **package**: the trail, the rapport, the sommaire, the `evidence/` archive, and `manifest.json` (`balise-assessment/1`) — the packing list, **written last**. The manifest carries the trail head and the SHA-256 of each post-close artifact's shipped bytes, plus a declared seal set. It lists the trail by head only (a file hash would be a second commitment to the same fact) and does not list `evidence/` (the chain is the index). It has no self-hash, and no artifact may reference it: the manifest's own hash is the package's single sealing surface, computed from its bytes by whatever seals or verifies it. The rapport prints the assessment id and the trail head; it never prints the manifest hash.

`balise verify <package-dir>` checks the whole package offline, outward-in: manifest → artifacts against their hashes → chain walk → trail head against the manifest → evidence archive against the chain-derived index → declared seals. Verdicts name the mechanism, never the conclusion:

| Verdict | Exit | Meaning |
|---|---|---|
| `SELF-CONSISTENT` | 0 | Every internal check passed. Printed with its stated limit: with no seals, indistinguishable from a wholesale regeneration. |
| `CHAIN-BROKEN` | 1 | The trail's integrity failed. |
| `ARTIFACT-DIVERGED` | 2 | An artifact does not match its commitment (report, sommaire, evidence file, or a trail that is not the listed one). |
| `SEAL-MISSING` / `SEAL-INVALID` | 3 | A declared seal is absent or fails. A stripped seal is a failure, never a silent downgrade. |
| `UNSUPPORTED-FORMAT` | 4 | Refusal to judge, not a verdict: no readable manifest of a known format. |

## Seals: closing tier 3

`balise seal <package-dir>` applies two seals to the manifest's exact shipped bytes, answering orthogonal questions:

- **The anchor** (OpenTimestamps) says *when*: the manifest digest is committed to Bitcoin via free public calendar servers — no wallet, no account, no service to operate. The proof starts *pending* and completes with `balise seal --upgrade` a few hours later, once Bitcoin has it (only the seals sidecar changes; the manifest is frozen from the first seal). A completed proof earns the `+ ANCHORED (block N)` rung. The anchor is the only seal the issuer cannot forge later, which is what finally closes tier 3: a regenerated package can only carry a *young* anchor.
- **The issuer signature** (Ed25519, detached) says *who*: the holder of the key issued this package, unchanged since signing. The verdict prints `+ SIGNED (key: <fingerprint>)` — the fingerprint, never a name: the key ships inside the package and is testimony; the recipient compares the printed fingerprint against [docs/SIGNING.md](SIGNING.md), a channel the package cannot rewrite. Neither seal replaces the other: a signature has no clock and can be redone by whoever holds the key; nobody can anchor a forgery into the past.

The seal declaration is written into the manifest before the first seal is applied (the declaration is part of the sealed bytes), so the declared set is frozen with everything else: stripping a seal yields `SEAL-MISSING`, and re-sealing under a substituted key changes the printed fingerprint. Key custody and the signing ritual are in [docs/SIGNING.md](SIGNING.md).
