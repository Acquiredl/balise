"""Site retrieval for the external scan.

Security posture (see THREAT-MODEL.md):
- Only http/https URLs; requests to private, loopback, and link-local addresses
  are refused (SSRF guard) — the tool scans public websites, nothing else.
- Bounded page count, response size, and timeouts.
- Fetched content is UNTRUSTED INPUT everywhere downstream.
"""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import httpx

MAX_PAGES = 12
MAX_BYTES = 2_000_000
TIMEOUT_S = 15.0
USER_AGENT = "BaliseScanner/0.1 (+Law 25 readiness self-assessment)"

# Candidate paths where privacy-relevant pages usually live.
CANDIDATE_PATHS = (
    "/", "/politique-de-confidentialite", "/confidentialite",
    "/politique-confidentialite", "/vie-privee", "/privacy", "/privacy-policy",
    "/mentions-legales", "/conditions", "/terms", "/contact", "/nous-joindre",
)


class ScanRefused(Exception):
    """URL refused by the security policy (scheme or address range)."""


@dataclass
class Page:
    url: str
    status_code: int
    html: str


@dataclass
class SiteSnapshot:
    root_url: str
    pages: list[Page] = field(default_factory=list)

    def page(self, url: str) -> Page | None:
        for p in self.pages:
            if p.url == url:
                return p
        return None


def _assert_public(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ScanRefused(f"unsupported scheme: {parsed.scheme!r}")
    host = parsed.hostname or ""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ScanRefused(f"cannot resolve host: {host}") from exc
    for info in infos:
        addr = ipaddress.ip_address(info[4][0])
        if (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast):
            raise ScanRefused(f"refusing non-public address for {host}: {addr}")


def _fetch_page(client: httpx.Client, url: str) -> Page | None:
    try:
        response = client.get(url)
    except httpx.HTTPError:
        return None
    body = response.text[:MAX_BYTES] if response.text else ""
    return Page(url=str(response.url), status_code=response.status_code, html=body)


def snapshot(root_url: str, extra_urls: tuple[str, ...] = ()) -> SiteSnapshot:
    """Fetch the root page plus likely privacy-relevant pages."""
    _assert_public(root_url)
    site = SiteSnapshot(root_url=root_url)
    seen: set[str] = set()
    with httpx.Client(
        follow_redirects=True,
        timeout=TIMEOUT_S,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        candidates = [urljoin(root_url, path) for path in CANDIDATE_PATHS]
        candidates.extend(extra_urls)
        for url in candidates:
            if len(site.pages) >= MAX_PAGES:
                break
            _assert_public(url)
            page = _fetch_page(client, url)
            if page is None:
                continue
            if page.url in seen:
                continue
            seen.add(page.url)
            if page.status_code < 400:
                site.pages.append(page)
    return site
