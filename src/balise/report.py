"""Bilingual report builder + audit trail (the signature feature).

Every finding is rendered with its status, authority tier, legal hook,
evidence and reasoning — and the full machine-readable trail is written as
JSONL next to the report. French canonical, English mirror.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .advice import CLIENT_COPY
from .external import Finding
from .insurer import render_appendix
from .registry import (
    EVIDENCE_GRADE_LABELS,
    MODE_EVIDENCE_GRADE,
    STATUS_LABELS,
    Domain,
    Status,
    catalog_fingerprint,
)
from .semantic import SemanticEngine, prompt_fingerprint

DISCLAIMER_FR = (
    "> **Avis important** — Ce rapport est une autoévaluation de préparation "
    "produite par un outil automatisé. Il ne constitue pas un avis juridique, "
    "ne rend aucun verdict de conformité et ne remplace pas la consultation "
    "d'un professionnel du droit. Chaque constat indique le niveau d'autorité "
    "de sa base légale (LOI / CAI / INTERPRÉTATION)."
)
DISCLAIMER_EN = (
    "> **Important notice** — This report is a readiness self-assessment "
    "produced by an automated tool. It is not legal advice, renders no "
    "compliance verdict, and does not replace consulting a legal "
    "professional. Every finding states the authority tier of its legal "
    "basis (STATUTE / CAI / FIRM)."
)

DOMAIN_LABELS = {
    Domain.TRANSPARENCY: ("Transparence", "Transparency"),
    Domain.GOVERNANCE: ("Gouvernance", "Governance"),
    Domain.INCIDENTS: ("Incidents", "Incidents"),
    Domain.VENDORS_TRANSFERS: ("Fournisseurs et transferts", "Vendors & transfers"),
    Domain.SPECIAL_CATEGORIES: ("Catégories particulières", "Special categories"),
}

TIER_LABELS_FR = {"STATUTE": "LOI", "CAI": "CAI", "FIRM": "INTERPRÉTATION"}


@dataclass
class ReportPaths:
    report_md: Path
    audit_jsonl: Path
    head: str = ""     # final chain hash; printed in the deliverables


# Audit-trail format v1 — see docs/AUDIT-TRAIL.md. Field names and canonical
# form are FROZEN: hashes cover the field-name bytes, so any rename orphans
# every existing client trail.
TRAIL_FORMAT = "balise-audit-trail/1"
# Canonical form: sorted keys, compact separators, raw UTF-8, no floats
# anywhere in the schema (timestamps are strings for exactly this reason).
_CANONICAL = {"sort_keys": True, "separators": (",", ":"), "ensure_ascii": False}


def _eval_suite_fingerprint() -> str:
    """SHA-256 over the eval fixture pack and labels, or "none" when the
    suite is not alongside the package (installed outside the repo). The
    suite does not alter output, but genesis records which quality bar the
    producing tool was held to."""
    evals = Path(__file__).resolve().parents[2] / "evals"
    if not evals.is_dir():
        return "none"
    digest = hashlib.sha256()
    for path in sorted(p for p in evals.rglob("*")
                       if p.is_file() and "__pycache__" not in p.parts):
        digest.update(path.relative_to(evals).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _sealed(record: dict, prev: str | None) -> dict:
    record = {**record, "prev": prev}
    record["sha256"] = hashlib.sha256(
        json.dumps(record, **_CANONICAL).encode("utf-8")).hexdigest()
    return record


def _build_trail(findings: list[Finding], target: str) -> list[dict]:
    """Genesis + one sealed record per finding, hash-chained.

    The genesis record binds the chain to its engagement (target, date, tool)
    and declares the expected record count, so a truncated tail fails
    verification on its own — not only against the head in the report."""
    ordered = sorted(findings, key=_check_order)
    records = [_sealed({
        "format": TRAIL_FORMAT,
        "ts": datetime.now(UTC).isoformat(),
        "target": target,
        "tool": "balise 0.1.0",
        # producer provenance: every ingredient whose change alters output
        # must be visible in the record it produced — a silent model, prompt
        # or catalog change is otherwise indistinguishable from drift
        "engine": SemanticEngine.MODEL if SemanticEngine.configured() else "none",
        "prompt_sha256": prompt_fingerprint(),
        "catalog_sha256": catalog_fingerprint(),
        "eval_suite": _eval_suite_fingerprint(),
        "records": len(ordered),
    }, prev=None)]
    for finding in ordered:
        records.append(_sealed({
            "ts": datetime.now(UTC).isoformat(),
            "check": finding.check_id,
            "legal_hook": finding.check.legal_hook,
            "tier": finding.check.tier.value,
            "contested": finding.check.contested,
            "status": finding.status.value,
            "evidence_grade": MODE_EVIDENCE_GRADE[finding.check.mode].value,
            "evidence": finding.evidence,
            "reasoning": finding.reasoning,
            "reasoning_fr": finding.reasoning_fr,
        }, prev=records[-1]["sha256"]))
    return records


def _check_order(finding: Finding) -> tuple[str, int]:
    """Natural order: A1..A10 then B1..B18 (never A1, A10, A2)."""
    check_id = finding.check_id
    return (check_id[0], int(check_id[1:]))


def _posture_line(findings: list[Finding], domain: Domain, lang: str) -> str:
    relevant = [f for f in findings if f.check.domain == domain]
    if not relevant:
        return ""
    counts: dict[Status, int] = {}
    for finding in relevant:
        counts[finding.status] = counts.get(finding.status, 0) + 1
    idx = 0 if lang == "fr" else 1
    parts = [f"{STATUS_LABELS[status][idx]}: {n}" for status, n in counts.items()]
    return f"**{DOMAIN_LABELS[domain][idx]}** — " + ", ".join(parts)


def _exec_summary(findings: list[Finding], lang: str) -> list[str]:
    """The 'if you read one paragraph' opener: status counts and the top
    priorities, in the owner's language. Derived from the same authored copy
    as the visual summary so the two never disagree."""
    idx = 0 if lang == "fr" else 1
    title = ("Si vous ne lisez qu'un paragraphe" if lang == "fr"
             else "If you read only one paragraph")
    counts = {status: sum(1 for f in findings if f.status is status)
              for status in Status}
    total = len(findings)
    count_parts = [f"{STATUS_LABELS[status][idx]} {n}"
                   for status, n in counts.items() if n]
    points_label = ("points vérifiés" if lang == "fr" else "points assessed")
    lines = [f"## {title}", "",
             f"**{total} {points_label}** : " + " · ".join(count_parts) + ".", ""]

    gaps = [f for f in findings
            if f.status in (Status.NOT_MET, Status.PARTIAL)
            and f.check_id in CLIENT_COPY]
    gaps.sort(key=lambda f: (CLIENT_COPY[f.check_id].priority, _check_order(f)))
    if gaps:
        lines.append("**Priorités :**" if lang == "fr" else "**Priorities:**")
        for rank, finding in enumerate(gaps[:3], start=1):
            copy = CLIENT_COPY[finding.check_id]
            plain = copy.plain_fr if lang == "fr" else copy.plain_en
            action = copy.action_fr if lang == "fr" else copy.action_en
            lines.append(f"{rank}. **{plain}.** {action}")
        lines.append("")
    else:
        lines.extend([("Aucune lacune prioritaire relevée par cette évaluation."
                       if lang == "fr"
                       else "No priority gap identified by this assessment."), ""])

    if counts.get(Status.UNKNOWN):
        lines.extend([("Un constat « Indéterminé » est un point à clarifier "
                       "ensemble, pas un échec." if lang == "fr"
                       else "An 'Unknown' finding is a point to clarify "
                       "together, not a failure."), ""])
    return lines


def _render_finding(finding: Finding, lang: str) -> str:
    check = finding.check
    idx = 0 if lang == "fr" else 1
    tier = TIER_LABELS_FR[check.tier.value] if lang == "fr" else check.tier.value
    title = check.title_fr if lang == "fr" else check.title_en
    lines = [
        f"### {check.id} — {title}",
        "",
        f"- **{'Statut' if lang == 'fr' else 'Status'}:** {STATUS_LABELS[finding.status][idx]}",
        f"- **{'Base légale' if lang == 'fr' else 'Legal basis'}:** {check.legal_hook} "
        f"[{tier}]" + (" *(interprétation contestée)*" if check.contested and lang == "fr"
                       else " *(contested interpretation)*" if check.contested else ""),
        f"- **{'Nature de la preuve' if lang == 'fr' else 'Evidence basis'}:** "
        f"{EVIDENCE_GRADE_LABELS[MODE_EVIDENCE_GRADE[check.mode]][idx]}",
    ]
    if finding.evidence:
        label = "Éléments observés" if lang == "fr" else "Evidence"
        lines.append(f"- **{label}:**")
        lines.extend(f"  - {item}" for item in finding.evidence)
    # Registry notes are operator context (verification history, market framing)
    # and are never rendered into the client-facing report.
    reasoning = (finding.reasoning_fr or finding.reasoning) if lang == "fr" \
        else (finding.reasoning or finding.reasoning_fr)
    if reasoning:
        label = "Raisonnement" if lang == "fr" else "Reasoning"
        lines.append(f"- **{label}:** {reasoning}")
    lines.append("")
    return "\n".join(lines)


def _integrity_block(head: str, lang: str) -> list[str]:
    if lang == "fr":
        text = ("**Intégrité** : cette évaluation est scellée par une piste "
                "d'audit chaînée (chaque enregistrement contient l'empreinte "
                "du précédent). Empreinte finale (SHA-256) : `" + head + "`. "
                "Une piste dont l'empreinte finale diffère ne correspond pas "
                "à ce rapport.")
    else:
        text = ("**Integrity**: this assessment is sealed by a hash-chained "
                "audit trail (each record contains the previous record's "
                "fingerprint). Final fingerprint (SHA-256): `" + head + "`. "
                "A trail whose final fingerprint differs does not correspond "
                "to this report.")
    return ["", "---", "", text, ""]


def _render_language_section(findings: list[Finding], target: str, lang: str,
                             notices: list[tuple[str, str]],
                             head: str = "") -> str:
    title = ("Rapport de préparation — Loi 25" if lang == "fr"
             else "Law 25 Readiness Report")
    disclaimer = DISCLAIMER_FR if lang == "fr" else DISCLAIMER_EN
    posture_title = "Posture par domaine" if lang == "fr" else "Posture by domain"
    findings_title = "Constats" if lang == "fr" else "Findings"
    lines = [f"# {title}", "", f"**Site:** {target}",
             f"**Date:** {datetime.now(UTC).date().isoformat()}", "",
             disclaimer, ""]
    for notice_fr, notice_en in notices:
        lines.extend([f"> ⚠️ **{notice_fr if lang == 'fr' else notice_en}**", ""])
    lines.extend(_exec_summary(findings, lang))
    lines.extend([f"## {posture_title}", ""])
    for domain in Domain:
        line = _posture_line(findings, domain, lang)
        if line:
            lines.append(f"- {line}")
    lines.extend(["", f"## {findings_title}", ""])
    for finding in sorted(findings, key=_check_order):
        lines.append(_render_finding(finding, lang))
    lines.extend(["", render_appendix(findings, lang)])
    if head:
        lines.extend(_integrity_block(head, lang))
    return "\n".join(lines)


def write_report(findings: list[Finding], target: str, out_dir: str | Path,
                 notices: list[tuple[str, str]] | None = None) -> ReportPaths:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    notices = notices or []

    # Trail first: its head is printed in the report body, making the
    # delivered document itself the head record — a truncated or regenerated
    # trail contradicts the paper in the client's hands.
    trail = _build_trail(findings, target)
    head = trail[-1]["sha256"]
    audit_path = out / "audit-trail.jsonl"
    with audit_path.open("w", encoding="utf-8") as handle:
        for record in trail:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    body = (_render_language_section(findings, target, "fr", notices, head)
            + "\n\n---\n\n"
            + _render_language_section(findings, target, "en", notices, head))
    report_path = out / "rapport-balise.md"
    report_path.write_text(body, encoding="utf-8")
    return ReportPaths(report_md=report_path, audit_jsonl=audit_path, head=head)


def verify_audit_trail(path: str | Path, expect_head: str | None = None) -> bool:
    """True iff the chain is internally intact AND complete.

    Catches (tier 1, unconditional): any edited field, deleted or reordered
    record, and a truncated tail — the genesis record declares the expected
    record count. Catches (tier 2): wholesale regeneration, but ONLY when
    `expect_head` is supplied from outside the file — in practice, the
    fingerprint printed in the delivered report. Without an external head or
    anchor, a regenerated chain is indistinguishable from an honest one."""
    records = [json.loads(line) for line
               in Path(path).read_text(encoding="utf-8").splitlines()
               if line.strip()]
    if not records:
        return False
    prev = None
    for record in records:
        claimed = record.pop("sha256", None)
        if record.get("prev") != prev:
            return False
        recomputed = hashlib.sha256(
            json.dumps(record, **_CANONICAL).encode("utf-8")).hexdigest()
        if recomputed != claimed:
            return False
        prev = claimed
    genesis = records[0]
    if genesis.get("format") != TRAIL_FORMAT:
        return False
    if genesis.get("records") != len(records) - 1:
        return False
    if expect_head is not None and prev != expect_head:
        return False
    return True
