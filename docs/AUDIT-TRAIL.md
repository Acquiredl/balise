# Audit trail — format and guarantees (v1)

The audit trail is the engagement's machine-readable record: one JSONL file, hash-chained, from which the rapport and sommaire can be regenerated without rescanning. This document freezes the format and states exactly what verification does and does not prove.

## Format: `balise-audit-trail/1`

Line 1 is the **genesis record**; every following line is one **finding record**. Field names are **frozen**: hashes cover the field-name bytes, so renaming any field orphans every existing trail.

Genesis record fields: `format`, `ts`, `target`, `tool`, `records` (the exact number of finding records that follow), `prev` (always `null`), `sha256`.

Finding record fields: `ts`, `check`, `legal_hook`, `tier`, `contested`, `status`, `evidence`, `reasoning`, `reasoning_fr`, `prev` (the previous record's `sha256`), `sha256`.

## Canonical form

`sha256` is SHA-256 over the record's canonical JSON, minus the `sha256` field itself:

1. Keys sorted lexicographically.
2. Compact separators: `,` and `:`, no whitespace.
3. Raw UTF-8 (no ASCII escaping), no trailing newline.
4. No floats anywhere in the schema — timestamps are strings for exactly this reason (float serialization is not portable).

In Python: `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`. The rules are normative; the Python idiom is not.

## Verification (`report.verify_audit_trail`)

Walks the file once and checks: each record's recomputed canonical hash equals its stored `sha256`; each record's `prev` equals the previous record's hash (genesis: `null`); the genesis `format` matches; and the genesis `records` count equals the number of finding records present.

## Guarantee tiers — stated honestly

1. **Unconditional (the file alone):** any edited field, deleted record, reordering, or truncated tail is detected. Truncation is caught by the genesis record count.
2. **Against the delivered report:** the trail's final hash (its *head*) is printed in the rapport and the sommaire. A wholesale-regenerated trail verifies internally, but its head will not match the fingerprint in the documents the client holds — the deliverable itself is the head record. Pass that fingerprint as `expect_head` to check this tier.
3. **Not provided (yet):** proof against a party who controls *both* the trail and the delivered documents before delivery. Closing that requires anchoring the head in an external, append-only system at delivery time (e.g., an OpenTimestamps commitment). Deliberately deferred; revisit when a client dispute scenario makes it worth the operational cost.

Two scope notes. The trail proves the **integrity of the record**, not the correctness of the findings: a finding wrong at write time is faithfully chained wrong. And the chain cannot prove a check was *never* recorded beyond the genesis count — completeness within a run is the genesis record's job; completeness across runs is the operator's.
