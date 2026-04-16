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
