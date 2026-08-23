"""balise — Law 25 readiness scan CLI.

Usage:
    balise scan https://example.com [--intake intake.yaml] [--out ./out]
"""

from __future__ import annotations

import argparse
import sys

from . import external, fetcher, intake as intake_mod, report, semantic


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="balise")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Run a readiness scan against a public website")
    scan.add_argument("url", help="Root URL of the site (https://...)")
    scan.add_argument("--intake", help="Path to a filled intake YAML (Module B)")
    scan.add_argument("--out", default="./balise-out", help="Output directory")
    args = parser.parse_args(argv)

    try:
        site = fetcher.snapshot(args.url)
    except fetcher.ScanRefused as exc:
        print(f"scan refused: {exc}", file=sys.stderr)
        return 2

    if not site.pages:
        print("no pages retrieved; check the URL", file=sys.stderr)
        return 1

    findings = external.run_external_scan(site)
    findings += semantic.run_semantic_checks(site)
    intake_data = intake_mod.load_intake(args.intake) if args.intake else None
    findings += intake_mod.run_intake_assessment(intake_data)

    paths = report.write_report(findings, target=site.root_url, out_dir=args.out)
    print(f"report:      {paths.report_md}")
    print(f"audit trail: {paths.audit_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
