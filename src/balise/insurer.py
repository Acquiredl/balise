"""Insurer appendix — findings mapped to cyber-insurance application themes.

Grounded in four application forms read end to end on 2026-08-23 (CFC Canada,
Northbridge Canada, Beazley short form, Chubb/ACE long form): revenue and
headcount set the base premium; a short list of controls gates eligibility
and discounts. The appendix maps what Balise assesses onto those recurring
themes so the owner can answer their broker from the report — and says
plainly which insurer questions Balise does NOT assess.
"""

from __future__ import annotations

from dataclasses import dataclass

from .external import Finding
from .registry import STATUS_LABELS as _STATUS_LABELS


@dataclass(frozen=True)
class Theme:
    title_fr: str
    title_en: str
    asks_fr: str      # where/how insurers ask about this
    asks_en: str
    check_ids: tuple[str, ...]


THEMES: tuple[Theme, ...] = (
    Theme("Authentification multifacteur (MFA)",
          "Multi-factor authentication (MFA)",
          "Question obligatoire des formulaires courts (condition d'admissibilité).",
          "Mandatory question on short-form applications (eligibility condition).",
          ("B19",)),
    Theme("Copies de sauvegarde hors ligne, testées",
          "Offline, tested backups",
          "Question obligatoire des formulaires courts (condition d'admissibilité).",
          "Mandatory question on short-form applications (eligibility condition).",
          ("B20",)),
    Theme("Formation et sensibilisation du personnel",
          "Staff security and privacy training",
          "Question obligatoire ou à rabais sur la plupart des formulaires.",
          "Mandatory or discount-earning question on most applications.",
          ("B11",)),
    Theme("Plan de réponse et registre des incidents",
          "Incident response plan and register",
          "Tous les formulaires exigent l'historique des violations (3 à 5 ans); "
          "un registre d'incidents tenu à jour y répond directement.",
          "Every form requires 3-5 years of breach history; a maintained "
          "incident register answers it directly.",
          ("B1",)),
    Theme("Politique de confidentialité documentée",
          "Documented privacy policy",
          "Formulaires détaillés et suivis de souscription; l'assureur peut "
          "demander la politique elle-même.",
          "Fuller applications and underwriting follow-ups; the insurer may "
          "request the policy itself.",
          ("A1", "A2")),
    Theme("Responsable désigné (sécurité et vie privée)",
          "Designated individual (security and privacy)",
          "Formulaires détaillés (personne désignée pour la vie privée).",
          "Fuller applications (designated privacy individual).",
          ("A3",)),
    Theme("Gestion des fournisseurs et des tiers",
          "Vendor and third-party management",
          "Formulaires courts (liste des fournisseurs TI critiques) et détaillés "
          "(revues annuelles, preuve d'assurance des fournisseurs).",
          "Short forms (critical IT vendor list) and fuller forms (annual "
          "reviews, proof of vendors' own coverage).",
          ("B3", "B4")),
    Theme("Conservation, destruction et demandes d'accès",
          "Retention, disposal and access requests",
          "Formulaires détaillés (politique de conservation, destruction "
          "sécurisée, procédures de demandes d'accès).",
          "Fuller applications (retention policy, secure disposal, "
          "access-request procedures).",
          ("B5", "B14", "B16")),
    Theme("Mesures de sécurité générales (art. 10)",
          "General security safeguards (s. 10)",
          "Trame de fond de toutes les questions techniques des formulaires.",
          "The backdrop of every technical question on the forms.",
          ("B12",)),
)

_NOT_ASSESSED_FR = (
    "Balise n'évalue pas les contrôles purement techniques que les "
    "formulaires détaillés peuvent aussi demander (chiffrement, EDR, gestion "
    "des correctifs, tests d'intrusion, etc.) : indiquez « non évalué par cet "
    "outil » et répondez-y avec votre fournisseur TI."
)
_NOT_ASSESSED_EN = (
    "Balise does not assess the purely technical controls fuller applications "
    "may also ask about (encryption, EDR, patch management, penetration "
    "testing, etc.): mark those \"not assessed by this tool\" and answer them "
    "with your IT provider."
)

_INTRO_FR = (
    "Les demandes d'assurance cyber s'ouvrent sur le chiffre d'affaires et le "
    "nombre d'employés; les contrôles ci-dessous déterminent ensuite "
    "l'admissibilité et les rabais. Les éléments de gouvernance (politique, "
    "responsable, conservation) figurent surtout sur les formulaires détaillés "
    "et les suivis de souscription — pas sur tous les formulaires courts. Ce "
    "tableau relie vos constats Balise à ces thèmes récurrents; chaque statut "
    "renvoie au constat complet et à sa preuve dans le rapport."
)
_INTRO_EN = (
    "Cyber-insurance applications open with revenue and employee count; the "
    "controls below then determine eligibility and discounts. Governance items "
    "(policy, designated officer, retention) appear chiefly on fuller "
    "applications and underwriting follow-ups — not on every short form. This "
    "table links your Balise findings to those recurring themes; each status "
    "points back to the full finding and its evidence in the report."
)


def render_appendix(findings: list[Finding], lang: str) -> str:
    idx = 0 if lang == "fr" else 1
    by_check = {f.check_id: f for f in findings}
    title = ("Annexe — Préparer une demande d'assurance cyber" if lang == "fr"
             else "Appendix — Preparing a cyber-insurance application")
    theme_h = "Thème du questionnaire" if lang == "fr" else "Application theme"
    asks_h = "Où les assureurs le demandent" if lang == "fr" else "Where insurers ask"
    status_h = "Vos constats" if lang == "fr" else "Your findings"
    lines = [f"## {title}", "",
             _INTRO_FR if lang == "fr" else _INTRO_EN, "",
             f"| {theme_h} | {asks_h} | {status_h} |",
             "|---|---|---|"]
    for theme in THEMES:
        cells = []
        for check_id in theme.check_ids:
            finding = by_check.get(check_id)
            if finding is None:
                continue
            cells.append(f"{check_id} : {_STATUS_LABELS[finding.status][idx]}")
        if not cells:
            continue
        lines.append(f"| {theme.title_fr if lang == 'fr' else theme.title_en} "
                     f"| {theme.asks_fr if lang == 'fr' else theme.asks_en} "
                     f"| {' · '.join(cells)} |")
    lines.extend(["", f"> {_NOT_ASSESSED_FR if lang == 'fr' else _NOT_ASSESSED_EN}", ""])
    return "\n".join(lines)
