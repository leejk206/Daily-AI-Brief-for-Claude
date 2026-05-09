import json
from pathlib import Path

from scripts import tags_state


def test_load_missing_file_returns_empty_state(tmp_path):
    state, backup = tags_state.load(tmp_path / "tags.json")
    assert state == {"version": 1, "items": {}}
    assert backup is None


def test_load_valid_json(tmp_path):
    p = tmp_path / "tags.json"
    p.write_text(json.dumps({
        "version": 1,
        "items": {
            "https://x.example": {
                "title": "T", "summary": "S",
                "category": "mcp", "source": "hacker_news",
                "brief_date": "2026-05-01",
                "tags": ["mcp-server"],
                "tagged_at": "2026-05-01T09:00:00+09:00",
            }
        }
    }))
    state, backup = tags_state.load(p)
    assert backup is None
    assert state["items"]["https://x.example"]["tags"] == ["mcp-server"]


def test_load_corrupt_backs_up_and_returns_empty(tmp_path):
    p = tmp_path / "tags.json"
    p.write_text("{not valid json")
    state, backup = tags_state.load(p)
    assert state == {"version": 1, "items": {}}
    assert backup is not None
    assert ".corrupt-" in backup
    assert Path(backup).exists()


def test_load_malformed_shape_backs_up(tmp_path):
    p = tmp_path / "tags.json"
    p.write_text(json.dumps([1, 2, 3]))  # not a dict
    state, backup = tags_state.load(p)
    assert state == {"version": 1, "items": {}}
    assert backup is not None


def test_save_creates_parent_dirs(tmp_path):
    p = tmp_path / "deep" / "nested" / "tags.json"
    tags_state.save(p, {"version": 1, "items": {}})
    assert p.exists()
    assert json.loads(p.read_text()) == {"version": 1, "items": {}}


def test_upsert_new_item():
    state = {"version": 1, "items": {}}
    tags_state.upsert_item(
        state, "https://a.example",
        title="A", summary="sum",
        category="mcp", source="hacker_news",
        brief_date="2026-05-09",
        tags=["mcp-server", "tool-use"],
    )
    item = state["items"]["https://a.example"]
    assert item["title"] == "A"
    assert item["category"] == "mcp"
    assert item["brief_date"] == "2026-05-09"
    assert sorted(item["tags"]) == ["mcp-server", "tool-use"]
    assert "tagged_at" in item


def test_upsert_existing_merges_tags_and_preserves_brief_date():
    state = {
        "version": 1,
        "items": {
            "https://a.example": {
                "title": "A", "summary": "s",
                "category": "mcp", "source": "hacker_news",
                "brief_date": "2026-04-15",
                "tags": ["mcp-server"],
                "tagged_at": "2026-04-15T09:00:00+09:00",
            }
        },
    }
    tags_state.upsert_item(
        state, "https://a.example",
        title="A2", summary="s2",  # ignored on update
        category="other", source="other",  # ignored on update
        brief_date="2026-05-09",  # ignored — first-touch wins
        tags=["tool-use"],
    )
    item = state["items"]["https://a.example"]
    assert sorted(item["tags"]) == ["mcp-server", "tool-use"]
    assert item["brief_date"] == "2026-04-15"  # preserved
    assert item["title"] == "A"  # preserved
    assert item["category"] == "mcp"  # preserved
    assert item["tagged_at"] != "2026-04-15T09:00:00+09:00"  # refreshed


def test_get_item():
    state = {"version": 1, "items": {"u": {"tags": ["x"]}}}
    assert tags_state.get_item(state, "u") == {"tags": ["x"]}
    assert tags_state.get_item(state, "missing") is None
