import json
from pathlib import Path

from scripts.archive_top5 import archive_top5


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_new_top5_added(tmp_path):
    archive = tmp_path / "archive.json"
    archive.write_text("{}")
    top5 = tmp_path / "top5.json"
    top5.write_text(
        json.dumps(
            [
                {"url": "https://a.example", "title": "A"},
                {"url": "https://b.example", "title": "B"},
            ]
        )
    )
    summary = archive_top5(str(archive), str(top5), today="2026-04-15")
    assert summary["added"] == 2
    assert summary["skipped"] == 0
    data = _load(archive)
    assert data["https://a.example"]["archived_on"] == "2026-04-15"
    assert data["https://a.example"]["title"] == "A"
    assert data["https://b.example"]["archived_on"] == "2026-04-15"


def test_existing_url_not_overwritten(tmp_path):
    archive = tmp_path / "archive.json"
    archive.write_text(
        json.dumps(
            {"https://a.example": {"archived_on": "2026-04-10", "title": "A original"}}
        )
    )
    top5 = tmp_path / "top5.json"
    top5.write_text(
        json.dumps(
            [
                {"url": "https://a.example", "title": "A new title"},
                {"url": "https://b.example", "title": "B"},
            ]
        )
    )
    summary = archive_top5(str(archive), str(top5), today="2026-04-16")
    assert summary["added"] == 1
    assert summary["skipped"] == 1
    data = _load(archive)
    assert data["https://a.example"]["archived_on"] == "2026-04-10"
    assert data["https://a.example"]["title"] == "A original"
    assert data["https://b.example"]["archived_on"] == "2026-04-16"


def test_missing_archive_file_treated_as_empty(tmp_path):
    archive = tmp_path / "archive.json"
    top5 = tmp_path / "top5.json"
    top5.write_text(json.dumps([{"url": "https://a.example", "title": "A"}]))
    summary = archive_top5(str(archive), str(top5), today="2026-04-15")
    assert summary["added"] == 1
    assert archive.exists()


def test_corrupt_archive_backed_up(tmp_path):
    archive = tmp_path / "archive.json"
    archive.write_text("not json")
    top5 = tmp_path / "top5.json"
    top5.write_text("[]")
    summary = archive_top5(str(archive), str(top5), today="2026-04-15")
    assert summary["corrupt_backup"] is not None
    assert Path(summary["corrupt_backup"]).exists()
    assert _load(archive) == {}


def test_skips_items_without_url(tmp_path):
    archive = tmp_path / "archive.json"
    archive.write_text("{}")
    top5 = tmp_path / "top5.json"
    top5.write_text(
        json.dumps(
            [
                {"title": "no url"},
                {"url": "https://a.example", "title": "A"},
            ]
        )
    )
    summary = archive_top5(str(archive), str(top5), today="2026-04-15")
    assert summary["added"] == 1
    data = _load(archive)
    assert "https://a.example" in data
