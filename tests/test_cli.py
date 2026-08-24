from balise import cli, fetcher
from balise.registry import CHECKS


def _fixture_snapshot(root_url, html="<html lang='fr'></html>"):
    site = fetcher.SiteSnapshot(root_url=root_url)
    site.pages.append(fetcher.Page(url=root_url, status_code=200, html=html))
    return site


def test_mini_scan_writes_teaser_only(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.fetcher, "snapshot",
                        lambda url, extra_urls=(): _fixture_snapshot(url))
    code = cli.main(["scan", "https://x.example", "--mini", "--out", str(tmp_path)])
    assert code == 0
    teaser = tmp_path / "apercu-balise.html"
    assert teaser.exists()
    assert not (tmp_path / "rapport-balise.md").exists()   # no full deliverables
    body = teaser.read_text(encoding="utf-8")
    assert "Aperçu gratuit" in body and "Free preview" in body
    # honest accounting: full-assessment counter matches the registry
    assert f"{len(CHECKS) - 4} vérifications supplémentaires" in body
    # the differentiator is visible: gap cards carry legal hooks
    assert "art." in body or "s. " in body


def test_also_flag_feeds_extra_urls_into_the_corpus(tmp_path, monkeypatch, capsys):
    captured = {}

    def fake_snapshot(root_url, extra_urls=()):
        captured["extra_urls"] = extra_urls
        site = fetcher.SiteSnapshot(root_url=root_url)
        site.pages.append(fetcher.Page(url=root_url, status_code=200,
                                       html="<html></html>"))
        return site

    monkeypatch.setattr(cli.fetcher, "snapshot", fake_snapshot)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    code = cli.main(["scan", "https://x.example",
                     "--also", "https://x.example/soumission",
                     "--also", "https://x.example/infolettre",
                     "--out", str(tmp_path)])

    assert code == 0
    assert captured["extra_urls"] == ("https://x.example/soumission",
                                      "https://x.example/infolettre")
    assert (tmp_path / "rapport-balise.md").exists()
