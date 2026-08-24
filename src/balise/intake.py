"""Module B — intake questionnaire loading and assessment.

The intake YAML mirrors intake/intake.template.yaml. Each answered item maps
to a B-check finding; unanswered items report `unknown` honestly.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .external import Finding
from .registry import Status, module_checks

_ANSWER_TO_STATUS = {
    # English enums
    "yes": Status.MET,
    "partial": Status.PARTIAL,
    "partially": Status.PARTIAL,
    "no": Status.NOT_MET,
    "not_applicable": Status.NOT_APPLICABLE,
    "na": Status.NOT_APPLICABLE,
    "n/a": Status.NOT_APPLICABLE,
    "unknown": Status.UNKNOWN,
    # French, as owners actually answer
    "oui": Status.MET,
    "non": Status.NOT_MET,
    "partiel": Status.PARTIAL,
    "partiellement": Status.PARTIAL,
    "sans_objet": Status.NOT_APPLICABLE,
    "sans objet": Status.NOT_APPLICABLE,
    "incertain": Status.UNKNOWN,
    "inconnu": Status.UNKNOWN,
    # unambiguous negation leads (walk finding F18): "jamais, on garde tout"
    # is an emphatic no, not an unknown. "pas" stays out — too ambiguous
    # ("pas de problème, oui on a ça").
    "jamais": Status.NOT_MET,
    "aucun": Status.NOT_MET,
    "aucune": Status.NOT_MET,
    "rien": Status.NOT_MET,
}

_NO_TOKENS = {"no", "non", "false", "0"}


def _parse_answer(raw: str) -> Status:
    """Map a natural-language answer to a status via its leading token.

    Owners answer in sentences ("non, nous n'avons pas de registre...");
    the leading word carries the verdict, the rest is context kept as
    evidence. Unrecognized answers degrade to UNKNOWN, never guessed.
    """
    text = raw.strip().lower().strip("\"'")
    if text in _ANSWER_TO_STATUS:
        return _ANSWER_TO_STATUS[text]
    lead = re.split(r"[\s,.;:!]+", text, maxsplit=1)[0] if text else ""
    return _ANSWER_TO_STATUS.get(lead, Status.UNKNOWN)


def load_intake(path: str | Path) -> dict:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("intake file must be a YAML mapping")
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
                          "cannot be observed from outside.",
                reasoning_fr="Sans réponse au questionnaire; les obligations "
                             "organisationnelles ne s'observent pas de l'extérieur."))
            continue
        raw_answer = str(entry.get("answer", "unknown"))
        note = str(entry.get("details", "")).strip()
        applicable = str(entry.get("applicable", "")).strip().lower()
        if applicable in _NO_TOKENS:
            findings.append(Finding(
                check.id, Status.NOT_APPLICABLE,
                evidence=[f"réponse / answer: {raw_answer}"] + ([note] if note else []),
                reasoning="Declared not applicable in the intake (the practice "
                          "this check covers is not in use).",
                reasoning_fr="Déclaré sans objet dans le questionnaire (la "
                             "pratique visée par cette vérification n'est pas "
                             "utilisée)."))
            continue
        status = _parse_answer(raw_answer)
        findings.append(Finding(
            check.id, status,
            evidence=[f"réponse / answer: {raw_answer}"] + ([note] if note else []),
            reasoning="Self-reported through the intake questionnaire; "
                      "supporting documents not independently verified.",
            reasoning_fr="Autodéclaré dans le questionnaire; les documents à "
                         "l'appui n'ont pas été vérifiés de façon indépendante."))
    return findings
