"""Append today's TOP 5 URLs to the permanent archive.

Usage: python scripts/archive_top5.py <archive_path> <top5_path>

The archive is permanent — once a URL is in it, the /brief command
filters it out of every future brief. Existing entries are never
overwritten so the original archived_on date is preserved.
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def _load_archive(path: str) -> tuple[dict[str, Any], str | None]:
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


def archive_top5(archive_path: str, top5_path: str, today: str) -> dict[str, Any]:
    archive, corrupt_backup = _load_archive(archive_path)
    items = json.loads(Path(top5_path).read_text())

    added = 0
    skipped = 0
    for item in items:
        url = item.get("url")
        if not url:
            continue
        if url in archive:
            skipped += 1
            continue
        archive[url] = {
            "archived_on": today,
            "title": item.get("title", ""),
        }
        added += 1

    Path(archive_path).write_text(
        json.dumps(archive, ensure_ascii=False, indent=2) + "\n"
    )

    return {"added": added, "skipped": skipped, "corrupt_backup": corrupt_backup}


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: archive_top5.py <archive_path> <top5_path>", file=sys.stderr)
        return 2
    summary = archive_top5(sys.argv[1], sys.argv[2], today=dt.date.today().isoformat())
    print(f"archive_top5: added={summary['added']} skipped={summary['skipped']}")
    if summary["corrupt_backup"]:
        print(f"WARNING: corrupt archive backed up to {summary['corrupt_backup']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
