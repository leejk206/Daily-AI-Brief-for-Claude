import json
from pathlib import Path

from scripts.update_seen import update_seen


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_new_item_added(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text("{}")
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([
        {"url": "https://a.example", "title": "A"},
    ]))
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    assert summary["added"] == 1
    data = _load(state)
    assert data["https://a.example"]["days"] == 1
    assert data["https://a.example"]["first_seen"] == "2026-04-15"
    assert data["https://a.example"]["last_seen"] == "2026-04-15"


def test_bumped_when_seen_yesterday(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text(json.dumps({
        "https://a.example": {
            "first_seen": "2026-04-13",
            "last_seen": "2026-04-14",
            "days": 2,
            "title": "A",
        }
    }))
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([{"url": "https://a.example", "title": "A"}]))
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    assert summary["bumped"] == 1
    data = _load(state)
    assert data["https://a.example"]["days"] == 3
    assert data["https://a.example"]["last_seen"] == "2026-04-15"


def test_reset_on_gap(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text(json.dumps({
        "https://a.example": {
            "first_seen": "2026-04-10",
            "last_seen": "2026-04-12",
            "days": 2,
            "title": "A",
        }
    }))
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([{"url": "https://a.example", "title": "A"}]))
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    data = _load(state)
    assert data["https://a.example"]["days"] == 1
    assert data["https://a.example"]["first_seen"] == "2026-04-15"
    assert summary["added"] == 1


def test_prune_older_than_7_days(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text(json.dumps({
        "https://old.example": {
            "first_seen": "2026-04-01",
            "last_seen": "2026-04-07",
            "days": 5,
            "title": "Old",
        },
        "https://fresh.example": {
            "first_seen": "2026-04-14",
            "last_seen": "2026-04-14",
            "days": 1,
            "title": "Fresh",
        },
    }))
    selected = tmp_path / "selected.json"
    selected.write_text("[]")
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    data = _load(state)
    assert "https://old.example" not in data
    assert "https://fresh.example" in data
    assert summary["pruned"] == 1


def test_corrupt_state_backed_up(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text("not json")
    selected = tmp_path / "selected.json"
    selected.write_text("[]")
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    assert summary["corrupt_backup"] is not None
    assert Path(summary["corrupt_backup"]).exists()
    data = _load(state)
    assert data == {}
