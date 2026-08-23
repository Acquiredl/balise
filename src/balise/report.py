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

from .external import Finding
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


def _render_language_section(findings: list[Finding], target: str, lang: str) -> str:
    title = ("Rapport de préparation — Loi 25" if lang == "fr"
             else "Law 25 Readiness Report")
    disclaimer = DISCLAIMER_FR if lang == "fr" else DISCLAIMER_EN
    posture_title = "Posture par domaine" if lang == "fr" else "Posture by domain"
    findings_title = "Constats" if lang == "fr" else "Findings"
    lines = [f"# {title}", "", f"**{'Site' if lang == 'fr' else 'Site'}:** {target}",
             f"**Date:** {datetime.now(timezone.utc).date().isoformat()}", "",
             disclaimer, "", f"## {posture_title}", ""]
    for domain in Domain:
        line = _posture_line(findings, domain, lang)
        if line:
            lines.append(f"- {line}")
    lines.extend(["", f"## {findings_title}", ""])
    for finding in sorted(findings, key=lambda f: f.check_id):
        lines.append(_render_finding(finding, lang))
    return "\n".join(lines)


def write_report(findings: list[Finding], target: str, out_dir: str | Path) -> ReportPaths:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    body = (_render_language_section(findings, target, "fr")
            + "\n\n---\n\n"
            + _render_language_section(findings, target, "en"))

    audit_path = out / "audit-trail.jsonl"
    with audit_path.open("w", encoding="utf-8") as handle:
        for finding in sorted(findings, key=lambda f: f.check_id):
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
            }
            record["sha256"] = hashlib.sha256(
                json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    report_path = out / "rapport-balise.md"
    report_path.write_text(body, encoding="utf-8")
    return ReportPaths(report_md=report_path, audit_jsonl=audit_path)
