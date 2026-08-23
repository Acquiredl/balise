"""Client-facing visual summary — the briefing that accompanies the report.

The report is the verbose record; this page is what the owner actually reads
first: posture at a glance, the priorities and WHY they matter in plain
language, what's solid, and what needs clarifying. Status is never conveyed
by color alone (icon + label always; palette CVD-validated with in-segment
labels and gaps as secondary encoding).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .advice import CLIENT_COPY
from .external import Finding
from .registry import Domain, Status
from .report import DOMAIN_LABELS, TIER_LABELS_FR, _check_order

STATUS_META = {
    Status.MET:            ("#177a4c", "✓", "Atteint", "Met"),
    Status.PARTIAL:        ("#b0790a", "◐", "Partiel", "Partial"),
    Status.NOT_MET:        ("#9d3511", "✗", "Non atteint", "Not met"),
    Status.NOT_APPLICABLE: ("#5b7285", "—", "Sans objet", "Not applicable"),
    Status.UNKNOWN:        ("#8a8f98", "?", "Indéterminé", "Unknown"),
}

_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;color:#16232e;
     background:#fff;line-height:1.5;font-size:15px;max-width:880px;margin:0 auto;padding:36px 28px}
h1{font-family:Georgia,serif;font-size:30px;margin-bottom:4px}
h2{font-family:Georgia,serif;font-size:21px;margin:34px 0 12px;padding-bottom:6px;border-bottom:2px solid #16232e}
.meta{color:#55616c;font-size:13.5px;margin-bottom:14px}
.notice{border-left:4px solid #9d3511;background:#faf3f0;padding:10px 14px;margin:12px 0;font-size:13.5px}
.disclaimer{border-left:4px solid #c96f1e;background:#fdf8f1;padding:10px 14px;margin:12px 0;font-size:13px;color:#3d4f5e}
.tiles{display:flex;gap:14px;margin:20px 0;flex-wrap:wrap}
.tile{flex:1;min-width:150px;border:1.5px solid #d8dde2;border-radius:6px;padding:14px 16px}
.tile .n{font-family:Georgia,serif;font-size:34px;line-height:1}
.tile .t{font-size:12.5px;color:#55616c;margin-top:4px;text-transform:uppercase;letter-spacing:.8px}
.bars{margin:14px 0}
.bar-row{display:grid;grid-template-columns:190px 1fr;gap:12px;align-items:center;margin:7px 0}
.bar-label{font-size:13.5px;text-align:right;color:#3d4f5e}
.bar{display:flex;height:22px;border-radius:4px;overflow:hidden;background:#eef1f4}
.seg{display:flex;align-items:center;justify-content:center;color:#fff;font-size:11.5px;
     font-weight:600;margin-right:2px}
.seg:last-child{margin-right:0}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:#3d4f5e;margin:10px 0 0}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:3px;display:inline-block}
.card{border:1.5px solid #d8dde2;border-left-width:5px;border-radius:6px;padding:16px 18px;margin:12px 0;
      page-break-inside:avoid}
.card h3{font-size:16.5px;margin-bottom:6px}
.chip{display:inline-block;font-size:12px;font-weight:600;padding:2px 10px;border-radius:10px;
      color:#fff;margin-left:8px;vertical-align:2px}
.card .why{margin:8px 0 6px}
.card .why b,.card .act b{font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:#55616c;display:block;margin-bottom:2px}
.card .ref{font-size:12px;color:#8a8f98;margin-top:8px}
.oklist,.unklist{list-style:none}
.oklist li,.unklist li{padding:6px 0 6px 28px;position:relative;border-top:1px dotted #e2e6ea;font-size:14.5px}
.oklist li::before{content:"✓";position:absolute;left:4px;color:#177a4c;font-weight:700}
.unklist li::before{content:"?";position:absolute;left:6px;color:#8a8f98;font-weight:700}
.small{font-size:13px;color:#55616c}
.pagebreak{page-break-before:always;border-top:3px double #16232e;margin-top:44px;padding-top:30px}
@media print{body{padding:0}}
"""


def _bar(domain_counts: dict[Status, int]) -> str:
    total = sum(domain_counts.values()) or 1
    segs = []
    for status in (Status.MET, Status.PARTIAL, Status.NOT_MET,
                   Status.NOT_APPLICABLE, Status.UNKNOWN):
        count = domain_counts.get(status, 0)
        if not count:
            continue
        color, icon, *_ = STATUS_META[status]
        width = count / total * 100
        label = str(count) if width >= 11 else ""
        segs.append(f'<div class="seg" style="width:{width:.1f}%;'
                    f'background:{color}" title="{icon} {count}">{label}</div>')
    return f'<div class="bar">{"".join(segs)}</div>'


def _chip(status: Status, lang: str) -> str:
    color, icon, fr, en = STATUS_META[status]
    return (f'<span class="chip" style="background:{color}">'
            f'{icon} {fr if lang == "fr" else en}</span>')


def _lang_section(findings: list[Finding], target: str, lang: str,
                  notices: list[tuple[str, str]]) -> str:
    fr = lang == "fr"
    idx = 0 if fr else 1
    copy = {cid: c for cid, c in CLIENT_COPY.items()}

    priorities = sorted(
        (f for f in findings if f.status in (Status.NOT_MET, Status.PARTIAL)),
        key=lambda f: (copy[f.check_id].priority if f.check_id in copy else 3,
                       0 if f.status is Status.NOT_MET else 1,
                       _check_order(f)))
    solid = [f for f in findings if f.status is Status.MET]
    unknown = [f for f in findings if f.status is Status.UNKNOWN]
    na = [f for f in findings if f.status is Status.NOT_APPLICABLE]

    domain_counts: dict[Domain, dict[Status, int]] = {}
    for f in findings:
        domain_counts.setdefault(f.check.domain, {})
        domain_counts[f.check.domain][f.status] = \
            domain_counts[f.check.domain].get(f.status, 0) + 1

    out = []
    out.append(f"<h1>{'Sommaire de préparation — Loi 25' if fr else 'Law 25 Readiness Summary'}</h1>")
    out.append(f'<p class="meta">{target} · {datetime.now(timezone.utc).date().isoformat()}</p>')
    out.append('<div class="disclaimer">' + (
        "Autoévaluation de préparation produite par un outil automatisé. Ce n'est pas un avis "
        "juridique et aucun verdict de conformité n'est rendu. Le rapport détaillé qui accompagne "
        "ce sommaire montre la preuve et la base légale de chaque constat." if fr else
        "A readiness self-assessment produced by an automated tool. This is not legal advice and "
        "no compliance verdict is rendered. The detailed report accompanying this summary shows "
        "each finding's evidence and legal basis.") + "</div>")
    for n_fr, n_en in notices:
        out.append(f'<div class="notice"><b>{n_fr if fr else n_en}</b></div>')

    out.append('<div class="tiles">')
    for n, t_fr, t_en in ((len(priorities), "priorités à traiter", "priorities to address"),
                          (len(solid), "points déjà en place", "already in place"),
                          (len(unknown), "points à clarifier", "to clarify")):
        out.append(f'<div class="tile"><div class="n">{n}</div>'
                   f'<div class="t">{t_fr if fr else t_en}</div></div>')
    out.append("</div>")

    out.append(f"<h2>{'Vue d’ensemble par domaine' if fr else 'Posture by domain'}</h2>")
    out.append('<div class="bars">')
    for domain in Domain:
        if domain not in domain_counts:
            continue
        out.append(f'<div class="bar-row"><div class="bar-label">'
                   f'{DOMAIN_LABELS[domain][idx]}</div>{_bar(domain_counts[domain])}</div>')
    out.append("</div>")
    out.append('<div class="legend">' + "".join(
        f'<span><span class="dot" style="background:{c}"></span>{i} '
        f'{lfr if fr else len_}</span>'
        for c, i, lfr, len_ in STATUS_META.values()) + "</div>")

    out.append(f"<h2>{'Vos priorités, et pourquoi' if fr else 'Your priorities, and why'}</h2>")
    if not priorities:
        out.append(f'<p class="small">{"Aucun écart relevé." if fr else "No gaps found."}</p>')
    for f in priorities:
        c = copy.get(f.check_id)
        if c is None:
            continue
        color = STATUS_META[f.status][0]
        tier = TIER_LABELS_FR[f.check.tier.value] if fr else f.check.tier.value
        out.append(
            f'<div class="card" style="border-left-color:{color}">'
            f"<h3>{c.plain_fr if fr else c.plain_en}{_chip(f.status, lang)}</h3>"
            f'<p class="why"><b>{"Pourquoi c’est important" if fr else "Why it matters"}</b>'
            f"{c.risk_fr if fr else c.risk_en}</p>"
            f'<p class="act"><b>{"Action recommandée" if fr else "Recommended action"}</b>'
            f"{c.action_fr if fr else c.action_en}</p>"
            f'<p class="ref">{f.check.id} · {f.check.legal_hook} [{tier}]</p>'
            f"</div>")

    if solid:
        out.append(f"<h2>{'Ce qui est déjà en place' if fr else 'What’s already in place'}</h2>")
        out.append('<ul class="oklist">' + "".join(
            f"<li>{copy[f.check_id].plain_fr if fr else copy[f.check_id].plain_en}</li>"
            for f in sorted(solid, key=_check_order) if f.check_id in copy) + "</ul>")

    if unknown:
        out.append(f"<h2>{'À clarifier ensemble' if fr else 'To clarify together'}</h2>")
        out.append('<p class="small">' + (
            "« Indéterminé » signifie que ni le site ni vos réponses ne permettent de trancher — "
            "c'est un point de discussion, pas un échec." if fr else
            "“Unknown” means neither the site nor your answers settle the point — it's a "
            "conversation item, not a failure.") + "</p>")
        out.append('<ul class="unklist">' + "".join(
            f"<li>{copy[f.check_id].plain_fr if fr else copy[f.check_id].plain_en}</li>"
            for f in sorted(unknown, key=_check_order) if f.check_id in copy) + "</ul>")

    if na:
        out.append(f'<p class="small" style="margin-top:16px">' + (
            f"{len(na)} vérifications sans objet pour votre organisation (pratiques non utilisées)."
            if fr else
            f"{len(na)} checks not applicable to your organization (practices not in use).") + "</p>")
    return "\n".join(out)


def write_summary(findings: list[Finding], target: str, out_dir: str | Path,
                  notices: list[tuple[str, str]] | None = None) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    notices = notices or []
    html = ("<!DOCTYPE html>\n<html lang=\"fr\"><head><meta charset=\"UTF-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            "<title>Sommaire Balise</title><style>" + _CSS + "</style></head><body>"
            + _lang_section(findings, target, "fr", notices)
            + '<div class="pagebreak"></div>'
            + _lang_section(findings, target, "en", notices)
            + "</body></html>")
    path = out / "sommaire-balise.html"
    path.write_text(html, encoding="utf-8")
    return path
