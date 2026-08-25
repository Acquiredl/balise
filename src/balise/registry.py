"""Check catalog — the assessment methodology as data.

Every check traces to a legal hook and carries an authority tier (ADR 0001).
Statutory references are triangulated, not yet human-verified against
LegisQuebec: docs/VERIFICATION.md gates client-facing use.
"""

import hashlib
import json
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


# Client-facing status wording, (FR, EN) — single source for every renderer
# (walk finding F22: report, summary, and insurer each carried their own copy).
STATUS_LABELS = {
    Status.MET: ("Atteint", "Met"),
    Status.PARTIAL: ("Partiel", "Partial"),
    Status.NOT_MET: ("Non atteint", "Not met"),
    Status.NOT_APPLICABLE: ("Sans objet", "Not applicable"),
    Status.UNKNOWN: ("Indéterminé", "Unknown"),
}


class EvidenceGrade(str, Enum):
    """What kind of evidence backs a finding — orthogonal to its status.

    A grade qualifies a status, never changes it: it measures the
    independence of the evidence, not the correctness of the conclusion.
    Grading table with examples: docs/VERIFICATION-TRAIL.md."""
    SELF_REPORTED = "self_reported"              # subject testimony, unexamined
    DOCUMENT_EVIDENCED = "document_evidenced"    # a supporting document was received
    ARTIFACT_INSPECTED = "artifact_inspected"    # the artifact itself was examined
    INDEPENDENTLY_OBSERVED = "independently_observed"  # recomputable by the verifier


# Client-facing evidence-grade wording, (FR, EN) — single source, like STATUS_LABELS.
EVIDENCE_GRADE_LABELS = {
    EvidenceGrade.SELF_REPORTED: ("Déclaré par l'entreprise, non vérifié",
                                  "Self-reported, unverified"),
    EvidenceGrade.DOCUMENT_EVIDENCED: ("Document fourni", "Document provided"),
    EvidenceGrade.ARTIFACT_INSPECTED: ("Observé sur le site", "Observed on the site"),
    EvidenceGrade.INDEPENDENTLY_OBSERVED: ("Vérifiable indépendamment",
                                           "Independently verifiable"),
}

# v0.1 grades derive from the check's mode: both deterministic detectors and
# semantic checks examine the fetched site (the artifact); intake answers are
# the subject's word. document_evidenced and independently_observed are
# reserved for future evidence sources (client documents; anchored facts).
MODE_EVIDENCE_GRADE = {
    Mode.DETERMINISTIC: EvidenceGrade.ARTIFACT_INSPECTED,
    Mode.SEMANTIC: EvidenceGrade.ARTIFACT_INSPECTED,
    Mode.INTAKE: EvidenceGrade.SELF_REPORTED,
}


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
          "Privacy policy published on the website",
          note="Trigger is conditional: applies when PI is collected BY TECHNOLOGICAL "
               "MEANS (website, email, app) — CAI policy guide p. 2. Statute also "
               "requires DIFFUSION to reach the persons concerned, which a website scan "
               "cannot observe — reported as a scan limitation."),
    Check("A2", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "ss. 8, 8.2 + guide CAI",
          "Politique en termes simples et clairs, couvrant fins, droits, tiers et communication hors Québec",
          "Policy in clear and plain language, covering purposes, rights, third parties and communication outside Quebec",
          note="Content beyond s. 8's own disclosure list is CAI recommendation, not "
               "statute: the CAI states no private-sector content regulation exists "
               "(policy guide p. 3). Semantic rubric mirrors the guide's [must]/[may] "
               "structure, incl. its anti-conflation rule: ToS and privacy policy must "
               "not be merged (guide s. 1.2)."),
    Check("A3", "A", Domain.GOVERNANCE, Mode.DETERMINISTIC, Tier.STATUTE, "s. 3.1",
          "Titre et coordonnées du responsable de la protection des renseignements personnels publiés",
          "Privacy officer title and contact information published",
          note="TITLE + contact are mandatory; the officer's NAME is optional per the "
               "CAI policy guide (s. 2.5) — never penalize its absence."),
    Check("A4", "A", Domain.GOVERNANCE, Mode.SEMANTIC, Tier.STATUTE, "s. 3.2",
          "Information détaillée sur les politiques de gouvernance publiée",
          "Detailed information about governance policies published"),
    Check("A5", "A", Domain.TRANSPARENCY, Mode.DETERMINISTIC, Tier.CAI,
          "s. 8.1 + Lignes directrices 2023-1",
          "Témoins non essentiels inactifs avant consentement; bannière avec refus accessible",
          "Non-essential trackers inactive before consent; banner with accessible refusal",
          contested=True,
          note="The CAI drafts off-by-default in MANDATORY language (Guidelines 2023-1 "
               "s. B.4: 'doivent être désactivées par défaut') and applies it to "
               "profiling cookies (Ex. B-b) — the CAI does not hedge. The contest is "
               "between the CAI's reading and the statutory browser-cookie carve-out "
               "(s. 9.1); the Guidelines themselves state they lack force of law."),
    Check("A6", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 8.1",
          "Technologies de repérage, localisation ou profilage divulguées, avec moyens d'activation",
          "Tracking, locating or profiling technology disclosed, with means of activation"),
    Check("A7", "A", Domain.TRANSPARENCY, Mode.DETERMINISTIC, Tier.FIRM,
          "Charte de la langue française, art. 52, 55",
          "Version française du site, de la politique et des conditions (français d'abord pour les contrats d'adhésion)",
          "French version of site, policy and terms (French-first for adhesion contracts)",
          contested=True,
          note="Policies-in-scope of s. 52 is convergent firm interpretation ('documents of "
               "the same nature', 'regardless of the medium'). Dual exposure: Law 25 "
               "plain-language + OQLF ($3k-$30k per offence). Verified 2026-08-23: other "
               "languages allowed if the French version is available on terms at least as "
               "favourable; s. 55 French-first for adhesion contracts exempts contracts "
               "used in relations with persons outside Québec."),
    Check("A8", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 14",
          "Formulaires : consentement par finalité, en termes clairs, demandé distinctement",
          "Forms: purpose-granular consent, in clear language, requested separately",
          note="CAI Guidelines 2023-1 define EIGHT validity criteria: manifeste, libre, "
               "éclairé, spécifique, granulaire, compréhensible, temporaire, DISTINCT — "
               "violating any one voids the consent. 'Temporaire' requires the duration "
               "be delimited IN ADVANCE (by deadline or event, Guidelines s. 7.2)."),
    Check("A9", "A", Domain.TRANSPARENCY, Mode.SEMANTIC, Tier.STATUTE, "s. 8.2",
          "Pratique d'avis de modification de la politique",
          "Policy amendment-notice practice",
          note="Statute-only sourcing: no CAI guide restates the amendment-notice duty "
               "(the policy guide only recommends periodic re-evaluation)."),
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
               "and CAI notification is never deferred (s. 3.5). CAI expectation "
               "(prevention checklist p. 8): an incident-MANAGEMENT policy/procedures "
               "(detect, record, report, respond) as a governance artifact distinct "
               "from the register itself. "
               "Walk finding F6 (2026-08-23): the uncited third sanction layer — "
               "punitive damages of at least $1,000 per person for intentional or "
               "gross-fault breaches, expressly combinable into class actions "
               "(McCarthy toolkit table 2). Also honest-broker framing: the CAI must "
               "weigh remediation measures, cooperation, and compensation offered when "
               "setting an AMP — the response to an incident materially changes the "
               "sanction."),
    Check("B2", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 3.3",
          "EFVP pour tout système d'information acquis, développé ou refondu impliquant des RP",
          "PIA for any acquired, developed or overhauled information system involving PI",
          note="Trigger also covers electronic service delivery systems and any PI "
               "lifecycle operation (collection through destruction). s. 3.3 al. 3 adds "
               "portability-by-design: projects must ensure collected computerized PI "
               "can be output in a structured, commonly used format (statute-only — the "
               "CAI EFVP guide is silent on this prong). Client pointer: CAI EFVP guide "
               "v3.1 (avril 2024) + the CAI's modele generique de rapport d'EFVP; the "
               "guide names biometric, AI, video-surveillance systems, member zones, "
               "mobile apps as s. 3.3 triggers (s. 7.2)."),
    Check("B3", "B", Domain.VENDORS_TRANSFERS, Mode.INTAKE, Tier.STATUTE, "s. 17",
          "EFVP et entente écrite pour toute communication hors Québec (incluant chaque SaaS hébergé aux É.-U.)",
          "PIA and written agreement for any communication outside Quebec (including every US-hosted SaaS)",
          note="No adequacy whitelist exists; analysis depth is a proportionality judgment "
               "(FIRM-level methodology). Empirically the biggest unmet paper obligation. "
               "Verified 2026-08-23: s. 17 al. 3 explicitly extends the duty to entrusting "
               "collection/use/keeping to a person outside Québec — cloud hosting is caught "
               "by the statute's own words. Cite CAI EFVP guide s. 7.1 (4 factors, 11 "
               "recognized principles as the adequacy rubric, refuse-if-inadequate) — NOT "
               "the 2015 infonuagique fiche (outdated 'equivalent' standard, marked en "
               "cours de révision). "
               "Walk finding F7 (2026-08-23): s. 17 catches INTERPROVINCIAL transfers "
               "too, not only international ones ('hors Québec' means exactly that — "
               "McCarthy toolkit s. 3C reads it as covering interprovincial and "
               "cross-border alike). A Toronto-hosted SaaS needs the same EFVP + "
               "written agreement as a US one; intake question updated to say so."),
    Check("B4", "B", Domain.VENDORS_TRANSFERS, Mode.INTAKE, Tier.STATUTE, "s. 18.3",
          "Contrats écrits avec les mandataires et fournisseurs de services",
          "Written contracts with mandataries and service providers",
          note="Verified 2026-08-23: contract must also bar retention after expiry; "
               "processor must notify the privacy officer without delay of violations "
               "AND attempted violations, and allow confidentiality verifications. "
               "Contract-content requirements waived for public bodies and members of "
               "professional orders (s. 18.3 in fine). "
               "Walk finding F4 (2026-08-23): the employer stays fully liable when "
               "outsourcing (TCJ art. 968) — the sharpest client-facing point on this "
               "check. Current probe (McCarthy toolkit table 4): standard AI-vendor "
               "contracts with ML-training clauses let the vendor use client data "
               "beyond the mandate, violating s. 12's use restrictions — ask about "
               "AI tools specifically."),
    Check("B5", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 3.2",
          "Politiques internes : rôles du cycle de vie, conservation/destruction, traitement des plaintes",
          "Internal policies: lifecycle roles, retention/destruction, complaint handling"),
    Check("B6", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.STATUTE, "LCCJTI, art. 44-45",
          "Systèmes biométriques : consentement exprès et déclaration à la CAI 60 jours avant la mise en service",
          "Biometric systems: express consent and CAI declaration 60 days before service",
          note="The CAI's only active enforcement area (Transcontinental 2024, Metro 2025 — "
               "cease/destroy orders). Highest-yield intake question. Verified 2026-08-23: "
               "s. 44 also requires prior CAI disclosure of the verification PRACTICE "
               "itself (not just the s. 45 database), strict minimization, no secondary "
               "use, and destruction of records as soon as the purpose is met. CAI "
               "biometrics guide adds: a no-pressure ALTERNATIVE means on refusal is "
               "mandatory; no collection a l'insu; journaling (LCCJTI 41 al. 2) with "
               "log review; prefer irreversible template over raw image; the guide's "
               "11-item consent-disclosure list + the CAI's model consent form are "
               "the client pointers."),
    Check("B7", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.STATUTE, "s. 12.1",
          "Décisions fondées exclusivement sur un traitement automatisé : information et observations auprès d'une personne en mesure de réviser la décision",
          "Decisions based exclusively on automated processing: disclosure and observations to a staff member able to review the decision",
          note="Walk finding F1 (2026-08-23): the s. 12.1 remedy is observations TO a "
               "person in a position to review the decision — a review channel, not a "
               "suggestion box. Both lawyer corpora (TCJ art. 984; McCarthy toolkit "
               "s. 5B) frame it as a human-review right; the old title undersold it. "
               "On request the person also gets: the PI used, the reasons and principal "
               "factors/parameters, and the correction right."),
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
          note="Not a freestanding statutory mandate; the CAI frames training as the "
               "expected way to IMPLEMENT the s. 3.2 governance obligation (prevention "
               "checklist p. 6 nests it under that duty as an example)."),
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
               "(see Regulation respecting the anonymization of personal information). "
               "Walk finding F2 (2026-08-23): penal exposure attaches (s. 91 regime; "
               "s. 91(4) makes failure to take s. 10 measures a penal offence — see "
               "VERIFICATION bonus row). Primary-source (CAI recruitment page, read "
               "2026-08-24): anonymization discouraged — 'quasi impossible de "
               "certifier' irreversibility; destruction preferred. "
               "Sharp intake probe from TCJ art. 983: backups are the classic "
               "destruction blind spot — 'do your backups also honor destruction?'"),
    Check("B15", "B", Domain.TRANSPARENCY, Mode.INTAKE, Tier.STATUTE, "ss. 12, 22",
          "Prospection commerciale : consentement requis (jamais une « fin compatible »); identification et droit de retrait",
          "Commercial prospection: consent required (never a 'consistent purpose'); self-identification and withdrawal right",
          note="s. 12 states expressly that commercial or philanthropic prospection may "
               "not be considered a consistent purpose — marketing reuse always needs "
               "consent; s. 22 adds identify-yourself and stop-on-withdrawal duties. "
               "Statute-only sourcing: no current CAI guide addresses prospection "
               "(the 2013 profilage fiche predates these provisions). "
               "Walk finding F3 (2026-08-23): dual federal exposure — CASL/LCAP "
               "requires express consent + functional unsubscribe for commercial "
               "electronic messages, penalties to $10M (TCJ art. 970); flag alongside "
               "the Law 25 analysis the way A7 flags OQLF. Calming nuance (McCarthy): "
               "consents validly obtained before Law 25 remain valid — no re-consent "
               "campaign needed; and s. 12 lists narrow no-consent exceptions "
               "(compatible purposes with a direct-and-relevant link, manifest benefit, "
               "fraud prevention, service delivery, depersonalized research) — "
               "prospection is expressly excluded from 'compatible'."),
    Check("B16", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "ss. 27-34",
          "Traitement des demandes d'accès et de rectification : réponse écrite sous 30 jours, gratuité, refus motivés",
          "Access/rectification request handling: written reply within 30 days, free access, reasoned refusals",
          note="The ONE hard statutory deadline in this law: reply promptly and no later "
               "than 30 days (s. 32); silence = deemed refusal. Requests go to the "
               "privacy officer; refusals must cite the provision, remedies, and time "
               "limit (s. 34). The market fears a fake 72-hour rule and misses this "
               "real 30-day one. Covers the CAI's full four-rights frame: access, "
               "rectification, portability (see B9), and cessation of dissemination / "
               "de-indexing (s. 28.1). Duty of complete-and-serious search extends to "
               "email, messaging, and PI held by third parties/processors. "
               "Walk finding F9 (2026-08-23), procedural mechanics from the McCarthy "
               "toolkit: the enterprise may ask the CAI to extend the 30-day window "
               "within the initial period (s. 46); refusals must also state the "
               "requester's right to a CAI examen de mésentente within 30 days "
               "(s. 43) and help understanding the refusal on request (s. 34); "
               "s. 28.1 de-indexing requests weigh prescribed factors (public-figure "
               "status, minority, accuracy, sensitivity, context, elapsed time, "
               "criminal matter/pardon)."),
    # ---- added from CAI corpus triple-check 2026-08-23 ----
    Check("B17", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.CAI,
          "pratique-phare de la CAI (aide-mémoire; guide prévention, étape 2; guide EFVP, étape 3)",
          "Inventaire à jour des renseignements personnels détenus, avec évaluation de sensibilité",
          "Up-to-date inventory of personal information held, with sensitivity assessment",
          note="The CAI's cornerstone practice — not a discrete statutory mandate, but "
               "the foundation every statutory duty rests on (you cannot protect, "
               "destroy, or produce what you have not located). Quoi/Pourquoi/Qui/"
               "Comment/Où/Quand model table in the prevention guide."),
    Check("B18", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.CAI,
          "fiche vidéosurveillance (2019, jurisprudence) + s. 8; EFVP obligatoire post-Loi 25",
          "Vidéosurveillance : nécessité/proportionnalité documentées, affichage, conservation limitée (~30 jours)",
          "Video surveillance: documented necessity/proportionality, signage, limited retention (~30 days)",
          note="Necessity must be evidenced ('de simples appréhensions... ne suffisent "
               "pas'); signage with contact info (s. 8 duty applied); the corpus's only "
               "quantified retention benchmark: ~30 days generally sufficient and "
               "recommended; camera projects trigger a mandatory PIA post-Loi 25 "
               "(named in EFVP guide s. 7.2). Fiche is 2019/pre-Loi 25 — necessity test "
               "is jurisprudence-grounded and current; procedural details are stale."),
    # ---- added 2026-08-23: insurer-eligibility specifics (questionnaire research) ----
    Check("B19", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.FIRM,
          "s. 10 (application courante)",
          "Authentification multifacteur (MFA) sur les courriels et les accès à distance",
          "Multi-factor authentication (MFA) on email and remote access",
          note="MFA is not named by the statute; it is the market's convergent reading "
               "of a s. 10 proportionate measure and the #1 cyber-insurance eligibility "
               "gate. Research 2026-08-23 (4 application forms read): MFA on email is a "
               "MANDATORY question on CFC's and Beazley's short forms; City of Hamilton's "
               "$18.3M ransomware claim was denied in 2025 over incomplete MFA. "
               "Self-reported; feeds the insurer appendix."),
    Check("B20", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.FIRM,
          "s. 10 (application courante)",
          "Copies de sauvegarde hors ligne des données critiques, testées régulièrement",
          "Offline backups of critical data, regularly tested",
          note="Same footing as B19: a s. 10 application, insurer-gated. Research "
               "2026-08-23: daily offline backups is a MANDATORY question on CFC's "
               "short form; Beazley requires compromise-isolated, tested backups. "
               "Self-reported; feeds the insurer appendix."),
    # ---- added at gate re-opening 2026-08-24 (ratified in-session) ----
    Check("B21", "B", Domain.GOVERNANCE, Mode.INTAKE, Tier.STATUTE, "s. 9.1",
          "Paramètres de confidentialité par défaut au plus haut niveau (produits et services technologiques)",
          "Privacy settings default to the highest level (technological products and services)",
          note="Born-verified 2026-08-24 (official FR text read in browser): applies "
               "when the enterprise OFFERS THE PUBLIC a technological product or "
               "service with privacy settings; highest level by default, 'sans "
               "aucune intervention'; connection cookies (témoins de connexion) "
               "expressly excluded (al. 2). Distinct from A5: A5 is the CAI's "
               "off-by-default cookie expectation; s. 9.1 is the statutory "
               "product-default duty the cookie carve-out sits inside. Conditional "
               "practice: applicable-gated (client portals, apps, member zones)."),
    Check("B22", "B", Domain.SPECIAL_CATEGORIES, Mode.INTAKE, Tier.CAI,
          "s. 5 + lignes directrices CAI recrutement (2025-03-17)",
          "Recrutement : collecte limitée au nécessaire à chaque étape, destruction en fin de processus",
          "Recruitment: collection limited to what each stage requires, destruction when the process ends",
          note="Born-verified 2026-08-24: s. 5 necessity read verbatim on LegisQuébec; "
               "the CAI guidelines (2025-03-17) read on the CAI's own page. Four "
               "stages with per-stage permitted lists. Prohibited: photocopying or "
               "recording identity documents; keeping judicial records unrelated to "
               "the position or pardoned. Discouraged: social-media screening, credit "
               "checks (prefer references), emotion-recognition AI ('un usage "
               "inapproprié de l'IA'). SIN and banking only at hiring; destroy "
               "candidate data once the purpose is met (anonymization discouraged: "
               "'quasi impossible de certifier'). These guidelines POST-DATE the "
               "original 2026-08-23 gate sweep — first gate re-opening event. "
               "Career pages are also a Module A surface (future)."),
)


def catalog_fingerprint() -> str:
    """SHA-256 over the canonical serialization of the whole check catalog.

    Recorded in each trail's genesis so 'why did this assessment change' has
    an answer: a changed hook, tier, title or note changes the fingerprint.
    Canonical form mirrors the trail's rules (sorted keys, compact
    separators, raw UTF-8)."""
    payload = [[c.id, c.module, c.domain.value, c.mode.value, c.tier.value,
                c.legal_hook, c.title_fr, c.title_en, c.contested, c.note]
               for c in CHECKS]
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def by_id(check_id: str) -> Check:
    for check in CHECKS:
        if check.id == check_id:
            return check
    raise KeyError(f"unknown check id: {check_id}")


def module_checks(module: str) -> tuple[Check, ...]:
    return tuple(c for c in CHECKS if c.module == module)
