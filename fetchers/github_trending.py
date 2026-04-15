"""GitHub Trending fetcher. Scrapes https://github.com/trending."""

from __future__ import annotations

import json
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup

from fetchers import make_envelope

URL = "https://github.com/trending?since=daily"
USER_AGENT = "Mozilla/5.0 (daily-ai-brief)"
TIMEOUT = 30


def fetch_raw() -> bytes:
    resp = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.content


def _parse_int(s: str) -> int:
    cleaned = s.replace(",", "").strip()
    if not cleaned:
        return 0
    try:
        return int(cleaned)
    except ValueError:
        return 0


def parse(raw: bytes) -> dict[str, Any]:
    soup = BeautifulSoup(raw, "html.parser")
    items: list[dict[str, Any]] = []
    for article in soup.select("article.Box-row"):
        h2 = article.select_one("h2 a")
        if not h2:
            continue
        slug = h2.get_text(strip=True).replace("\n", "").replace(" ", "")
        if "/" not in slug:
            continue
        url = "https://github.com" + h2.get("href", "")
        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""
        lang_el = article.select_one('[itemprop="programmingLanguage"]')
        language = lang_el.get_text(strip=True) if lang_el else ""
        star_els = article.select('a[href$="/stargazers"]')
        stars = _parse_int(star_els[0].get_text()) if star_els else 0
        star_today_el = article.select_one("span.d-inline-block.float-sm-right")
        stars_today = 0
        if star_today_el:
            txt = star_today_el.get_text(strip=True)
            digits = "".join(c for c in txt if c.isdigit() or c == ",")
            stars_today = _parse_int(digits) if digits else 0
        items.append(
            {
                "id": f"github:{slug}",
                "title": slug,
                "url": url,
                "description": description,
                "signals": {
                    "stars": stars,
                    "stars_today": stars_today,
                    "language": language,
                },
                "category_hint": None,
            }
        )
    return make_envelope("github_trending", items)


def main() -> int:
    try:
        raw = fetch_raw()
        env = parse(raw)
    except Exception as exc:
        print(f"github_trending fetch failed: {exc}", file=sys.stderr)
        env = make_envelope("github_trending", [])
        print(json.dumps(env, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(env, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
