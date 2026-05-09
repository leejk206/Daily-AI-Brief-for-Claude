"""state/tags.json read/write helpers — single-responsibility data layer."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def _empty_state() -> dict[str, Any]:
    return {"version": 1, "items": {}}


def load(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return _empty_state(), None
    try:
        data = json.loads(path.read_text())
        if (
            not isinstance(data, dict)
            or "version" not in data
            or "items" not in data
            or not isinstance(data["items"], dict)
        ):
            raise ValueError("malformed")
        return data, None
    except (json.JSONDecodeError, ValueError):
        ts = dt.datetime.now(KST).strftime("%Y%m%d%H%M%S")
        backup = path.with_suffix(path.suffix + f".corrupt-{ts}")
        shutil.copy(path, backup)
        return _empty_state(), str(backup)


def save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def upsert_item(
    state: dict[str, Any],
    url: str,
    *,
    title: str,
    summary: str,
    category: str,
    source: str,
    brief_date: str,
    tags: list[str],
) -> None:
    """Insert new item or merge tags into existing.

    On update: tags = union(existing, new); brief_date / title / summary /
    category / source preserved (first-touch wins); tagged_at refreshed.
    """
    now = dt.datetime.now(KST).isoformat(timespec="seconds")
    existing = state["items"].get(url)
    if existing is None:
        state["items"][url] = {
            "title": title,
            "summary": summary,
            "category": category,
            "source": source,
            "brief_date": brief_date,
            "tags": sorted(set(tags)),
            "tagged_at": now,
        }
    else:
        merged = sorted(set(existing.get("tags", [])) | set(tags))
        existing["tags"] = merged
        existing["tagged_at"] = now


def get_item(state: dict[str, Any], url: str) -> dict[str, Any] | None:
    """Returns a live reference into state — do not mutate; use upsert_item to write."""
    return state["items"].get(url)
