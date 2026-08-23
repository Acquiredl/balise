import json

from balise.external import Finding
from balise.intake import run_intake_assessment
from balise.registry import Status
from balise.report import write_report


def test_report_is_bilingual_with_disclaimers_and_audit_trail(tmp_path):
    findings = [
        Finding("A1", Status.MET, evidence=["https://x.example/politique"],
                reasoning="Policy page retrieved."),
        Finding("B6", Status.NOT_MET, evidence=["intake answer: no"],
                reasoning="Self-reported through the intake questionnaire; "
                          "supporting documents not independently verified."),
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)

    body = paths.report_md.read_text(encoding="utf-8")
    assert "ne constitue pas un avis juridique" in body
    assert "is not legal advice" in body
    assert "LCCJTI" in body            # legal hook rendered
    assert "[LOI]" in body             # FR tier label
    assert "[STATUTE]" in body         # EN tier label

    lines = paths.audit_jsonl.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(findings)
    for line in lines:
        record = json.loads(line)
        assert {"check", "legal_hook", "tier", "status", "reasoning", "sha256"} <= set(record)


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
