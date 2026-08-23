"""Check catalog — the assessment methodology as data.

Every check traces to a legal hook and carries an authority tier (ADR 0001).
Statutory references are triangulated, not yet human-verified against
LegisQuebec: docs/VERIFICATION.md gates client-facing use.
"""

from dataclasses import dataclass
from enum import Enum


class Tier(str, Enum):
    STATUTE = "STATUTE"  # explicit text of CQLR c. P-39.1 or LCCJTI
    CAI = "CAI"          # regulator guidance/expectation
    FIRM = "FIRM"        # convergent law-firm interpretation, unsettled


class Mode(str, Enum):
    DETERMINISTIC = "deterministic"
    SEMANTIC = "semantic"
    INTAKE = "intake"


class Domain(str, Enum):
    TRANSPARENCY = "transparency"
    GOVERNANCE = "governance"
    INCIDENTS = "incidents"
    VENDORS_TRANSFERS = "vendors_transfers"
    SPECIAL_CATEGORIES = "special_categories"


class Status(str, Enum):
    MET = "met"
    PARTIAL = "partial"
    NOT_MET = "not_met"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Check:
    id: str
    module: str               # "A" (external scan) or "B" (intake)
    domain: Domain
    mode: Mode
    tier: Tier
    legal_hook: str           # statutory section / guidance document
    title_fr: str
    title_en: str
    contested: bool = False   # tier is argued, not settled — reports must say so
    note: str = ""


CHECKS: tuple[Check, ...] = (
    # ---- Module A: external scan -------------------------------------------
    Check("A1", "A", Domain.TRANSPARENCY, Mode.DETERMINISTIC, Tier.STATUTE, "s. 8.2",
          "Politique de confidentialité publiée sur le site web",
          "Privacy policy published on the website"),
    Check("A2", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "ss. 8, 8.2 + guide CAI",
          "Politique en termes simples et clairs, couvrant fins, droits, tiers et communication hors Québec",
          "Policy in clear and plain language, covering purposes, rights, third parties and communication outside Quebec"),
    Check("A3", "A", Domain.GOVERNANCE, Mode.DETERMINISTIC, Tier.STATUTE, "s. 3.1",
          "Titre et coordonnées du responsable de la protection des renseignements personnels publiés",
          "Privacy officer title and contact information published"),
    Check("A4", "A", Domain.GOVERNANCE, Mode.SEMANTIC, Tier.STATUTE, "s. 3.2",
          "Information détaillée sur les politiques de gouvernance publiée",
          "Detailed information about governance policies published"),
    Check("A5", "A", Domain.TRANSPARENCY, Mode.DETERMINISTIC, Tier.CAI,
          "s. 8.1 + Lignes directrices 2023-1",
          "Témoins non essentiels inactifs avant consentement; bannière avec refus accessible",
          "Non-essential trackers inactive before consent; banner with accessible refusal",
          contested=True,
          note="Opt-in rests on CAI guidance; s. 9.1 excludes browser cookies from "
               "privacy-by-default. Reported as regulator expectation, not settled statute."),
    Check("A6", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 8.1",
          "Technologies de repérage, localisation ou profilage divulguées, avec moyens d'activation",
          "Tracking, locating or profiling technology disclosed, with means of activation"),
    Check("A7", "A", Domain.TRANSPARENCY, Mode.DETERMINISTIC, Tier.FIRM,
          "Charte de la langue française, art. 52, 55",
          "Version française du site, de la politique et des conditions (français d'abord pour les contrats d'adhésion)",
          "French version of site, policy and terms (French-first for adhesion contracts)",
          contested=True,
          note="Policies-in-scope of s. 52 is convergent firm interpretation. Dual exposure: "
               "Law 25 plain-language + OQLF ($3k-$30k per offence)."),
    Check("A8", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 14",
          "Formulaires : consentement par finalité, en termes clairs, demandé distinctement",
          "Forms: purpose-granular consent, in clear language, requested separately"),
    Check("A9", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 8.2",
          "Pratique d'avis de modification de la politique",
          "Policy amendment-notice practice"),
    # ---- Module B: intake --------------------------------------------------
    Check("B1", "B", Domain.INCIDENTS, Mode.INTAKE, Tier.STATUTE,
          "ss. 3.5-3.8 + Règlement sur les incidents",
          "Registre des incidents de confidentialité (8 éléments prescrits, conservation 5 ans) et processus de réponse",
          "Confidentiality-incident register (8 prescribed elements, 5-year retention) and response process",
          note="Notification standard is 'with diligence' — there is NO 72-hour statutory "
               "deadline (that figure is GDPR, not Quebec)."),
    Check("B2", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 3.3",
          "EFVP pour tout système d'information acquis, développé ou refondu impliquant des RP",
          "PIA for any acquired, developed or overhauled information system involving PI"),
    Check("B3", "B", Domain.VENDORS_TRANSFERS, Mode.INTAKE, Tier.STATUTE, "s. 17",
          "EFVP et entente écrite pour toute communication hors Québec (incluant chaque SaaS hébergé aux É.-U.)",
          "PIA and written agreement for any communication outside Quebec (including every US-hosted SaaS)",
          note="No adequacy whitelist exists; analysis depth is a proportionality judgment "
               "(FIRM-level methodology). Empirically the biggest unmet paper obligation."),
    Check("B4", "B", Domain.VENDORS_TRANSFERS, Mode.INTAKE, Tier.STATUTE, "s. 18.3",
          "Contrats écrits avec les mandataires et fournisseurs de services",
          "Written contracts with mandataries and service providers"),
    Check("B5", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 3.2",
          "Politiques internes : rôles du cycle de vie, conservation/destruction, traitement des plaintes",
          "Internal policies: lifecycle roles, retention/destruction, complaint handling"),
    Check("B6", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.STATUTE, "LCCJTI, art. 44-45",
          "Systèmes biométriques : consentement exprès et déclaration à la CAI 60 jours avant la mise en service",
          "Biometric systems: express consent and CAI declaration 60 days before service",
          note="The CAI's only active enforcement area (Transcontinental 2024, Metro 2025 — "
               "cease/destroy orders). Highest-yield intake question."),
    Check("B7", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.STATUTE, "s. 12.1",
          "Décisions fondées exclusivement sur un traitement automatisé : information et droit de faire des observations",
          "Decisions based exclusively on automated processing: disclosure and right to submit observations"),
    Check("B8", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.STATUTE, "s. 4.1",
          "Mineurs de moins de 14 ans : consentement du titulaire de l'autorité parentale",
          "Minors under 14: consent of the holder of parental authority"),
    Check("B9", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 27",
          "Traitement des demandes de portabilité (format technologique structuré et couramment utilisé)",
          "Data-portability request handling (structured, commonly used technological format)"),
    Check("B10", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.STATUTE, "ss. 12-13",
          "Renseignements sensibles : consentement exprès pour l'utilisation et la communication",
          "Sensitive information: express consent for use and communication"),
    Check("B11", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.CAI, "attente de la CAI (guides)",
          "Formation et sensibilisation du personnel à la protection des RP",
          "Staff privacy training and awareness",
          note="CAI guidance expectation, not an explicit statutory training mandate."),
)


def by_id(check_id: str) -> Check:
    for check in CHECKS:
        if check.id == check_id:
            return check
    raise KeyError(f"unknown check id: {check_id}")


def module_checks(module: str) -> tuple[Check, ...]:
    return tuple(c for c in CHECKS if c.module == module)
