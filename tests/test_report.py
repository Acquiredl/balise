import json

from balise.external import Finding
from balise.intake import run_intake_assessment
from balise.registry import Status
from balise.report import write_report


def test_report_is_bilingual_with_disclaimers_and_audit_trail(tmp_path):
    findings = [
        Finding("A1", Status.MET, evidence=["https://x.example/politique"],
                reasoning="Policy page retrieved.",
                reasoning_fr="Page de politique trouvée."),
        Finding("B6", Status.NOT_MET, evidence=["réponse / answer: no"],
                reasoning="Self-reported through the intake questionnaire; "
                          "supporting documents not independently verified.",
                reasoning_fr="Autodéclaré dans le questionnaire; documents non "
                             "vérifiés de façon indépendante."),
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)

    body = paths.report_md.read_text(encoding="utf-8")
    assert "ne constitue pas un avis juridique" in body
    assert "is not legal advice" in body
    assert "LCCJTI" in body            # legal hook rendered
    assert "[LOI]" in body             # FR tier label
    assert "[STATUTE]" in body         # EN tier label

    # FR section uses the French reasoning, not the English fallback
    fr_section = body.split("Law 25 Readiness Report")[0]
    assert "Page de politique trouvée." in fr_section
    assert "Policy page retrieved." not in fr_section

    # operator registry notes never leak into the client report
    assert "Highest-yield" not in body        # B6 note fragment
    assert "Verified 2026" not in body        # verification-history fragments

    lines = paths.audit_jsonl.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(findings)
    for line in lines:
        record = json.loads(line)
        assert {"check", "legal_hook", "tier", "status", "reasoning",
                "reasoning_fr", "sha256"} <= set(record)


def test_unanswered_intake_reports_unknown_not_failure():
    findings = run_intake_assessment(None)
    assert findings, "intake assessment must cover all B checks"
    assert all(f.status is Status.UNKNOWN for f in findings)
    assert all(f.reasoning for f in findings)


def test_answered_intake_maps_statuses():
    intake = {"answers": {
        "B6": {"answer": "no", "details": "fingerprint time-clock in use, no CAI declaration"},
    }}
    findings = run_intake_assessment(intake)
    b6 = next(f for f in findings if f.check_id == "B6")
    assert b6.status is Status.NOT_MET
    assert any("time-clock" in item for item in b6.evidence)


def test_intake_parses_natural_french_answers():
    intake = {"answers": {
        "B1": {"answer": "non, nous n'avons pas de registre, mais un processus existe."},
        "B5": {"answer": "oui"},
        "B9": {"answer": "incertain", "details": "besoin d'aide"},
        "B4": {"answer": "Partiellement mis en place"},
        "B18": {"answer": "pas de cameras", "applicable": "non"},
    }}
    findings = {f.check_id: f for f in run_intake_assessment(intake)}
    assert findings["B1"].status is Status.NOT_MET
    assert findings["B5"].status is Status.MET
    assert findings["B9"].status is Status.UNKNOWN
    assert findings["B4"].status is Status.PARTIAL
    assert findings["B18"].status is Status.NOT_APPLICABLE
    assert findings["B18"].reasoning_fr.startswith("Déclaré sans objet")


def test_summary_orders_priorities_and_explains_unknown(tmp_path):
    from balise.summary import write_summary
    findings = [
        Finding("A9", Status.NOT_MET, reasoning="x", reasoning_fr="x"),   # priority 3
        Finding("B1", Status.NOT_MET, reasoning="x", reasoning_fr="x"),   # priority 1
        Finding("B9", Status.UNKNOWN, reasoning="x", reasoning_fr="x"),
        Finding("A1", Status.MET, reasoning="x", reasoning_fr="x"),
    ]
    path = write_summary(findings, target="https://x.example", out_dir=tmp_path,
                         notices=[("Avis public.", "Public notice.")])
    body = path.read_text(encoding="utf-8")
    # urgent (B1, priority 1) renders before priority-3 (A9)
    assert body.index("registre des incidents") < body.index("changements de politique")
    assert "Pourquoi c’est important" in body
    assert "point de discussion, pas un échec" in body   # unknown explained
    assert "Avis public." in body and "Public notice." in body
    assert "Autodéclaré" not in body                     # report internals stay out


def test_findings_sort_naturally_and_notices_render(tmp_path):
    findings = [
        Finding("A10", Status.UNKNOWN, reasoning="x", reasoning_fr="x"),
        Finding("A2", Status.UNKNOWN, reasoning="x", reasoning_fr="x"),
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path,
                         notices=[("Organisme public détecté.", "Public body detected.")])
    body = paths.report_md.read_text(encoding="utf-8")
    assert body.index("### A2 ") < body.index("### A10 ")
    assert "Organisme public détecté." in body
    assert "Public body detected." in body
