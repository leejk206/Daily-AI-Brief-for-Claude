"""DCInside '특이점이 온다' minor gallery fetcher.

DCInside no longer exposes an RSS feed, so we scrape the recommended-posts
(개념글) listing of the thesingularity minor gallery. The recommended filter
(``exception_mode=recommend``) is much higher signal than the full board, but
it is still a community forum: expect memes and chatter. The brief command is
responsible for curating these into a separate community section — this fetcher
just emits the recommended rows with their engagement signals.

DCInside blocks non-browser clients, so a desktop browser User-Agent plus a
Referer header are required to get a 200.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup

from fetchers import make_envelope

GALLERY_ID = "thesingularity"
LISTING_URL = (
    "https://gall.dcinside.com/mgallery/board/lists/"
    f"?id={GALLERY_ID}&exception_mode=recommend"
)
BASE_URL = "https://gall.dcinside.com"
TIMEOUT = 30
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
MAX_ITEMS = 30


def fetch_raw() -> bytes:
    resp = requests.get(
        LISTING_URL,
        headers={"User-Agent": USER_AGENT, "Referer": BASE_URL + "/"},
        timeout=TIMEOUT,
        allow_redirects=True,
    )
    resp.raise_for_status()
    return resp.content


def _int(text: str) -> int:
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def parse_html(raw: bytes) -> list[dict[str, Any]]:
    try:
        soup = BeautifulSoup(raw, "html.parser")
    except Exception:
        return []
    items: list[dict[str, Any]] = []
    for row in soup.select("tr.ub-content.us-post"):
        # Skip pinned notices / setup rows — keep only real recommended posts.
        if row.get("data-type") == "icon_notice":
            continue
        a = row.select_one(".gall_tit a")
        if not a or not a.get("href"):
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        href = a["href"]
        url = href if href.startswith("http") else BASE_URL + href
        num_el = row.select_one(".gall_num")
        post_no = num_el.get_text(strip=True) if num_el else ""
        rec_el = row.select_one(".gall_recommend")
        reply_el = row.select_one(".reply_num")
        views_el = row.select_one(".gall_count")
        items.append(
            {
                "id": f"dcinside:{post_no or url}",
                "title": title,
                "url": url,
                "description": "",
                "signals": {
                    "gallery": GALLERY_ID,
                    "recommend": _int(rec_el.get_text() if rec_el else ""),
                    "replies": _int(reply_el.get_text() if reply_el else ""),
                    "views": _int(views_el.get_text() if views_el else ""),
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
        print(f"dcinside fetch failed: {exc}", file=sys.stderr)
        env = make_envelope("dcinside", [])
        print(json.dumps(env, ensure_ascii=False, indent=2))
        return 1
    items = parse_html(raw)
    env = make_envelope("dcinside", items)
    print(json.dumps(env, ensure_ascii=False, indent=2))
    return 0 if items else 1


if __name__ == "__main__":
    raise SystemExit(main())
