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
    Check("A10", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 9",
          "Formulaires : aucun refus de biens ou services pour refus de fournir des RP non nécessaires",
          "Forms: no refusal of goods or services over declining to provide unnecessary PI",
          note="Burden is on the enterprise: 'in case of doubt, personal information is "
               "deemed non-necessary' (s. 9 in fine). Assess required form fields against "
               "the stated purpose. Added at verification gate 2026-08-23."),
    # ---- Module B: intake --------------------------------------------------
    Check("B1", "B", Domain.INCIDENTS, Mode.INTAKE, Tier.STATUTE,
          "ss. 3.5-3.8 + Règlement sur les incidents",
          "Registre des incidents de confidentialité (8 éléments prescrits, conservation 5 ans) et processus de réponse",
          "Confidentiality-incident register (8 prescribed elements, 5-year retention) and response process",
          note="Notification standard is 'promptly' / « avec diligence » — there is NO "
               "72-hour statutory deadline (that figure is GDPR, not Quebec). Individual "
               "notice may be deferred ONLY while it could hamper an investigation by a "
               "body legally responsible for preventing/detecting/repressing crime or "
               "statutory offences — internal or hired investigations do NOT qualify, "
               "and CAI notification is never deferred (s. 3.5)."),
    Check("B2", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 3.3",
          "EFVP pour tout système d'information acquis, développé ou refondu impliquant des RP",
          "PIA for any acquired, developed or overhauled information system involving PI",
          note="Trigger also covers electronic service delivery systems and any PI "
               "lifecycle operation (collection through destruction). s. 3.3 al. 3 adds "
               "portability-by-design: projects must ensure collected computerized PI "
               "can be output in a structured, commonly used format."),
    Check("B3", "B", Domain.VENDORS_TRANSFERS, Mode.INTAKE, Tier.STATUTE, "s. 17",
          "EFVP et entente écrite pour toute communication hors Québec (incluant chaque SaaS hébergé aux É.-U.)",
          "PIA and written agreement for any communication outside Quebec (including every US-hosted SaaS)",
          note="No adequacy whitelist exists; analysis depth is a proportionality judgment "
               "(FIRM-level methodology). Empirically the biggest unmet paper obligation. "
               "Verified 2026-08-23: s. 17 al. 3 explicitly extends the duty to entrusting "
               "collection/use/keeping to a person outside Québec — cloud hosting is caught "
               "by the statute's own words."),
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
          "Sensitive information: express consent for use and communication",
          note="Sensitivity arises from the information's nature (medical, biometric, "
               "otherwise intimate) OR from the context of its use or communication "
               "(s. 12 in fine) — context alone can make ordinary info sensitive."),
    Check("B11", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.CAI, "attente de la CAI (guides)",
          "Formation et sensibilisation du personnel à la protection des RP",
          "Staff privacy training and awareness",
          note="CAI guidance expectation, not an explicit statutory training mandate."),
    # ---- added at verification gate 2026-08-23 (from official text sweep) ----
    Check("B12", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 10",
          "Mesures de sécurité proportionnées (sensibilité, finalité, quantité, répartition, support)",
          "Security safeguards proportionate to sensitivity, purpose, quantity, distribution, medium"),
    Check("B13", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 11",
          "Exactitude et mise à jour des RP utilisés pour une décision; conservation ≥ 1 an après la décision",
          "Accuracy and currency of PI used to make a decision; keep decision-info ≥ 1 year after"),
    Check("B14", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 23",
          "Destruction ou anonymisation des RP lorsque les fins sont accomplies",
          "Destruction or anonymization of PI once purposes are achieved",
          note="Anonymization must meet regulation-determined criteria and best practices "
               "(see Regulation respecting the anonymization of personal information)."),
    Check("B15", "B", Domain.TRANSPARENCY, Mode.INTAKE, Tier.STATUTE, "ss. 12, 22",
          "Prospection commerciale : consentement requis (jamais une « fin compatible »); identification et droit de retrait",
          "Commercial prospection: consent required (never a 'consistent purpose'); self-identification and withdrawal right",
          note="s. 12 states expressly that commercial or philanthropic prospection may "
               "not be considered a consistent purpose — marketing reuse always needs "
               "consent; s. 22 adds identify-yourself and stop-on-withdrawal duties."),
    Check("B16", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "ss. 27-34",
          "Traitement des demandes d'accès et de rectification : réponse écrite sous 30 jours, gratuité, refus motivés",
          "Access/rectification request handling: written reply within 30 days, free access, reasoned refusals",
          note="The ONE hard statutory deadline in this law: reply promptly and no later "
               "than 30 days (s. 32); silence = deemed refusal. Requests go to the "
               "privacy officer; refusals must cite the provision, remedies, and time "
               "limit (s. 34). The market fears a fake 72-hour rule and misses this "
               "real 30-day one."),
)


def by_id(check_id: str) -> Check:
    for check in CHECKS:
        if check.id == check_id:
            return check
    raise KeyError(f"unknown check id: {check_id}")


def module_checks(module: str) -> tuple[Check, ...]:
    return tuple(c for c in CHECKS if c.module == module)
