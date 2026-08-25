import json

from balise.external import Finding
from balise.intake import run_intake_assessment
from balise.registry import Status
from balise.report import verify_audit_trail, write_report


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
    assert len(lines) == len(findings) + 1          # genesis + one per finding
    genesis = json.loads(lines[0])
    assert genesis["format"] == "balise-audit-trail/1"
    assert genesis["records"] == len(findings)
    for line in lines[1:]:
        record = json.loads(line)
        assert {"check", "legal_hook", "tier", "status", "reasoning",
                "reasoning_fr", "prev", "sha256"} <= set(record)
    # the head is printed in the report body — the deliverable is the head record
    assert paths.head in body


def test_trail_carries_evidence_grade_and_provenance(tmp_path):
    findings = [
        Finding("A1", Status.MET, reasoning="x", reasoning_fr="x"),   # deterministic
        Finding("A2", Status.PARTIAL, reasoning="x", reasoning_fr="x"),  # semantic
        Finding("B6", Status.NOT_MET, reasoning="x", reasoning_fr="x"),  # intake
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)
    lines = paths.audit_jsonl.read_text(encoding="utf-8").strip().splitlines()

    # genesis commits every output-determining ingredient
    genesis = json.loads(lines[0])
    for field in ("prompt_sha256", "catalog_sha256"):
        assert len(genesis[field]) == 64 and int(genesis[field], 16) >= 0
    assert genesis["eval_suite"] == "none" or len(genesis["eval_suite"]) == 64

    # the grade derives from the check's mode: site checks are observations
    # of the artifact, intake answers are the subject's word
    grades = {json.loads(line)["check"]: json.loads(line)["evidence_grade"]
              for line in lines[1:]}
    assert grades == {"A1": "artifact_inspected", "A2": "artifact_inspected",
                      "B6": "self_reported"}

    # the report shows the reader which findings rest on the client's word
    body = paths.report_md.read_text(encoding="utf-8")
    assert "Nature de la preuve" in body
    assert "Déclaré par l'entreprise, non vérifié" in body
    assert "Self-reported, unverified" in body
    assert "Observed on the site" in body


def test_pre_existing_trail_without_new_fields_still_verifies(tmp_path):
    """Trails sealed before evidence_grade / provenance existed must keep
    verifying: the new fields are additive, never required."""
    from balise.report import TRAIL_FORMAT, _sealed
    genesis = _sealed({"format": TRAIL_FORMAT, "ts": "2026-08-24T00:00:00+00:00",
                       "target": "https://x.example", "tool": "balise 0.1.0",
                       "engine": "none", "records": 1}, prev=None)
    finding = _sealed({"ts": "2026-08-24T00:00:01+00:00", "check": "A1",
                       "legal_hook": "s. 8.2", "tier": "STATUTE",
                       "contested": False, "status": "met", "evidence": [],
                       "reasoning": "x", "reasoning_fr": "x"},
                      prev=genesis["sha256"])
    path = tmp_path / "audit-trail.jsonl"
    path.write_text(json.dumps(genesis, ensure_ascii=False) + "\n"
                    + json.dumps(finding, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    assert verify_audit_trail(path)
    assert verify_audit_trail(path, expect_head=finding["sha256"])


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


def test_emphatic_negation_leads_parse_as_not_met():
    intake = {"answers": {
        "B14": {"answer": "jamais, on garde tout."},
        "B17": {"answer": "aucun inventaire n'existe."},
        "B5": {"answer": "rien d'écrit chez nous."},
        "B11": {"answer": "pas encore"},          # "pas" stays ambiguous
    }}
    findings = {f.check_id: f for f in run_intake_assessment(intake)}
    assert findings["B14"].status is Status.NOT_MET
    assert findings["B17"].status is Status.NOT_MET
    assert findings["B5"].status is Status.NOT_MET
    assert findings["B11"].status is Status.UNKNOWN


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


def test_audit_trail_hash_chain_detects_tampering(tmp_path):
    findings = [
        Finding("A1", Status.MET, reasoning="x", reasoning_fr="x"),
        Finding("A3", Status.NOT_MET, reasoning="x", reasoning_fr="x"),
        Finding("B1", Status.PARTIAL, reasoning="x", reasoning_fr="x"),
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)
    assert verify_audit_trail(paths.audit_jsonl)
    assert verify_audit_trail(paths.audit_jsonl, expect_head=paths.head)

    # lines[0] is genesis; lines[1..3] are the finding records
    lines = paths.audit_jsonl.read_text(encoding="utf-8").strip().splitlines()

    # deleting a middle record breaks the chain
    paths.audit_jsonl.write_text(
        "\n".join([lines[0], lines[1], lines[3]]) + "\n", encoding="utf-8")
    assert not verify_audit_trail(paths.audit_jsonl)

    # truncating the tail leaves a valid-looking chain — genesis count catches it
    paths.audit_jsonl.write_text(
        "\n".join([lines[0], lines[1], lines[2]]) + "\n", encoding="utf-8")
    assert not verify_audit_trail(paths.audit_jsonl)

    # editing one field breaks that record's own hash
    tampered = json.loads(lines[2])
    tampered["status"] = "met"
    paths.audit_jsonl.write_text(
        "\n".join([lines[0], lines[1],
                   json.dumps(tampered, ensure_ascii=False), lines[3]])
        + "\n", encoding="utf-8")
    assert not verify_audit_trail(paths.audit_jsonl)

    # reordering breaks it even though every individual hash still matches
    paths.audit_jsonl.write_text(
        "\n".join([lines[0], lines[2], lines[1], lines[3]]) + "\n",
        encoding="utf-8")
    assert not verify_audit_trail(paths.audit_jsonl)

    # wholesale regeneration verifies internally — ONLY the external head
    # (printed in the delivered report) catches it
    regenerated = write_report(
        [Finding("A1", Status.MET, reasoning="y", reasoning_fr="y")],
        target="https://x.example", out_dir=tmp_path)
    assert verify_audit_trail(regenerated.audit_jsonl)
    assert not verify_audit_trail(regenerated.audit_jsonl,
                                  expect_head=paths.head)


def test_exec_summary_opens_report_with_counts_and_top_priorities(tmp_path):
    findings = [
        Finding("A9", Status.NOT_MET, reasoning="x", reasoning_fr="x"),   # priority 3
        Finding("B1", Status.NOT_MET, reasoning="x", reasoning_fr="x"),   # priority 1
        Finding("B9", Status.UNKNOWN, reasoning="x", reasoning_fr="x"),
        Finding("A1", Status.MET, reasoning="x", reasoning_fr="x"),
    ]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)
    body = paths.report_md.read_text(encoding="utf-8")

    fr_section = body.split("Law 25 Readiness Report")[0]
    assert "Si vous ne lisez qu'un paragraphe" in fr_section
    assert "If you read only one paragraph" in body
    assert "**4 points vérifiés**" in fr_section
    # opener renders before the posture table and the findings detail
    assert (fr_section.index("Si vous ne lisez qu'un paragraphe")
            < fr_section.index("Posture par domaine"))
    # priority-1 gap (B1) listed before priority-3 gap (A9)
    assert fr_section.index("1. **") < fr_section.index("2. **")
    b1_title = fr_section.index("registre des incidents")
    a9_title = fr_section.index("changements de politique")
    assert b1_title < a9_title
    # unknowns present -> the reassurance line renders
    assert "pas un échec" in fr_section


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


def test_genesis_carries_assessment_id_displayed_in_both_languages(tmp_path):
    findings = [Finding("A1", Status.MET, reasoning="x", reasoning_fr="x")]
    paths = write_report(findings, target="https://x.example", out_dir=tmp_path)

    genesis = json.loads(
        paths.audit_jsonl.read_text(encoding="utf-8").splitlines()[0])
    assert genesis["assessment_id"] == paths.assessment_id
    assert paths.assessment_id  # nonempty

    # printed in the report header of each language section, beside the head
    body = paths.report_md.read_text(encoding="utf-8")
    assert body.count(paths.assessment_id) >= 2
    assert verify_audit_trail(paths.audit_jsonl, expect_head=paths.head)


def test_assessment_ids_are_unique_per_run(tmp_path):
    findings = [Finding("A1", Status.MET, reasoning="x", reasoning_fr="x")]
    first = write_report(findings, target="https://x.example",
                         out_dir=tmp_path / "a")
    second = write_report(findings, target="https://x.example",
                          out_dir=tmp_path / "b")
    assert first.assessment_id != second.assessment_id
