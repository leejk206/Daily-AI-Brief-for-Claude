from pathlib import Path

from fetchers import validate_envelope
from fetchers.release_blogs import parse_feed, build_envelope

FIXTURE = Path(__file__).parent / "fixtures" / "openai_feed.xml"


def test_parse_feed_returns_items():
    items = parse_feed(FIXTURE.read_bytes(), source_label="openai")
    assert len(items) > 0
    for item in items:
        assert item["url"].startswith("http")
        assert item["title"]
        assert item["signals"]["vendor"] == "openai"


def test_build_envelope_wraps_items():
    items = parse_feed(FIXTURE.read_bytes(), source_label="openai")
    env = build_envelope(items)
    validate_envelope(env)
    assert env["source"] == "release_blogs"


def test_malformed_feed_returns_empty_list():
    items = parse_feed(b"<not-xml>", source_label="openai")
    assert items == []
