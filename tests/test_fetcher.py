import pytest

from balise import cli, fetcher


def test_also_urls_outrank_conventional_paths_under_page_cap(monkeypatch):
    monkeypatch.setattr(fetcher, "MAX_PAGES", 2)
    monkeypatch.setattr(fetcher, "_assert_public", lambda url: None)
    monkeypatch.setattr(
        fetcher, "_fetch_page",
        lambda client, url: fetcher.Page(url=url, status_code=200,
                                         html="<html></html>"))
    site = fetcher.snapshot("https://x.example/",
                            extra_urls=("https://x.example/soumission",))
    urls = [p.url for p in site.pages]
    # cap of 2: root + the operator's page; speculative paths lose, never --also
    assert urls == ["https://x.example/", "https://x.example/soumission"]


def test_mini_and_intake_together_is_an_error(tmp_path):
    with pytest.raises(SystemExit):
        cli.main(["scan", "https://x.example", "--mini",
                  "--intake", "whatever.yaml", "--out", str(tmp_path)])
