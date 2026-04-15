from pathlib import Path

from fetchers import validate_envelope
from fetchers.github_trending import parse

FIXTURE = Path(__file__).parent / "fixtures" / "github_trending.html"


def test_parse_returns_valid_envelope():
    env = parse(FIXTURE.read_bytes())
    validate_envelope(env)
    assert env["source"] == "github_trending"
    assert len(env["items"]) > 0


def test_items_have_github_fields():
    env = parse(FIXTURE.read_bytes())
    for item in env["items"]:
        assert item["url"].startswith("https://github.com/")
        assert "/" in item["title"]
        assert "stars" in item["signals"]
        assert isinstance(item["signals"]["stars"], int)


def test_top_item_has_nonempty_description():
    env = parse(FIXTURE.read_bytes())
    non_empty = [i for i in env["items"] if i["description"]]
    assert len(non_empty) >= 1


def test_empty_html_returns_empty_items():
    env = parse(b"<html><body></body></html>")
    validate_envelope(env)
    assert env["items"] == []
