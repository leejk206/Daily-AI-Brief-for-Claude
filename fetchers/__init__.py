"""Shared helpers for fetchers.

Every fetcher emits a JSON envelope with this shape:

    {
        "source": "<source_name>",
        "fetched_at": "<ISO-8601 with offset>",
        "items": [
            {
                "id": "<stable id>",
                "title": "<string>",
                "url": "<string>",
                "description": "<string>",
                "signals": {<source-specific numeric/string hints>},
                "category_hint": null
            },
            ...
        ]
    }
"""

from __future__ import annotations

import datetime as _dt
from typing import Any


def make_envelope(source: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a canonical envelope. `fetched_at` uses local time with offset."""
    now = _dt.datetime.now().astimezone()
    return {
        "source": source,
        "fetched_at": now.isoformat(timespec="seconds"),
        "items": items,
    }


REQUIRED_ITEM_FIELDS = {"id", "title", "url", "description", "signals", "category_hint"}


def validate_envelope(env: dict[str, Any]) -> None:
    """Raise ValueError if envelope is malformed. Used by tests."""
    if not isinstance(env, dict):
        raise ValueError("envelope must be a dict")
    for key in ("source", "fetched_at", "items"):
        if key not in env:
            raise ValueError(f"envelope missing key: {key}")
    if not isinstance(env["items"], list):
        raise ValueError("items must be a list")
    for i, item in enumerate(env["items"]):
        missing = REQUIRED_ITEM_FIELDS - item.keys()
        if missing:
            raise ValueError(f"item {i} missing fields: {missing}")
