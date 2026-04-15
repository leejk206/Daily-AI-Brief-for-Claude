from pathlib import Path

from fetchers import validate_envelope
from fetchers.hacker_news import parse

FIXTURE = Path(__file__).parent / "fixtures" / "hacker_news.json"


def test_parse_returns_valid_envelope():
    env = parse(FIXTURE.read_bytes())
    validate_envelope(env)
    assert env["source"] == "hacker_news"
    assert len(env["items"]) > 0


def test_items_have_hn_fields():
    env = parse(FIXTURE.read_bytes())
    for item in env["items"]:
        assert item["id"].startswith("hn:")
        assert "points" in item["signals"]
        assert "num_comments" in item["signals"]
        assert isinstance(item["signals"]["points"], int)


def test_url_fallback_to_hn_discussion():
    env = parse(FIXTURE.read_bytes())
    for item in env["items"]:
        assert item["url"].startswith("http")


def test_empty_json_returns_empty_items():
    env = parse(b'{"hits": []}')
    validate_envelope(env)
    assert env["items"] == []
