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


class _FakeResponse:
    def __init__(self, url, status_code=200, location=None, text="<html></html>"):
        self.url = url
        self.status_code = status_code
        self.text = text
        self.is_redirect = location is not None
        self.next_request = (
            type("Req", (), {"url": location})() if location else None)


def test_redirect_to_private_address_is_refused():
    responses = iter([_FakeResponse("https://x.example/",
                                    status_code=302,
                                    location="http://127.0.0.1/admin")])

    class FakeClient:
        def get(self, url):
            return next(responses)

    assert fetcher._fetch_page(FakeClient(), "https://x.example/") is None


def test_redirect_to_public_address_is_followed(monkeypatch):
    monkeypatch.setattr(fetcher, "_assert_public", lambda url: None)
    responses = iter([
        _FakeResponse("https://x.example/", status_code=301,
                      location="https://www.x.example/"),
        _FakeResponse("https://www.x.example/", status_code=200),
    ])

    class FakeClient:
        def get(self, url):
            return next(responses)

    page = fetcher._fetch_page(FakeClient(), "https://x.example/")
    assert page is not None and page.url == "https://www.x.example/"


def test_mini_and_intake_together_is_an_error(tmp_path):
    with pytest.raises(SystemExit):
        cli.main(["scan", "https://x.example", "--mini",
                  "--intake", "whatever.yaml", "--out", str(tmp_path)])
