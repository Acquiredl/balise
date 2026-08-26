"""Regenerate the demo engagement for the fictional Pépinière du Renard Bleu.

Runs the REAL pipeline on staged inputs: the fixture site in ./site is loaded
into a SiteSnapshot directly (the domain is fictional, so the fetcher is
bypassed — everything downstream is the production code path). With
ANTHROPIC_API_KEY set, the semantic checks run for real; without it they
report honest unknowns. Regenerate WITH the key before publishing.

Usage:  python samples/demo/generate.py
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

from balise import external, report, semantic, summary
from balise import intake as intake_mod
from balise.fetcher import Page, SiteSnapshot

BASE = "https://pepiniere-renard-bleu.example"
HERE = Path(__file__).parent

PAGES = (
    ("index.html", f"{BASE}/"),
    ("politique-de-confidentialite.html", f"{BASE}/politique-de-confidentialite.html"),
    ("contact.html", f"{BASE}/contact.html"),
)


def main() -> int:
    site = SiteSnapshot(root_url=BASE)
    # The fixture pages are "retrieved" now: the staged file is the
    # artifact the checks examine, so the source references and the
    # evidence archive carry its fingerprint like any real engagement.
    staged_at = datetime.now(UTC).isoformat()
    for filename, url in PAGES:
        html = (HERE / "site" / filename).read_text(encoding="utf-8")
        site.pages.append(Page(url=url, status_code=200, html=html,
                               fetched_at=staged_at))

    findings = external.run_external_scan(site)
    findings += semantic.run_semantic_checks(site)
    intake_data = intake_mod.load_intake(HERE / "intake.yaml")
    findings += intake_mod.run_intake_assessment(intake_data)

    out_dir = HERE / "out"
    paths = report.write_report(findings, target=BASE, out_dir=out_dir,
                                snapshot=site)
    summary_path = summary.write_summary(findings, target=BASE, out_dir=out_dir,
                                         head=paths.head)
    # The manifest is the package's last write — nothing may be written
    # to out/ after this line (sealing happens separately: seals apply
    # to the manifest's bytes from outside, they never change them).
    manifest_path = report.write_manifest(out_dir,
                                          assessment_id=paths.assessment_id,
                                          target=BASE,
                                          trail_head=paths.head)

    if not semantic.SemanticEngine.configured():
        print("NOTE: ANTHROPIC_API_KEY absent — semantic checks reported as "
              "unknown. Regenerate with the key before publishing this sample.")
    print(f"report:      {paths.report_md}")
    print(f"summary:     {summary_path}")
    print(f"trail:       {paths.audit_jsonl}")
    print(f"manifest:    {manifest_path}")
    print("next: `balise seal samples/demo/out --anchor-only`, then "
          "`balise verify samples/demo/out`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
