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


def test_missing_args_exits_2():
    result = _run()
    assert result.returncode == 2
    assert "usage" in (result.stderr + result.stdout).lower()
