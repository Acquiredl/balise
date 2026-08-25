"""The client-side questionnaire page must never drift from the intake
template: same check ids, same applicable gating, same question wording.
On failure, run `python tools/build_questionnaire.py` after editing the
template."""

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).parent.parent


def test_questionnaire_page_matches_intake_template():
    template = yaml.safe_load(
        (REPO / "intake" / "intake.template.yaml").read_text(encoding="utf-8"))
    html = (REPO / "docs" / "questionnaire.html").read_text(encoding="utf-8")
    match = re.search(
        r'<script id="questions-data" type="application/json">\s*(\[.*?\])\s*</script>',
        html, re.DOTALL)
    assert match, "questions-data block missing from questionnaire.html"
    page_questions = {q["id"]: q for q in json.loads(match.group(1))}

    template_answers = template["answers"]
    assert set(page_questions) == set(template_answers)
    for check_id, entry in template_answers.items():
        q = page_questions[check_id]
        assert q["applicable"] == ("applicable" in entry), check_id
        assert q["fr"] == entry["question_fr"].strip(), check_id
        assert q["en"] == entry["question_en"].strip(), check_id


def test_questionnaire_page_is_static_by_design():
    # ADR-0005: the page must never transmit answers
    html = (REPO / "docs" / "questionnaire.html").read_text(encoding="utf-8")
    lowered = html.lower()
    for forbidden in ("fetch(", "xmlhttprequest", "<form", "action=", "websocket"):
        assert forbidden not in lowered, f"questionnaire page contains {forbidden!r}"
