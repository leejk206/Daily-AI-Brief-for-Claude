"""Anthropic news fetcher.

Anthropic does not publish an RSS feed (the /news/rss.xml path 404s), so we
scrape the public news listing at https://www.anthropic.com/news instead. The
page is a Next.js render; each article is an <a href="/news/..."> card that
contains a title element (class suffix ``__title``), an optional <time> (class
suffix ``__date``), and a body excerpt (class suffix ``__body``). The CSS-module
class names carry a build hash, so we match on the stable suffix rather than the
full class string.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup

from fetchers import make_envelope

LISTING_URL = "https://www.anthropic.com/news"
BASE_URL = "https://www.anthropic.com"
TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
MAX_ITEMS = 25


def fetch_raw() -> bytes:
    resp = requests.get(
        LISTING_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    resp.raise_for_status()
    return resp.content


def _suffix_text(card: Any, suffix: str) -> str:
    """Return text of the first descendant whose class contains ``suffix``."""
    el = card.find(
        lambda tag: any(c.endswith(suffix) for c in (tag.get("class") or []))
    )
    return el.get_text(" ", strip=True) if el else ""


def parse_html(raw: bytes) -> list[dict[str, Any]]:
    try:
        soup = BeautifulSoup(raw, "html.parser")
    except Exception:
        return []
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/news/"):
            continue
        slug = href.rstrip("/").split("/")[-1]
        if not slug or href in seen:
            continue
        title = _suffix_text(a, "__title")
        if not title:
            continue
        seen.add(href)
        url = BASE_URL + href
        published = _suffix_text(a, "__date")
        body = _suffix_text(a, "__body")
        items.append(
            {
                "id": f"anthropic:{slug}",
                "title": title,
                "url": url,
                "description": body[:500],
                "signals": {
                    "vendor": "anthropic",
                    "published": published,
                },
                "category_hint": None,
            }
        )
        if len(items) >= MAX_ITEMS:
            break
    return items


def main() -> int:
    try:
        raw = fetch_raw()
    except Exception as exc:
        print(f"anthropic_news fetch failed: {exc}", file=sys.stderr)
        env = make_envelope("anthropic_news", [])
        print(json.dumps(env, ensure_ascii=False, indent=2))
        return 1
    items = parse_html(raw)
    env = make_envelope("anthropic_news", items)
    print(json.dumps(env, ensure_ascii=False, indent=2))
    return 0 if items else 1


if __name__ == "__main__":
    raise SystemExit(main())
