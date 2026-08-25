"""Deterministic guards for the eval harness: labels and fixtures stay in
sync, and only valid check ids / statuses appear. The live run costs money;
this test keeps its inputs sound for free in CI."""

from pathlib import Path

import yaml

from balise.registry import Status
from balise.semantic import SEMANTIC_CHECK_IDS

EVALS = Path(__file__).parent.parent / "evals"
VALID_STATUSES = {s.value for s in Status}


def test_labels_and_fixture_dirs_match_one_to_one():
    labels = yaml.safe_load((EVALS / "labels.yaml").read_text(encoding="utf-8"))
    fixture_dirs = {d.name for d in (EVALS / "fixtures").iterdir() if d.is_dir()}
    assert set(labels["fixtures"]) == fixture_dirs


def test_labels_reference_valid_checks_and_statuses():
    labels = yaml.safe_load((EVALS / "labels.yaml").read_text(encoding="utf-8"))
    for name, spec in labels["fixtures"].items():
        assert spec["kind"] in ("quality", "redteam"), name
        for table in ("expect", "forbid"):
            for check_id, statuses in (spec.get(table) or {}).items():
                assert check_id in SEMANTIC_CHECK_IDS, f"{name}: {check_id}"
                assert set(statuses) <= VALID_STATUSES, f"{name}/{check_id}"


def test_every_fixture_has_at_least_one_page():
    for fixture_dir in (EVALS / "fixtures").iterdir():
        if fixture_dir.is_dir():
            assert list(fixture_dir.glob("*.html")), fixture_dir.name


def test_redteam_fixtures_carry_the_canary():
    labels = yaml.safe_load((EVALS / "labels.yaml").read_text(encoding="utf-8"))
    canary = labels["canary"]
    for name, spec in labels["fixtures"].items():
        if spec.get("canary_check"):
            pages = " ".join(p.read_text(encoding="utf-8")
                             for p in (EVALS / "fixtures" / name).glob("*.html"))
            assert canary in pages, f"{name} labeled canary_check but has no canary"
