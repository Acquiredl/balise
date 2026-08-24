from balise.external import Finding
from balise.intake import run_intake_assessment
from balise.registry import Status, by_id
from balise.report import write_report


def test_b19_b20_registered_and_parsed_from_intake():
    assert by_id("B19").legal_hook.startswith("s. 10")
    assert by_id("B20").legal_hook.startswith("s. 10")
    intake = {"answers": {
        "B19": {"answer": "oui, sur les courriels et le VPN"},
        "B20": {"answer": "non, sauvegardes en ligne seulement"},
    }}
    findings = {f.check_id: f for f in run_intake_assessment(intake)}
    assert findings["B19"].status is Status.MET
    assert findings["B20"].status is Status.NOT_MET
    # unanswered new checks degrade honestly like every other B check
    unanswered = {f.check_id: f for f in run_intake_assessment(None)}
    assert unanswered["B19"].status is Status.UNKNOWN


def test_insurer_appendix_renders_bilingual_with_scope_note(tmp_path):
    findings = [
        Finding("B19", Status.MET, reasoning="x", reasoning_fr="x"),
        Finding("B20", Status.NOT_MET, reasoning="x", reasoning_fr="x"),
        Finding("B1", Status.PARTIAL, reasoning="x", reasoning_fr="x"),
        Finding("A3", Status.UNKNOWN, reasoning="x", reasoning_fr="x"),
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)
    body = paths.report_md.read_text(encoding="utf-8")

    assert "Annexe — Préparer une demande d'assurance cyber" in body
    assert "Appendix — Preparing a cyber-insurance application" in body
    # mapped statuses render; themes with no finding are omitted
    assert "B19 : Atteint" in body
    assert "B20 : Non atteint" in body
    assert "Gestion des fournisseurs" not in body   # B3/B4 absent from findings
    # the honest scope boundary is stated in both languages
    assert "non évalué par cet outil" in body
    assert "not assessed by this tool" in body
    # governance overlap is framed as fuller-forms, never every-form
    assert "formulaires détaillés" in body
