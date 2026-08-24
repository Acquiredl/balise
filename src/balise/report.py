"""Bilingual report builder + audit trail (the signature feature).

Every finding is rendered with its status, authority tier, legal hook,
evidence and reasoning — and the full machine-readable trail is written as
JSONL next to the report. French canonical, English mirror.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .advice import CLIENT_COPY
from .external import Finding
from .insurer import render_appendix
from .registry import Domain, Status

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

STATUS_LABELS = {
    Status.MET: ("Atteint", "Met"),
    Status.PARTIAL: ("Partiel", "Partial"),
    Status.NOT_MET: ("Non atteint", "Not met"),
    Status.NOT_APPLICABLE: ("Sans objet", "Not applicable"),
    Status.UNKNOWN: ("Indéterminé", "Unknown"),
}

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


def _render_language_section(findings: list[Finding], target: str, lang: str,
                             notices: list[tuple[str, str]]) -> str:
    title = ("Rapport de préparation — Loi 25" if lang == "fr"
             else "Law 25 Readiness Report")
    disclaimer = DISCLAIMER_FR if lang == "fr" else DISCLAIMER_EN
    posture_title = "Posture par domaine" if lang == "fr" else "Posture by domain"
    findings_title = "Constats" if lang == "fr" else "Findings"
    lines = [f"# {title}", "", f"**{'Site' if lang == 'fr' else 'Site'}:** {target}",
             f"**Date:** {datetime.now(timezone.utc).date().isoformat()}", "",
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
    return "\n".join(lines)


def write_report(findings: list[Finding], target: str, out_dir: str | Path,
                 notices: list[tuple[str, str]] | None = None) -> ReportPaths:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    notices = notices or []
    body = (_render_language_section(findings, target, "fr", notices)
            + "\n\n---\n\n"
            + _render_language_section(findings, target, "en", notices))

    audit_path = out / "audit-trail.jsonl"
    with audit_path.open("w", encoding="utf-8") as handle:
        # Hash chain: each record carries the previous record's hash inside
        # its own hashed content, so deleting or reordering ANY record breaks
        # every hash after it. "Records are intact" becomes "the trail is
        # intact" — the property the product's positioning rests on.
        prev_hash = "genesis"
        for finding in sorted(findings, key=_check_order):
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "check": finding.check_id,
                "legal_hook": finding.check.legal_hook,
                "tier": finding.check.tier.value,
                "contested": finding.check.contested,
                "status": finding.status.value,
                "evidence": finding.evidence,
                "reasoning": finding.reasoning,
                "reasoning_fr": finding.reasoning_fr,
                "prev": prev_hash,
            }
            record["sha256"] = hashlib.sha256(
                json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            prev_hash = record["sha256"]
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    report_path = out / "rapport-balise.md"
    report_path.write_text(body, encoding="utf-8")
    return ReportPaths(report_md=report_path, audit_jsonl=audit_path)


def verify_audit_trail(path: str | Path) -> bool:
    """True iff every record's hash validates AND the prev-chain is unbroken.

    A single edited field, a deleted record, or a reordering anywhere in the
    file returns False."""
    prev = "genesis"
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        claimed = record.pop("sha256", None)
        if record.get("prev") != prev:
            return False
        recomputed = hashlib.sha256(
            json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        if recomputed != claimed:
            return False
        prev = claimed
    return True
