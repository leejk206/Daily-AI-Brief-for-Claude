from pathlib import Path

from fetchers import validate_envelope
from fetchers.dcinside import parse_html
from fetchers import make_envelope

FIXTURE = Path(__file__).parent / "fixtures" / "dcinside_recommend.html"


def test_parse_html_returns_items():
    items = parse_html(FIXTURE.read_bytes())
    assert len(items) > 0
    for item in items:
        assert item["url"].startswith("https://gall.dcinside.com/")
        assert item["title"]
        assert item["signals"]["gallery"] == "thesingularity"


def test_notice_rows_excluded():
    # The fixture's top row is a pinned newbie-guide notice; it must be dropped.
    items = parse_html(FIXTURE.read_bytes())
    titles = [i["title"] for i in items]
    assert not any("뉴비 가이드" in t for t in titles)


def test_signals_are_numeric():
    items = parse_html(FIXTURE.read_bytes())
    for item in items:
        s = item["signals"]
        assert isinstance(s["recommend"], int)
        assert isinstance(s["replies"], int)
        assert isinstance(s["views"], int)


def test_envelope_is_valid():
    items = parse_html(FIXTURE.read_bytes())
    env = make_envelope("dcinside", items)
    validate_envelope(env)
    assert env["source"] == "dcinside"


def test_malformed_html_returns_empty_list():
    assert parse_html(b"<html><body>no rows</body></html>") == []
