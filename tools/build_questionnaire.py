"""Regenerate the questions block in docs/questionnaire.html from the intake
template. Run after ANY edit to intake/intake.template.yaml — the drift test
(tests/test_questionnaire_page.py) fails until the page is regenerated.

Idempotent: replaces the JSON inside the questions-data script block in place.

Usage:  python tools/build_questionnaire.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).parent.parent
BLOCK = re.compile(
    r'(<script id="questions-data" type="application/json">\s*)(\[.*?\]|__QUESTIONS_JSON__)(\s*</script>)',
    re.DOTALL)


def main() -> int:
    template = yaml.safe_load(
        (REPO / "intake" / "intake.template.yaml").read_text(encoding="utf-8"))
    questions = [{
        "id": check_id,
        "applicable": "applicable" in entry,
        "fr": entry["question_fr"].strip(),
        "en": entry["question_en"].strip(),
    } for check_id, entry in template["answers"].items()]

    page = REPO / "docs" / "questionnaire.html"
    html = page.read_text(encoding="utf-8")
    payload = json.dumps(questions, ensure_ascii=False, indent=1)
    updated, count = BLOCK.subn(lambda m: m.group(1) + payload + m.group(3), html)
    if count != 1:
        raise SystemExit("questions-data block not found in questionnaire.html")
    if updated != html:
        page.write_text(updated, encoding="utf-8")
        print(f"regenerated: {len(questions)} questions")
    else:
        print(f"already current: {len(questions)} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
