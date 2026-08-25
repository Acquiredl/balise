"""Package verification: the verdict ladder and the tamper battery.

Every attack from the provenance design gets a test: finding edit,
report edit, wholesale trail regeneration, evidence swap, smuggled
evidence, stripped seal. Verdicts name the mechanism, never the
conclusion.
"""

import json

from balise.external import Finding
from balise.fetcher import Page, SiteSnapshot
from balise.registry import Status
from balise.report import write_manifest, write_report
from balise.verify import verify_package


def build_package(tmp_path):
    page = Page(url="https://x.example/politique", status_code=200,
                html="<html><body>politique de confidentialité</body></html>",
                fetched_at="2026-08-25T00:00:00+00:00")
    site = SiteSnapshot(root_url="https://x.example")
    site.pages = [page]
    findings = [
        Finding("A1", Status.MET, evidence=[page.url],
                reasoning="x", reasoning_fr="x",
                sources=[page.source_ref()]),
        Finding("B6", Status.NOT_MET, evidence=["réponse / answer: no"],
                reasoning="x", reasoning_fr="x"),
    ]
    paths = write_report(findings, target="https://x.example",
                         out_dir=tmp_path, snapshot=site)
    (tmp_path / "sommaire-balise.html").write_text("<html>s</html>",
                                                   encoding="utf-8")
    write_manifest(tmp_path, assessment_id=paths.assessment_id,
                   target="https://x.example", trail_head=paths.head)
    return paths


def test_intact_package_is_self_consistent_with_stated_limit(tmp_path):
    build_package(tmp_path)
    verdict = verify_package(tmp_path)
    assert verdict.verdict == "SELF-CONSISTENT"
    assert verdict.exit_code == 0
    rendered = verdict.render()
    assert "SELF-CONSISTENT" in rendered
    # the honest ceiling is printed, not hidden in a doc
    assert "regeneration" in rendered.lower()


def test_attack_edit_finding_breaks_the_chain(tmp_path):
    build_package(tmp_path)
    trail = tmp_path / "audit-trail.jsonl"
    lines = trail.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[1])
    record["status"] = "met" if record["status"] != "met" else "not_met"
    lines[1] = json.dumps(record, ensure_ascii=False)
    trail.write_text("\n".join(lines) + "\n", encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "CHAIN-BROKEN"
    assert verdict.exit_code == 1


def test_attack_edit_report_diverges_from_manifest(tmp_path):
    build_package(tmp_path)
    report = tmp_path / "rapport-balise.md"
    report.write_text(report.read_text(encoding="utf-8")
                      .replace("A1", "A1 (améliorée)"), encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "ARTIFACT-DIVERGED"
    assert verdict.exit_code == 2


def test_attack_regenerated_trail_verifies_alone_but_not_in_package(tmp_path):
    paths = build_package(tmp_path)
    # regenerate the whole trail: internally valid, different head
    findings = [Finding("A1", Status.MET, reasoning="forged",
                        reasoning_fr="forgé")]
    forged = write_report(findings, target="https://x.example",
                          out_dir=tmp_path / "forge")
    assert forged.head != paths.head
    (tmp_path / "audit-trail.jsonl").write_text(
        (tmp_path / "forge" / "audit-trail.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "ARTIFACT-DIVERGED"


def test_attack_modified_evidence_fails_its_hash(tmp_path):
    build_package(tmp_path)
    evidence = next((tmp_path / "evidence").iterdir())
    evidence.write_text("<html><body>rewritten</body></html>",
                        encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "ARTIFACT-DIVERGED"


def test_attack_smuggled_evidence_file_is_flagged(tmp_path):
    build_package(tmp_path)
    (tmp_path / "evidence" / ("f" * 64 + ".html")).write_text(
        "<html>planted</html>", encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "ARTIFACT-DIVERGED"


def test_attack_stripped_declared_seal_is_missing_not_a_downgrade(tmp_path):
    build_package(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["seals"] = ["anchor"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n",
                             encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "SEAL-MISSING"
    assert verdict.exit_code == 3


def test_missing_or_unknown_manifest_is_a_refusal_not_a_verdict(tmp_path):
    build_package(tmp_path)
    (tmp_path / "manifest.json").unlink()
    verdict = verify_package(tmp_path)
    assert verdict.verdict == "UNSUPPORTED-FORMAT"
    assert verdict.exit_code == 4

    build_package(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["format"] = "balise-assessment/999"
    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    assert verify_package(tmp_path).verdict == "UNSUPPORTED-FORMAT"


def test_cli_verify_prints_checklist_and_exits_by_verdict(tmp_path, capsys):
    from balise.cli import main

    build_package(tmp_path)
    assert main(["verify", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "RESULT: SELF-CONSISTENT" in out

    (tmp_path / "rapport-balise.md").write_text("tampered", encoding="utf-8")
    assert main(["verify", str(tmp_path)]) == 2


def test_broken_chain_does_not_flag_the_archive_as_smuggled(tmp_path):
    build_package(tmp_path)
    trail = tmp_path / "audit-trail.jsonl"
    lines = trail.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[1])
    record["status"] = "met" if record["status"] != "met" else "not_met"
    lines[1] = json.dumps(record, ensure_ascii=False)
    trail.write_text("\n".join(lines) + "\n", encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "CHAIN-BROKEN"
    rendered = verdict.render()
    # the chain is the index; with no usable index the archive is not
    # judged, not accused
    assert "not referenced by any finding" not in rendered
    assert "not judged" in rendered
