"""Package verification: three mechanical steps, outward-in.

Check the manifest, check each artifact against it, walk the chain —
then derive the expected evidence archive from the trail itself (the
chain is the index) and compare. Verdicts name the mechanism, never the
conclusion: the top verdict here is SELF-CONSISTENT, printed with its
stated limit, because an unsealed package is indistinguishable from a
wholesale regeneration. Words like "authentic" or "verified" are
deliberately absent from this output.

Verdict ladder and exit codes (this package's mapping):
    0  SELF-CONSISTENT      every internal check passed
    1  CHAIN-BROKEN         the trail's integrity failed
    2  ARTIFACT-DIVERGED    an artifact does not match its commitment
    3  SEAL-MISSING / SEAL-INVALID   a declared seal is absent or fails
    4  UNSUPPORTED-FORMAT   refusal to judge, not a verdict
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import seal as seal_mod
from .report import MANIFEST_FORMAT, verify_audit_trail

_LIMIT_NOTE = ("no seals declared: internal consistency only — "
               "indistinguishable from a wholesale regeneration")


@dataclass
class Check:
    label: str
    ok: bool
    detail: str = ""


@dataclass
class PackageVerdict:
    verdict: str
    exit_code: int
    checks: list[Check] = field(default_factory=list)

    def render(self) -> str:
        lines = ["BALISE PACKAGE VERIFICATION",
                 "-" * 40]
        for check in self.checks:
            mark = "ok " if check.ok else "FAIL"
            detail = f"  ({check.detail})" if check.detail else ""
            lines.append(f"  [{mark:4}] {check.label}{detail}")
        lines.append("-" * 40)
        lines.append(f"RESULT: {self.verdict}")
        return "\n".join(lines)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_package(package_dir: str | Path) -> PackageVerdict:
    package = Path(package_dir)
    checks: list[Check] = []

    # 1. The manifest is the entry point; without a readable one there is
    # nothing to judge against — a refusal, not a verdict.
    manifest_path = package / "manifest.json"
    if not manifest_path.is_file():
        return PackageVerdict("UNSUPPORTED-FORMAT", 4,
                              [Check("manifest present", False,
                                     "manifest.json not found")])
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return PackageVerdict("UNSUPPORTED-FORMAT", 4,
                              [Check("manifest readable", False,
                                     "manifest.json is not valid JSON")])
    if manifest.get("format") != MANIFEST_FORMAT:
        return PackageVerdict("UNSUPPORTED-FORMAT", 4,
                              [Check("manifest format", False,
                                     f"unknown format {manifest.get('format')!r}")])
    checks.append(Check("manifest", True, manifest.get("assessment_id", "")))

    chain_broken = False
    diverged = False

    # 2. Every listed artifact must match the hash of its shipped bytes.
    for name, digest in manifest.get("artifacts", {}).items():
        path = package / name
        if not path.is_file():
            checks.append(Check(f"artifact {name}", False, "missing"))
            diverged = True
        elif _sha256_file(path) != digest:
            checks.append(Check(f"artifact {name}", False, "hash mismatch"))
            diverged = True
        else:
            checks.append(Check(f"artifact {name}", True))

    # 3. The trail: walk the chain, then hold its head against the manifest.
    trail_path = package / "audit-trail.jsonl"
    records: list[dict] = []
    if not trail_path.is_file():
        checks.append(Check("trail present", False, "audit-trail.jsonl missing"))
        chain_broken = True
    elif not verify_audit_trail(trail_path):
        checks.append(Check("chain integrity", False))
        chain_broken = True
    else:
        checks.append(Check("chain integrity", True))
        records = [json.loads(line) for line
                   in trail_path.read_text(encoding="utf-8").splitlines()
                   if line.strip()]
        head = records[-1]["sha256"]
        if head != manifest.get("trail_head"):
            checks.append(Check("trail head vs manifest", False,
                                "the trail is not the listed one"))
            diverged = True
        else:
            checks.append(Check("trail head vs manifest", True))

    # 4. The chain is the evidence index: the archive must contain exactly
    # the referenced set, each file matching the name it carries.
    expected = {ref["sha256"] for record in records
                for ref in record.get("sources", [])}
    evidence_dir = package / "evidence"
    actual = ({p.name: p for p in evidence_dir.iterdir()}
              if evidence_dir.is_dir() else {})
    evidence_ok = True
    for digest in sorted(expected):
        name = f"{digest}.html"
        if name not in actual:
            checks.append(Check(f"evidence {digest[:12]}…", False, "missing"))
            evidence_ok = False
            diverged = True
        elif _sha256_file(actual[name]) != digest:
            checks.append(Check(f"evidence {digest[:12]}…", False,
                                "hash mismatch"))
            evidence_ok = False
            diverged = True
    for name in sorted(actual):
        if name.removesuffix(".html") not in expected:
            checks.append(Check(f"evidence {name[:12]}…", False,
                                "not referenced by any finding"))
            evidence_ok = False
            diverged = True
    if evidence_ok:
        checks.append(Check("evidence archive",
                            True, f"{len(expected)} file(s), exact set"))

    # 5. Declared seals: a declared-but-absent seal is a failure, never a
    # silent downgrade. Each valid seal adds its rung to the verdict; a
    # pending anchor is judged honestly (submitted, not yet attested) and
    # earns no rung. The signature rung prints the key's fingerprint and
    # never a name: comparing it against an out-of-band channel is the
    # recipient's job.
    seal_missing = seal_invalid = False
    rungs = []
    declared = manifest.get("seals", [])
    for kind in declared:
        if kind == "ed25519":
            state, detail = seal_mod.judge_signature(package)
            if state == "valid":
                checks.append(Check("seal ed25519", True,
                                    f"key {detail[:16]}…"))
                rungs.append(f"SIGNED (key: {detail[:16]}…)")
            elif state == "missing":
                checks.append(Check("seal ed25519", False, detail))
                seal_missing = True
            else:
                checks.append(Check("seal ed25519", False, detail))
                seal_invalid = True
        elif kind == "anchor":
            state, detail = seal_mod.judge_anchors(package)
            if state == "bitcoin":
                checks.append(Check("seal anchor", True, detail))
                rungs.append(f"ANCHORED ({detail})")
            elif state == "pending":
                checks.append(Check("seal anchor", True, detail))
            elif state == "missing":
                checks.append(Check("seal anchor", False, detail))
                seal_missing = True
            else:
                checks.append(Check("seal anchor", False, detail))
                seal_invalid = True
        else:
            checks.append(Check(f"seal {kind}", False,
                                "unknown seal kind — cannot judge"))
            seal_invalid = True
    if not declared:
        checks.append(Check("seals", True, _LIMIT_NOTE))

    if chain_broken:
        return PackageVerdict("CHAIN-BROKEN", 1, checks)
    if diverged:
        return PackageVerdict("ARTIFACT-DIVERGED", 2, checks)
    if seal_invalid:
        return PackageVerdict("SEAL-INVALID", 3, checks)
    if seal_missing:
        return PackageVerdict("SEAL-MISSING", 3, checks)
    verdict = " + ".join(["SELF-CONSISTENT", *rungs])
    return PackageVerdict(verdict, 0, checks)
