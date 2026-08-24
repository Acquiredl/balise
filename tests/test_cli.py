from balise import cli, fetcher


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
