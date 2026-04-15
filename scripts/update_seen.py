"""Update state/seen.json from the day's selected items.

Usage: python scripts/update_seen.py <state_path> <selected_path>
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from pathlib import Path
from typing import Any

WINDOW_DAYS = 7


def _load_state(path: str) -> tuple[dict[str, Any], str | None]:
    p = Path(path)
    if not p.exists():
        return {}, None
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError:
        backup = p.with_suffix(
            p.suffix + f".corrupt-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        shutil.copy(p, backup)
        return {}, str(backup)


def _load_selected(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def update_seen(state_path: str, selected_path: str, today: str) -> dict[str, Any]:
    state, corrupt_backup = _load_state(state_path)
    selected = _load_selected(selected_path)
    today_d = dt.date.fromisoformat(today)

    added = 0
    bumped = 0

    for item in selected:
        url = item.get("url")
        title = item.get("title", "")
        if not url:
            continue
        entry = state.get(url)
        if entry is None:
            state[url] = {
                "first_seen": today,
                "last_seen": today,
                "days": 1,
                "title": title,
            }
            added += 1
            continue
        last = dt.date.fromisoformat(entry["last_seen"])
        gap = (today_d - last).days
        if gap <= 1:
            entry["last_seen"] = today
            entry["days"] = int(entry.get("days", 1)) + (1 if gap == 1 else 0)
            bumped += 1
        else:
            state[url] = {
                "first_seen": today,
                "last_seen": today,
                "days": 1,
                "title": title,
            }
            added += 1

    pruned = 0
    cutoff = today_d - dt.timedelta(days=WINDOW_DAYS)
    for url in list(state.keys()):
        last = dt.date.fromisoformat(state[url]["last_seen"])
        if last < cutoff:
            del state[url]
            pruned += 1

    Path(state_path).write_text(json.dumps(state, ensure_ascii=False, indent=2))

    return {
        "added": added,
        "bumped": bumped,
        "pruned": pruned,
        "corrupt_backup": corrupt_backup,
    }


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: update_seen.py <state_path> <selected_path>", file=sys.stderr)
        return 2
    state_path = sys.argv[1]
    selected_path = sys.argv[2]
    today = dt.date.today().isoformat()
    summary = update_seen(state_path, selected_path, today=today)
    print(
        f"update_seen: added={summary['added']} bumped={summary['bumped']} pruned={summary['pruned']}"
    )
    if summary["corrupt_backup"]:
        print(f"WARNING: corrupt state backed up to {summary['corrupt_backup']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
