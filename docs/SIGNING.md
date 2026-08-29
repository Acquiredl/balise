# Issuer signing key — fingerprint and custody

This page is the canonical out-of-band channel for the Balise issuer key: the one place a package cannot rewrite. A recipient runs `balise verify` on their package, reads the fingerprint it prints, and compares it against this page. The verifier's job is the math; this comparison is the recipient's job — the tool prints `SIGNED (key: …)` and never a name, because a key inside a package proves nothing about who holds it.

## Current fingerprint

| Fingerprint (SHA-256 of the public key) | In service since | Status |
|---|---|---|
| `81cf985bb660ed055dbed21f9d0ab7877910190945b7d7d4d63124651108e6b3` | 2026-08-25 | active |

Fingerprints are **never removed** from this table: packages outlive keys, and a package from year one must still be checkable against year one's fingerprint. Rotation happens on need (compromise or loss), not on a calendar. A compromise notice, if ever needed, appears here with a date fence: packages carrying an anchor from before that date remain defensible — a stolen key can sign a forgery, but no one can anchor a forgery into the past.

## What the signature claims

> This manifest — and transitively every artifact it lists — was issued by the holder of key K and has not changed since signing.

Nothing more. It does not claim the package is the only version ever issued (ordering in time comes from the anchor), does not claim the findings are correct, and does not by itself bind the key to a name — that binding is this page.

## Custody (operator side)

The private key lives in the operator's password manager and nowhere else — never on disk, never in a repo, never on the machine the assessment pipeline runs on, out of reach of any process the trail records. The ritual:

1. **Once:** `balise keygen` — the private key is printed a single time and written nowhere. Store it in the password manager; publish the fingerprint here; close the terminal.
2. **Per assessment:** run the pipeline, then `balise seal <package-dir>` — paste the key at the prompt (it is read without echo, held in memory for the duration of one signature, and never written). The command also anchors the manifest via OpenTimestamps.
3. **A few hours later:** `balise seal <package-dir> --upgrade` completes the anchor once Bitcoin has it. This touches only the seals sidecar; the sealed manifest is never modified.

The seal declaration is part of the sealed bytes: `balise seal` declares the full seal set before applying anything, so a stripped seal shows up as `SEAL-MISSING` on verification, never as a silent downgrade.
