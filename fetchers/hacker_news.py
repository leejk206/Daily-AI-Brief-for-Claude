"""Hacker News fetcher via Algolia API."""

from __future__ import annotations

import json
import sys
from typing import Any

import requests

from fetchers import make_envelope

URL = "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"
TIMEOUT = 30


def fetch_raw() -> bytes:
    resp = requests.get(URL, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.content


def parse(raw: bytes) -> dict[str, Any]:
    data = json.loads(raw)
    items: list[dict[str, Any]] = []
    for hit in data.get("hits", []):
        obj_id = hit.get("objectID")
        if not obj_id:
            continue
        title = hit.get("title") or hit.get("story_title") or ""
        if not title:
            continue
        external = hit.get("url") or hit.get("story_url")
        discussion = f"https://news.ycombinator.com/item?id={obj_id}"
        url = external or discussion
        points = int(hit.get("points") or 0)
        num_comments = int(hit.get("num_comments") or 0)
        items.append(
            {
                "id": f"hn:{obj_id}",
                "title": title,
                "url": url,
                "description": "",
                "signals": {
                    "points": points,
                    "num_comments": num_comments,
                    "discussion_url": discussion,
                },
                "category_hint": None,
            }
        )
    return make_envelope("hacker_news", items)


def main() -> int:
    try:
        raw = fetch_raw()
        env = parse(raw)
    except Exception as exc:
        print(f"hacker_news fetch failed: {exc}", file=sys.stderr)
        env = make_envelope("hacker_news", [])
        print(json.dumps(env, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(env, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
