"""Module A — deterministic detectors over a SiteSnapshot.

Each detector returns a Finding with reproducible evidence: the rule that
fired, the URLs and snippets that matched. Detectors never call a model
(ADR 0003). Semantic checks live in semantic.py.

Findings carry reasoning in both report languages (reasoning = EN,
reasoning_fr = FR); registry notes are operator context and are never
rendered into client-facing reports.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .fetcher import Page, SiteSnapshot
from .registry import Status, by_id

# -- signature tables (data, not logic) --------------------------------------

PRIVACY_LINK_PATTERNS = (
    r"politique\s+de\s+confidentialit", r"confidentialité", r"confidentialite",
    r"vie\s+privée", r"vie\s+privee", r"privacy\s+policy", r"privacy",
    r"protection\s+des\s+renseignements\s+personnels",
)

OFFICER_PATTERNS = (
    r"responsable\s+de\s+la\s+protection\s+des\s+renseignements\s+personnels",
    r"privacy\s+officer",
    r"person\s+in\s+charge\s+of\s+the\s+protection\s+of\s+personal\s+information",
    r"responsable\s+de\s+l['’]accès\s+aux\s+documents",
)

# Trackers observable in the initial HTML payload. Presence before any consent
# interaction is an indicator, not proof of firing-without-consent — scored
# accordingly (partial/unknown, never not_met on this evidence alone).
TRACKER_SIGNATURES = {
    "Google Analytics / GTM": (r"googletagmanager\.com", r"google-analytics\.com", r"gtag\("),
    "Meta Pixel": (r"connect\.facebook\.net", r"fbevents\.js", r"fbq\("),
    "Hotjar": (r"static\.hotjar\.com", r"hotjar"),
    "LinkedIn Insight": (r"snap\.licdn\.com",),
    "TikTok Pixel": (r"analytics\.tiktok\.com",),
}

CONSENT_BANNER_SIGNATURES = {
    "Axeptio": (r"axeptio",),
    "Cookiebot": (r"cookiebot",),
    "OneTrust": (r"onetrust", r"optanon"),
    "Didomi": (r"didomi",),
    "CookieYes": (r"cookieyes",),
    "Byscuit": (r"byscuit",),
    "tarteaucitron": (r"tarteaucitron",),
}

FRENCH_HINTS = (r"\bconfidentialité\b", r"\bnous\b", r"\bpolitique\b", r"\bvie privée\b")


@dataclass
class Finding:
    check_id: str
    status: Status
    evidence: list[str] = field(default_factory=list)
    reasoning: str = ""        # English
    reasoning_fr: str = ""     # French (canonical report language)

    @property
    def check(self):
        return by_id(self.check_id)


def _search_pages(site: SiteSnapshot, patterns: tuple[str, ...]) -> list[tuple[Page, str]]:
    hits: list[tuple[Page, str]] = []
    for page in site.pages:
        lowered = page.html.lower()
        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                start = max(0, match.start() - 60)
                snippet = re.sub(r"\s+", " ", lowered[start:match.end() + 60]).strip()
                hits.append((page, snippet))
                break
    return hits


def _find_privacy_page(site: SiteSnapshot) -> Page | None:
    for page in site.pages:
        path = page.url.lower()
        if any(k in path for k in ("confidentialite", "privacy", "vie-privee")):
            return page
    return None


def check_a1_privacy_policy(site: SiteSnapshot) -> Finding:
    policy_page = _find_privacy_page(site)
    if policy_page is not None:
        return Finding(
            "A1", Status.MET, evidence=[policy_page.url],
            reasoning="A dedicated privacy-policy page was retrieved.",
            reasoning_fr="Une page dédiée à la politique de confidentialité a été trouvée.")
    link_hits = _search_pages(site, PRIVACY_LINK_PATTERNS)
    if link_hits:
        page, snippet = link_hits[0]
        return Finding(
            "A1", Status.PARTIAL, evidence=[page.url, snippet],
            reasoning="Privacy wording found but no dedicated policy page was "
                      "retrievable at conventional paths.",
            reasoning_fr="Des mentions de confidentialité ont été repérées, mais aucune "
                         "page de politique dédiée n'a été trouvée aux emplacements usuels.")
    return Finding(
        "A1", Status.NOT_MET, evidence=[p.url for p in site.pages],
        reasoning="No privacy policy found on the retrieved pages (s. 8.2 requires "
                  "publication when PI is collected by technological means).",
        reasoning_fr="Aucune politique de confidentialité trouvée sur les pages "
                     "consultées (l'art. 8.2 exige sa publication lorsque des "
                     "renseignements personnels sont recueillis par un moyen "
                     "technologique).")


def check_a3_officer(site: SiteSnapshot) -> Finding:
    hits = _search_pages(site, OFFICER_PATTERNS)
    if not hits:
        return Finding(
            "A3", Status.NOT_MET, evidence=[p.url for p in site.pages],
            reasoning="No mention of a privacy officer on the retrieved pages "
                      "(s. 3.1 requires the title and contact information to be "
                      "published).",
            reasoning_fr="Aucune mention d'un responsable de la protection des "
                         "renseignements personnels sur les pages consultées "
                         "(l'art. 3.1 exige la publication du titre et des "
                         "coordonnées).")
    page, snippet = hits[0]
    has_contact = bool(re.search(r"mailto:|@|téléphone|telephone|phone", page.html.lower()))
    if has_contact:
        return Finding(
            "A3", Status.MET, evidence=[page.url, snippet],
            reasoning="Officer mention with contact means on the same page.",
            reasoning_fr="Responsable mentionné avec un moyen de contact sur la "
                         "même page.")
    return Finding(
        "A3", Status.PARTIAL, evidence=[page.url, snippet],
        reasoning="Officer mentioned but no contact means detected nearby.",
        reasoning_fr="Responsable mentionné, mais aucun moyen de contact détecté "
                     "à proximité.")


def check_a5_trackers(site: SiteSnapshot) -> Finding:
    root = site.pages[0] if site.pages else None
    if root is None:
        return Finding("A5", Status.UNKNOWN,
                       reasoning="No pages retrieved.",
                       reasoning_fr="Aucune page récupérée.")
    html = root.html.lower()
    trackers = [name for name, sigs in TRACKER_SIGNATURES.items()
                if any(re.search(s, html) for s in sigs)]
    banners = [name for name, sigs in CONSENT_BANNER_SIGNATURES.items()
               if any(re.search(s, html) for s in sigs)]
    if not trackers:
        return Finding(
            "A5", Status.MET, evidence=[root.url],
            reasoning="No known tracker signatures in the initial payload. "
                      "(Static analysis only; runtime behavior not observed.)",
            reasoning_fr="Aucune signature de traceur connue dans le contenu initial. "
                         "(Analyse statique seulement; le comportement à l'exécution "
                         "n'a pas été observé.)")
    if banners:
        return Finding(
            "A5", Status.PARTIAL,
            evidence=[root.url, f"traceurs / trackers: {', '.join(trackers)}",
                      f"plateforme de consentement / consent platform: {', '.join(banners)}"],
            reasoning="Trackers present alongside a consent platform; whether they "
                      "stay inactive before consent requires runtime verification. "
                      "CAI Guidelines 2023-1 expect off-by-default.",
            reasoning_fr="Traceurs présents avec une plateforme de consentement; leur "
                         "inactivité avant le consentement doit être confirmée à "
                         "l'exécution. Les Lignes directrices 2023-1 de la CAI "
                         "attendent une désactivation par défaut.")
    return Finding(
        "A5", Status.PARTIAL,
        evidence=[root.url, f"traceurs / trackers: {', '.join(trackers)}"],
        reasoning="Tracker scripts in the initial payload with no consent platform "
                  "detected. Indicator of activation before consent (regulator "
                  "expectation, contested tier); runtime confirmation recommended.",
        reasoning_fr="Scripts de traceurs dans le contenu initial sans plateforme de "
                     "consentement détectée. Indicateur d'activation avant "
                     "consentement (attente du régulateur, niveau contesté); une "
                     "confirmation à l'exécution est recommandée.")


def check_a7_french(site: SiteSnapshot) -> Finding:
    root = site.pages[0] if site.pages else None
    if root is None:
        return Finding("A7", Status.UNKNOWN,
                       reasoning="No pages retrieved.",
                       reasoning_fr="Aucune page récupérée.")
    html = root.html
    lang_attr = re.search(r"<html[^>]*\blang=[\"']?([a-zA-Z-]+)", html)
    lang = (lang_attr.group(1).lower() if lang_attr else "")
    has_fr_alternate = bool(re.search(r"hreflang=[\"']?fr", html.lower()))
    looks_french = sum(1 for p in FRENCH_HINTS if re.search(p, html.lower())) >= 2
    evidence = [root.url, f"html lang={lang or 'absent'}",
                f"version fr / fr alternate: {'oui/yes' if has_fr_alternate else 'non/no'}"]
    if lang.startswith("fr") or looks_french:
        return Finding(
            "A7", Status.MET, evidence=evidence,
            reasoning="Site presents in French (Charter s. 52 exposure low). "
                      "Policy/ToS French versions still need page-level review.",
            reasoning_fr="Le site se présente en français (exposition faible à "
                         "l'art. 52 de la Charte). Les versions françaises de la "
                         "politique et des conditions restent à vérifier page par page.")
    if has_fr_alternate:
        return Finding(
            "A7", Status.PARTIAL, evidence=evidence,
            reasoning="French alternate declared; completeness of the French version "
                      "not verified.",
            reasoning_fr="Version française déclarée; l'exhaustivité de la version "
                         "française n'a pas été vérifiée.")
    return Finding(
        "A7", Status.NOT_MET, evidence=evidence,
        reasoning="No French version detected on the root page. Charter s. 52 "
                  "(firm-interpreted to cover commercial sites and policies); "
                  "OQLF exposure $3k-$30k per offence.",
        reasoning_fr="Aucune version française détectée sur la page d'accueil. "
                     "Charte, art. 52 (interprétation convergente des cabinets "
                     "couvrant les sites commerciaux et leurs politiques); "
                     "exposition OQLF de 3 000 $ à 30 000 $ par infraction.")


DETERMINISTIC_CHECKS = {
    "A1": check_a1_privacy_policy,
    "A3": check_a3_officer,
    "A5": check_a5_trackers,
    "A7": check_a7_french,
}


def run_external_scan(site: SiteSnapshot) -> list[Finding]:
    return [fn(site) for fn in DETERMINISTIC_CHECKS.values()]
