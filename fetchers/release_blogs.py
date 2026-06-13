"""Release blogs fetcher — parses RSS/Atom from vendor feeds.

Anthropic does not publish an RSS feed at the time of writing. OpenAI and
Google DeepMind both expose working feeds. Add more vendors to FEEDS as
they appear.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import feedparser
import requests

from fetchers import make_envelope

FEEDS = [
    ("openai", "https://openai.com/news/rss.xml"),
    ("deepmind", "https://deepmind.google/blog/rss.xml"),
    ("gemini", "https://blog.google/products/gemini/rss/"),
]

TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (daily-ai-brief)"
MAX_ITEMS_PER_FEED = 20  # feeds are reverse chronological; keep recent items only


def fetch_raw() -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    for label, url in FEEDS:
        try:
            r = requests.get(
                url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, allow_redirects=True
            )
            r.raise_for_status()
            out.append((label, r.content))
        except Exception as exc:
            print(f"release_blogs: {label} failed: {exc}", file=sys.stderr)
    return out


def parse_feed(raw: bytes, source_label: str) -> list[dict[str, Any]]:
    try:
        parsed = feedparser.parse(raw)
    except Exception:
        return []
    if parsed.get("bozo") and not parsed.get("entries"):
        return []
    items: list[dict[str, Any]] = []
    for entry in parsed.get("entries", [])[:MAX_ITEMS_PER_FEED]:
        title = entry.get("title")
        link = entry.get("link")
        if not title or not link:
            continue
        summary = entry.get("summary", "") or entry.get("description", "") or ""
        items.append(
            {
                "id": f"rss:{source_label}:{link}",
                "title": title,
                "url": link,
                "description": summary[:500],
                "signals": {
                    "vendor": source_label,
                    "published": entry.get("published", ""),
                },
                "category_hint": None,
            }
        )
    return items


def build_envelope(items: list[dict[str, Any]]) -> dict[str, Any]:
    return make_envelope("release_blogs", items)


def main() -> int:
    try:
        feeds = fetch_raw()
    except Exception as exc:
        print(f"release_blogs fetch failed: {exc}", file=sys.stderr)
        feeds = []
    all_items: list[dict[str, Any]] = []
    for label, raw in feeds:
        all_items.extend(parse_feed(raw, label))
    env = build_envelope(all_items)
    print(json.dumps(env, ensure_ascii=False, indent=2))
    return 0 if all_items else 1


if __name__ == "__main__":
    raise SystemExit(main())
