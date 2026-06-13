from pathlib import Path

from fetchers import validate_envelope
from fetchers.anthropic_news import parse_html
from fetchers import make_envelope

FIXTURE = Path(__file__).parent / "fixtures" / "anthropic_news.html"


def test_parse_html_returns_items():
    items = parse_html(FIXTURE.read_bytes())
    assert len(items) > 0
    for item in items:
        assert item["url"].startswith("https://www.anthropic.com/news/")
        assert item["title"]
        assert item["signals"]["vendor"] == "anthropic"


def test_items_are_deduped():
    items = parse_html(FIXTURE.read_bytes())
    urls = [i["url"] for i in items]
    assert len(urls) == len(set(urls))


def test_envelope_is_valid():
    items = parse_html(FIXTURE.read_bytes())
    env = make_envelope("anthropic_news", items)
    validate_envelope(env)
    assert env["source"] == "anthropic_news"


def test_malformed_html_returns_empty_list():
    assert parse_html(b"<html><body>no articles</body></html>") == []
