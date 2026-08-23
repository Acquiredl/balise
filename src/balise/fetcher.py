"""Site retrieval for the external scan.

Security posture (see THREAT-MODEL.md):
- Only http/https URLs; requests to private, loopback, and link-local addresses
  are refused (SSRF guard) — the tool scans public websites, nothing else.
- Bounded page count, response size, and timeouts.
- Fetched content is UNTRUSTED INPUT everywhere downstream.
"""

from __future__ import annotations

import ipaddress
import re
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


LINK_TEXT_PATTERNS = re.compile(
    r"confidentialit|vie[\s-]?priv|privacy|renseignements\s+personnels|"
    r"conditions|mentions\s+l[ée]gales|terms", re.IGNORECASE)
LINK_HREF_PATTERNS = re.compile(
    r"confidentialite|declaration_confidentialite|privacy|vie-privee|"
    r"conditions|mentions-legales|terms", re.IGNORECASE)
MAX_DISCOVERED = 5


def _discover_privacy_links(html: str, base_url: str) -> list[str]:
    """Find privacy/terms links the site actually uses, whatever their URL
    shape (portal query strings included) — conventional paths are not enough
    in the wild."""
    found: list[str] = []
    for match in re.finditer(
            r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>",
            html, re.IGNORECASE | re.DOTALL):
        href, text = match.group(1), re.sub(r"<[^>]+>", " ", match.group(2))
        if LINK_HREF_PATTERNS.search(href) or LINK_TEXT_PATTERNS.search(text):
            absolute = urljoin(base_url, href.replace("&amp;", "&"))
            if absolute.startswith(("http://", "https://")) and absolute not in found:
                found.append(absolute)
        if len(found) >= MAX_DISCOVERED:
            break
    return found


def snapshot(root_url: str, extra_urls: tuple[str, ...] = ()) -> SiteSnapshot:
    """Fetch the root page, likely privacy paths, and the privacy/terms links
    the root page itself declares."""
    _assert_public(root_url)
    site = SiteSnapshot(root_url=root_url)
    seen: set[str] = set()

    def fetch_into(client: httpx.Client, url: str) -> Page | None:
        try:
            _assert_public(url)
        except ScanRefused:
            return None
        page = _fetch_page(client, url)
        if page is None or page.url in seen:
            return None
        seen.add(page.url)
        if page.status_code < 400:
            site.pages.append(page)
            return page
        return None

    with httpx.Client(
        follow_redirects=True,
        timeout=TIMEOUT_S,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        root_page = fetch_into(client, root_url)
        discovered = (_discover_privacy_links(root_page.html, root_page.url)
                      if root_page else [])
        candidates = discovered + [urljoin(root_url, p) for p in CANDIDATE_PATHS]
        candidates.extend(extra_urls)
        for url in candidates:
            if len(site.pages) >= MAX_PAGES:
                break
            fetch_into(client, url)
    return site
