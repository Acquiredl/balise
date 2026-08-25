"""balise — Law 25 readiness scan CLI.

Usage:
    balise scan https://example.com [--intake intake.yaml] [--out ./out]
"""

from __future__ import annotations

import argparse
import re
import sys

from . import external, fetcher, report, semantic, summary
from . import intake as intake_mod

# Balise assesses the PRIVATE-sector regime (CQLR c. P-39.1). Public bodies
# fall under the Loi sur l'accès instead — assessing them against the wrong
# statute would be professionally embarrassing, so we warn loudly.
_PUBLIC_BODY_PATTERNS = re.compile(
    r"municipalit|\bville\b|\bcity of\b|gouvernement|minist[eè]re|"
    r"commission scolaire|centre de services scolaire|\bcegep\b|c[ée]gep|"
    r"universit[ée]|\bhôpital\b|hopital|\bciusss\b|\bcisss\b|organisme public",
    re.IGNORECASE)
_PUBLIC_DOMAIN_PATTERNS = re.compile(
    r"\.gouv\.qc\.ca|\.canada\.ca|\.gc\.ca", re.IGNORECASE)

_SCOPE_NOTICE = (
    "Attention : cet organisme semble être un ORGANISME PUBLIC (municipalité, "
    "ministère, réseau public). Balise évalue le régime du secteur PRIVÉ "
    "(Loi sur le privé, RLRQ c. P-39.1). Les organismes publics relèvent "
    "plutôt de la Loi sur l'accès (RLRQ c. A-2.1) : plusieurs obligations se "
    "ressemblent, mais les articles cités ici ne s'appliquent pas tels quels.",
    "Warning: this organization appears to be a PUBLIC BODY (municipality, "
    "ministry, public network). Balise assesses the PRIVATE-sector regime "
    "(Private Sector Act, CQLR c. P-39.1). Public bodies fall under the Act "
    "respecting Access (CQLR c. A-2.1) instead: many obligations are similar, "
    "but the sections cited here do not apply as written.",
)


def _scope_notices(url: str, intake_data: dict | None) -> list[tuple[str, str]]:
    enterprise = (intake_data or {}).get("enterprise", {}) or {}
    haystack = " ".join(str(enterprise.get(k, "")) for k in ("name", "sector"))
    if _PUBLIC_BODY_PATTERNS.search(haystack) or _PUBLIC_DOMAIN_PATTERNS.search(url):
        return [_SCOPE_NOTICE]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="balise")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Run a readiness scan against a public website")
    scan.add_argument("url", help="Root URL of the site (https://...)")
    scan.add_argument("--intake", help="Path to a filled intake YAML (Module B)")
    scan.add_argument("--out", default="./balise-out", help="Output directory")
    scan.add_argument("--also", action="append", default=[], metavar="URL",
                      help="Extra page to include in the scan corpus (e.g. a "
                           "contact or signup form the crawler would miss); "
                           "repeatable")
    scan.add_argument("--mini", action="store_true",
                      help="Free-preview mode: deterministic remote checks "
                           "only (no intake, no semantic engine), producing a "
                           "teaser summary instead of the full deliverables")
    args = parser.parse_args(argv)
    if args.mini and args.intake:
        parser.error("--mini runs the remote preview only and would ignore "
                     "--intake; drop one of the two flags")

    try:
        site = fetcher.snapshot(args.url, extra_urls=tuple(args.also))
    except fetcher.ScanRefused as exc:
        print(f"scan refused: {exc}", file=sys.stderr)
        return 2

    if not site.pages:
        print("no pages retrieved; check the URL", file=sys.stderr)
        return 1

    findings = external.run_external_scan(site)

    if args.mini:
        teaser_path = summary.write_teaser(findings, target=site.root_url,
                                           out_dir=args.out)
        print(f"preview: {teaser_path}")
        return 0

    findings += semantic.run_semantic_checks(site)
    try:
        intake_data = intake_mod.load_intake(args.intake) if args.intake else None
    except (OSError, ValueError) as exc:
        print(f"intake file invalid: {exc}", file=sys.stderr)
        return 2
    findings += intake_mod.run_intake_assessment(intake_data)

    notices = _scope_notices(site.root_url, intake_data)
    paths = report.write_report(findings, target=site.root_url, out_dir=args.out,
                                notices=notices, snapshot=site)
    summary_path = summary.write_summary(findings, target=site.root_url,
                                         out_dir=args.out, notices=notices,
                                         head=paths.head)
    # The manifest is the package's last write: it hashes every artifact
    # already on disk, so nothing may be written to the package after it.
    manifest_path = report.write_manifest(args.out,
                                          assessment_id=paths.assessment_id,
                                          target=site.root_url,
                                          trail_head=paths.head)
    print(f"report:      {paths.report_md}")
    print(f"summary:     {summary_path}")
    print(f"trail:       {paths.audit_jsonl}")
    print(f"manifest:    {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
