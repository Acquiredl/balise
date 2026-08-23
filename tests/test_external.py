from balise.external import run_external_scan
from balise.fetcher import Page, SiteSnapshot
from balise.registry import Status


def site_with(pages: list[tuple[str, str]]) -> SiteSnapshot:
    snap = SiteSnapshot(root_url=pages[0][0])
    snap.pages = [Page(url=url, status_code=200, html=html) for url, html in pages]
    return snap


COMPLIANT_HOME = """
<html lang="fr"><body>
<a href="/politique-de-confidentialite">Politique de confidentialité</a>
</body></html>
"""

COMPLIANT_POLICY = """
<html lang="fr"><body>
<h1>Politique de confidentialité</h1>
<p>Responsable de la protection des renseignements personnels : Direction,
joignable à <a href="mailto:vie-privee@exemple.example">courriel</a>.</p>
</body></html>
"""

BARE_ENGLISH_HOME = """
<html lang="en"><head>
<script src="https://www.googletagmanager.com/gtag/js?id=G-XX"></script>
</head><body><p>Welcome to our store.</p></body></html>
"""


def by_id(findings, check_id):
    return next(f for f in findings if f.check_id == check_id)


def test_compliant_looking_site_scores_met():
    findings = run_external_scan(site_with([
        ("https://exemple.example/", COMPLIANT_HOME),
        ("https://exemple.example/politique-de-confidentialite", COMPLIANT_POLICY),
    ]))
    assert by_id(findings, "A1").status is Status.MET
    assert by_id(findings, "A3").status is Status.MET
    assert by_id(findings, "A5").status is Status.MET
    assert by_id(findings, "A7").status is Status.MET


def test_bare_english_tracker_site_scores_gaps():
    findings = run_external_scan(site_with([
        ("https://example.example/", BARE_ENGLISH_HOME),
    ]))
    assert by_id(findings, "A1").status is Status.NOT_MET
    assert by_id(findings, "A3").status is Status.NOT_MET
    a5 = by_id(findings, "A5")
    assert a5.status is Status.PARTIAL
    assert any("Google" in item for item in a5.evidence)
    assert by_id(findings, "A7").status is Status.NOT_MET


def test_every_finding_carries_reasoning():
    findings = run_external_scan(site_with([
        ("https://example.example/", BARE_ENGLISH_HOME),
    ]))
    for finding in findings:
        assert finding.reasoning.strip(), finding.check_id
