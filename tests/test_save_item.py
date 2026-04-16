import json
import subprocess
import sys
from pathlib import Path


def _run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "scripts.save_item", *args],
        cwd=cwd or Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
    )


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2))


def _save_args(tmp_path: Path, **overrides):
    defaults = dict(
        url="https://a.example",
        title="Sample Title",
        summary="샘플 요약",
        source="release_blogs",
        category="agent-frameworks",
        brief_date="2026-04-16",
        state_path=str(tmp_path / "state" / "saved.json"),
        saved_dir=str(tmp_path / "saved"),
    )
    defaults.update(overrides)
    out = []
    for k, v in defaults.items():
        out.append(f"--{k.replace('_','-')}")
        out.append(str(v))
    return out


def test_missing_args_exits_2():
    result = _run()
    assert result.returncode == 2
    assert "usage" in (result.stderr + result.stdout).lower()


def test_missing_state_file_created(tmp_path):
    result = _run(*_save_args(tmp_path))
    assert result.returncode == 0, result.stderr
    state_path = tmp_path / "state" / "saved.json"
    assert state_path.exists()
    data = json.loads(state_path.read_text())
    assert data["version"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["url"] == "https://a.example"


def test_duplicate_url_skipped(tmp_path):
    state_path = tmp_path / "state" / "saved.json"
    _write_json(state_path, {
        "version": 1,
        "items": [{
            "url": "https://a.example",
            "title": "Sample Title",
            "summary": "샘플 요약",
            "source": "release_blogs",
            "category": "agent-frameworks",
            "brief_date": "2026-04-16",
            "saved_at": "2026-04-16T10:00:00+09:00",
        }],
    })
    result = _run(*_save_args(tmp_path))
    assert result.returncode == 0
    assert "SKIP" in result.stdout
    data = json.loads(state_path.read_text())
    assert len(data["items"]) == 1


def test_corrupt_state_backed_up(tmp_path):
    state_path = tmp_path / "state" / "saved.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("not json {")
    result = _run(*_save_args(tmp_path))
    assert result.returncode == 0, result.stderr
    backups = list(state_path.parent.glob("saved.json.corrupt-*"))
    assert len(backups) == 1
    data = json.loads(state_path.read_text())
    assert len(data["items"]) == 1


def test_new_category_file_created(tmp_path):
    result = _run(*_save_args(tmp_path))
    assert result.returncode == 0, result.stderr
    md = tmp_path / "saved" / "agent-frameworks.md"
    assert md.exists()
    text = md.read_text()
    assert text.startswith("# agent-frameworks — 저장된 항목")
    assert "Sample Title" in text
    assert "https://a.example" in text
    assert "release_blogs" in text
    assert "2026-04-16" in text


def _count_date_headers(md: str) -> int:
    return sum(1 for line in md.splitlines() if line.startswith("## ") and "저장" in line)


def test_same_day_two_items_single_date_block(tmp_path):
    _run(*_save_args(tmp_path, url="https://a.example", title="First"))
    _run(*_save_args(tmp_path, url="https://b.example", title="Second"))
    md = (tmp_path / "saved" / "agent-frameworks.md").read_text()
    assert _count_date_headers(md) == 1
    first_idx = md.index("First")
    second_idx = md.index("Second")
    assert second_idx < first_idx


def test_different_day_creates_new_date_block(tmp_path):
    saved_dir = tmp_path / "saved"
    saved_dir.mkdir(parents=True)
    (saved_dir / "agent-frameworks.md").write_text(
        "# agent-frameworks — 저장된 항목\n\n"
        "## 2026-04-14 저장\n\n"
        "### Old Title\n"
        "- **요약**: old\n"
        "- **출처**: release_blogs\n"
        "- **brief 날짜**: 2026-04-14\n"
        "- **URL**: https://old.example\n\n"
        "---\n"
    )
    result = _run(*_save_args(tmp_path, url="https://new.example", title="New Today"))
    assert result.returncode == 0, result.stderr
    md = (saved_dir / "agent-frameworks.md").read_text()
    assert _count_date_headers(md) == 2
    new_idx = md.index("New Today")
    old_idx = md.index("Old Title")
    assert new_idx < old_idx


def test_uncategorized_file(tmp_path):
    result = _run(*_save_args(tmp_path, category="uncategorized"))
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "saved" / "uncategorized.md").exists()
