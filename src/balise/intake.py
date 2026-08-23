"""Module B — intake questionnaire loading and assessment.

The intake YAML mirrors intake/intake.template.yaml. Each answered item maps
to a B-check finding; unanswered items report `unknown` honestly.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .external import Finding
from .registry import Status, module_checks

_ANSWER_TO_STATUS = {
    "yes": Status.MET,
    "partial": Status.PARTIAL,
    "no": Status.NOT_MET,
    "not_applicable": Status.NOT_APPLICABLE,
    "unknown": Status.UNKNOWN,
}


def load_intake(path: str | Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    answers = data.get("answers", {})
    if not isinstance(answers, dict):
        raise ValueError("intake file must contain an 'answers' mapping")
    return data


def run_intake_assessment(intake: dict | None) -> list[Finding]:
    answers = (intake or {}).get("answers", {})
    findings: list[Finding] = []
    for check in module_checks("B"):
        entry = answers.get(check.id)
        if entry is None:
            findings.append(Finding(
                check.id, Status.UNKNOWN,
                reasoning="Not answered in intake; organizational obligations "
                          "cannot be observed from outside."))
            continue
        raw_answer = str(entry.get("answer", "unknown")).lower()
        status = _ANSWER_TO_STATUS.get(raw_answer, Status.UNKNOWN)
        note = str(entry.get("details", "")).strip()
        findings.append(Finding(
            check.id, status,
            evidence=[f"intake answer: {raw_answer}"] + ([note] if note else []),
            reasoning="Self-reported through the intake questionnaire; "
                      "supporting documents not independently verified."))
    return findings
