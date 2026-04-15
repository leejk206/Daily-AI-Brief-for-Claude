# daily-ai-brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal CLI-triggered AI trend briefing system (`daily-ai-brief`) with deterministic Python fetchers, a declarative interests file, state-based dedup, and a Claude Code `/brief` slash command that orchestrates the daily pipeline.

**Architecture:** Three layers — (1) deterministic Python fetchers emit structured JSON per source, (2) a seen.json state file tracks 7-day URL history for dedup, (3) a `.claude/commands/brief.md` slash command drives Claude Code to run fetchers, match interests, rank, summarize in Korean, write `brief.md`, update state, and commit. Fetchers are tested with pytest against captured HTML/JSON fixtures — no network in tests.

**Tech Stack:** Python 3.11+, `requests`, `beautifulsoup4`, `feedparser`, `pytest`. No extra packaging (pip + requirements.txt only).

---

## File Structure

Files to create:

- `requirements.txt` — dependencies
- `pytest.ini` — pytest config
- `.gitignore` — venv, pycache, etc.
- `README.md` — usage docs
- `interests.md` — user's 5 interest categories (declarative)
- `fetchers/__init__.py` — shared envelope helper (`make_envelope`, `ItemDict`)
- `fetchers/github_trending.py` — scrape github.com/trending
- `fetchers/hacker_news.py` — hn.algolia.com API
- `fetchers/huggingface.py` — HF trending models + daily papers
- `fetchers/release_blogs.py` — RSS from Anthropic/OpenAI/DeepMind/Meta
- `scripts/__init__.py` — empty
- `scripts/update_seen.py` — seen.json maintenance
- `state/seen.json` — initially `{}`
- `tests/__init__.py` — empty
- `tests/fixtures/github_trending.html` — captured fixture
- `tests/fixtures/hacker_news.json` — captured fixture
- `tests/fixtures/huggingface_models.json` — captured fixture
- `tests/fixtures/huggingface_papers.json` — captured fixture
- `tests/fixtures/anthropic_feed.xml` — captured fixture
- `tests/test_github_trending.py`
- `tests/test_hacker_news.py`
- `tests/test_huggingface.py`
- `tests/test_release_blogs.py`
- `tests/test_update_seen.py`
- `.claude/commands/brief.md` — the `/brief` slash command

Responsibility per file: each fetcher has exactly one `parse(raw_bytes) -> envelope` pure function plus a thin `fetch_raw()` HTTP call plus an `if __name__ == "__main__"` entry point. Tests call `parse()` only. `scripts/update_seen.py` is a pure state-transformation script. `.claude/commands/brief.md` is the orchestration prompt.

---

## Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Write `requirements.txt`**

```
requests==2.32.3
beautifulsoup4==4.12.3
feedparser==6.0.11
pytest==8.3.3
```

- [ ] **Step 2: Write `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -ra --strict-markers
```

- [ ] **Step 3: Write `.gitignore`**

```
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
*.egg-info/
daily/
!daily/.gitkeep
```

Note: `daily/` is gitignored during development but the slash command's commit step will use `git add -f daily/<date>` so archived briefs still get committed.

- [ ] **Step 4: Write `README.md`**

````markdown
# daily-ai-brief

Personal daily AI trend briefing system. Every morning, run `/brief` in Claude Code to get a Korean-language summary of notable items from GitHub Trending, Hacker News, Hugging Face, and official release blogs, filtered and ranked against your declared interests.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## Usage

1. Edit `interests.md` to declare your 5 interest categories with keywords.
2. Open this folder in Claude Code.
3. Type `/brief`. Claude will run the fetchers, match interests, rank, write `daily/<today>/brief.md`, and commit.

## Architecture

See `docs/superpowers/specs/2026-04-15-daily-ai-brief-design.md` for the full design spec.

Three layers:
1. **Fetchers** (Python) — deterministic, produce structured JSON
2. **State** — `state/seen.json` tracks 7-day URL history
3. **Orchestration** — `.claude/commands/brief.md` drives Claude Code

## Running fetchers manually

```bash
python -m fetchers.github_trending
python -m fetchers.hacker_news
python -m fetchers.huggingface
python -m fetchers.release_blogs
```

Each emits a JSON envelope to stdout.
````

- [ ] **Step 5: Commit**

```bash
git add requirements.txt pytest.ini .gitignore README.md
git commit -m "chore: scaffolding"
```

---

## Task 2: `interests.md`

**Files:**
- Create: `interests.md`

- [ ] **Step 1: Write `interests.md`**

```markdown
# My Interests

Claude reads this file at the start of every `/brief` run and uses it to
filter and categorize items from the fetchers. Edit freely — it's data,
not code.

## Categories

### agent-frameworks
Keywords: langgraph, crewai, autogen, claude agent sdk, agent framework, multi-agent, agentic workflow, agent orchestration
Exclude: —

### llm-harness-eval
Keywords: inspect_ai, lm-evaluation-harness, braintrust, eval harness, benchmark suite, leaderboard, model evaluation
Exclude: blockchain, crypto

### mcp
Keywords: model context protocol, mcp server, mcp client, mcp tool, mcp registry
Exclude: —

### coding-agents
Keywords: claude code, cursor, windsurf, aider, coding agent, pair programming AI, IDE assistant, code generation agent
Exclude: —

### prompt-context-engineering
Keywords: prompt engineering, context engineering, system prompt, prompting technique, context window, RAG retrieval strategy, long-context
Exclude: midjourney, image prompt, stable diffusion prompt

## Global exclude
NFT, airdrop, token sale, meme coin, rug pull
```

- [ ] **Step 2: Commit**

```bash
git add interests.md
git commit -m "feat: declare interests"
```

---

## Task 3: Shared envelope helper

**Files:**
- Create: `fetchers/__init__.py`

- [ ] **Step 1: Write `fetchers/__init__.py`**

```python
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
```

- [ ] **Step 2: Create empty `tests/__init__.py` and `scripts/__init__.py`**

```bash
touch tests/__init__.py scripts/__init__.py
```

- [ ] **Step 3: Commit**

```bash
git add fetchers/__init__.py tests/__init__.py scripts/__init__.py
git commit -m "feat: shared envelope helper"
```

---

## Task 4: `github_trending` fetcher

**Files:**
- Create: `tests/fixtures/github_trending.html`
- Create: `tests/test_github_trending.py`
- Create: `fetchers/github_trending.py`

- [ ] **Step 1: Capture fixture**

```bash
curl -sS -A "Mozilla/5.0" "https://github.com/trending?since=daily" > tests/fixtures/github_trending.html
wc -c tests/fixtures/github_trending.html
```
Expected: a file of 50KB–500KB. If the download is empty or tiny, retry.

- [ ] **Step 2: Write the failing test**

`tests/test_github_trending.py`:
```python
from pathlib import Path

from fetchers import validate_envelope
from fetchers.github_trending import parse

FIXTURE = Path(__file__).parent / "fixtures" / "github_trending.html"


def test_parse_returns_valid_envelope():
    env = parse(FIXTURE.read_bytes())
    validate_envelope(env)
    assert env["source"] == "github_trending"
    assert len(env["items"]) > 0


def test_items_have_github_fields():
    env = parse(FIXTURE.read_bytes())
    for item in env["items"]:
        assert item["url"].startswith("https://github.com/")
        assert "/" in item["title"]  # owner/repo
        assert "stars" in item["signals"]
        assert isinstance(item["signals"]["stars"], int)


def test_top_item_has_nonempty_description():
    env = parse(FIXTURE.read_bytes())
    non_empty = [i for i in env["items"] if i["description"]]
    assert len(non_empty) >= 1  # at least one repo has a description


def test_empty_html_returns_empty_items():
    env = parse(b"<html><body></body></html>")
    validate_envelope(env)
    assert env["items"] == []
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_github_trending.py -v
```
Expected: FAIL — `ModuleNotFoundError: fetchers.github_trending`.

- [ ] **Step 4: Implement `fetchers/github_trending.py`**

```python
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
    return int(s.replace(",", "").strip() or 0)


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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_github_trending.py -v
```
Expected: all 4 tests PASS. If `test_items_have_github_fields` fails because GitHub changed their HTML selectors, adjust the selectors in `parse()` and rerun.

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/github_trending.html tests/test_github_trending.py fetchers/github_trending.py
git commit -m "feat: github trending fetcher"
```

---

## Task 5: `hacker_news` fetcher

**Files:**
- Create: `tests/fixtures/hacker_news.json`
- Create: `tests/test_hacker_news.py`
- Create: `fetchers/hacker_news.py`

- [ ] **Step 1: Capture fixture**

```bash
curl -sS "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30" > tests/fixtures/hacker_news.json
python -c "import json; d=json.load(open('tests/fixtures/hacker_news.json')); print('hits:', len(d['hits']))"
```
Expected: `hits: 30` (or close to it).

- [ ] **Step 2: Write the failing test**

`tests/test_hacker_news.py`:
```python
from pathlib import Path

from fetchers import validate_envelope
from fetchers.hacker_news import parse

FIXTURE = Path(__file__).parent / "fixtures" / "hacker_news.json"


def test_parse_returns_valid_envelope():
    env = parse(FIXTURE.read_bytes())
    validate_envelope(env)
    assert env["source"] == "hacker_news"
    assert len(env["items"]) > 0


def test_items_have_hn_fields():
    env = parse(FIXTURE.read_bytes())
    for item in env["items"]:
        assert item["id"].startswith("hn:")
        assert "points" in item["signals"]
        assert "num_comments" in item["signals"]
        assert isinstance(item["signals"]["points"], int)


def test_url_fallback_to_hn_discussion():
    """If a story has no external URL, the HN discussion link is used."""
    env = parse(FIXTURE.read_bytes())
    for item in env["items"]:
        assert item["url"].startswith("http")


def test_empty_json_returns_empty_items():
    env = parse(b'{"hits": []}')
    validate_envelope(env)
    assert env["items"] == []
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_hacker_news.py -v
```
Expected: FAIL — `ModuleNotFoundError: fetchers.hacker_news`.

- [ ] **Step 4: Implement `fetchers/hacker_news.py`**

```python
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
                "description": "",  # HN titles are the whole story
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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_hacker_news.py -v
```
Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/hacker_news.json tests/test_hacker_news.py fetchers/hacker_news.py
git commit -m "feat: hacker news fetcher"
```

---

## Task 6: `huggingface` fetcher

**Files:**
- Create: `tests/fixtures/huggingface_models.json`
- Create: `tests/fixtures/huggingface_papers.json`
- Create: `tests/test_huggingface.py`
- Create: `fetchers/huggingface.py`

- [ ] **Step 1: Capture fixtures**

```bash
curl -sS "https://huggingface.co/api/models?sort=trendingScore&limit=20" > tests/fixtures/huggingface_models.json
curl -sS "https://huggingface.co/api/daily_papers" > tests/fixtures/huggingface_papers.json
python -c "import json; print('models:', len(json.load(open('tests/fixtures/huggingface_models.json')))); print('papers:', len(json.load(open('tests/fixtures/huggingface_papers.json'))))"
```
Expected: both > 0. If the papers endpoint returns 404, try `https://huggingface.co/api/daily_papers?date=2026-04-15` (today) and note the correct URL in the fetcher.

- [ ] **Step 2: Write the failing test**

`tests/test_huggingface.py`:
```python
from pathlib import Path

from fetchers import validate_envelope
from fetchers.huggingface import parse

FIX_MODELS = Path(__file__).parent / "fixtures" / "huggingface_models.json"
FIX_PAPERS = Path(__file__).parent / "fixtures" / "huggingface_papers.json"


def test_parse_returns_valid_envelope():
    env = parse(FIX_MODELS.read_bytes(), FIX_PAPERS.read_bytes())
    validate_envelope(env)
    assert env["source"] == "huggingface"
    assert len(env["items"]) > 0


def test_items_tagged_by_type():
    env = parse(FIX_MODELS.read_bytes(), FIX_PAPERS.read_bytes())
    types = {item["signals"].get("type") for item in env["items"]}
    assert "model" in types
    # Papers endpoint may be empty on some days — only assert if present
    if any(i["signals"].get("type") == "paper" for i in env["items"]):
        assert "paper" in types


def test_model_items_have_url():
    env = parse(FIX_MODELS.read_bytes(), FIX_PAPERS.read_bytes())
    models = [i for i in env["items"] if i["signals"].get("type") == "model"]
    assert len(models) > 0
    for m in models:
        assert m["url"].startswith("https://huggingface.co/")


def test_empty_inputs_return_empty_items():
    env = parse(b"[]", b"[]")
    validate_envelope(env)
    assert env["items"] == []
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_huggingface.py -v
```
Expected: FAIL — module not found.

- [ ] **Step 4: Implement `fetchers/huggingface.py`**

```python
"""Hugging Face fetcher — trending models + daily papers."""

from __future__ import annotations

import json
import sys
from typing import Any

import requests

from fetchers import make_envelope

MODELS_URL = "https://huggingface.co/api/models?sort=trendingScore&limit=20"
PAPERS_URL = "https://huggingface.co/api/daily_papers"
TIMEOUT = 30


def fetch_raw() -> tuple[bytes, bytes]:
    m = requests.get(MODELS_URL, timeout=TIMEOUT)
    m.raise_for_status()
    try:
        p = requests.get(PAPERS_URL, timeout=TIMEOUT)
        p.raise_for_status()
        papers_content = p.content
    except Exception:
        papers_content = b"[]"
    return m.content, papers_content


def _parse_models(raw: bytes) -> list[dict[str, Any]]:
    data = json.loads(raw)
    items: list[dict[str, Any]] = []
    for m in data:
        model_id = m.get("id") or m.get("modelId")
        if not model_id:
            continue
        downloads = int(m.get("downloads") or 0)
        likes = int(m.get("likes") or 0)
        pipeline = m.get("pipeline_tag") or ""
        items.append(
            {
                "id": f"hf-model:{model_id}",
                "title": model_id,
                "url": f"https://huggingface.co/{model_id}",
                "description": pipeline,
                "signals": {
                    "type": "model",
                    "downloads": downloads,
                    "likes": likes,
                    "pipeline": pipeline,
                },
                "category_hint": None,
            }
        )
    return items


def _parse_papers(raw: bytes) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    items: list[dict[str, Any]] = []
    for p in data:
        paper = p.get("paper") if isinstance(p, dict) else None
        if not paper:
            continue
        arxiv_id = paper.get("id")
        title = paper.get("title")
        summary = paper.get("summary") or ""
        upvotes = int(paper.get("upvotes") or 0)
        if not arxiv_id or not title:
            continue
        items.append(
            {
                "id": f"hf-paper:{arxiv_id}",
                "title": title,
                "url": f"https://huggingface.co/papers/{arxiv_id}",
                "description": summary[:300],
                "signals": {
                    "type": "paper",
                    "upvotes": upvotes,
                    "arxiv_id": arxiv_id,
                },
                "category_hint": None,
            }
        )
    return items


def parse(models_raw: bytes, papers_raw: bytes) -> dict[str, Any]:
    items = _parse_models(models_raw) + _parse_papers(papers_raw)
    return make_envelope("huggingface", items)


def main() -> int:
    try:
        models_raw, papers_raw = fetch_raw()
        env = parse(models_raw, papers_raw)
    except Exception as exc:
        print(f"huggingface fetch failed: {exc}", file=sys.stderr)
        env = make_envelope("huggingface", [])
        print(json.dumps(env, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(env, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_huggingface.py -v
```
Expected: all 4 tests PASS. If the papers endpoint returned HTML instead of JSON (fixture capture failure), recapture with the dated URL.

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/huggingface_models.json tests/fixtures/huggingface_papers.json tests/test_huggingface.py fetchers/huggingface.py
git commit -m "feat: huggingface fetcher"
```

---

## Task 7: `release_blogs` fetcher

**Files:**
- Create: `tests/fixtures/anthropic_feed.xml`
- Create: `tests/test_release_blogs.py`
- Create: `fetchers/release_blogs.py`

- [ ] **Step 1: Probe RSS URLs and capture at least one working fixture**

Try each candidate URL; capture the first one that returns valid RSS/Atom:

```bash
for url in \
  "https://www.anthropic.com/news/rss.xml" \
  "https://www.anthropic.com/rss.xml" \
  "https://www.anthropic.com/news/feed.xml" \
  "https://openai.com/blog/rss.xml" \
  "https://deepmind.google/blog/rss.xml"; do
    code=$(curl -sS -o /dev/null -w '%{http_code}' "$url")
    echo "$code $url"
done
```

Capture the first Anthropic candidate that returns 200:

```bash
curl -sS "https://www.anthropic.com/news/rss.xml" > tests/fixtures/anthropic_feed.xml
head -20 tests/fixtures/anthropic_feed.xml
```

If none of the Anthropic URLs work, capture OpenAI's or DeepMind's instead and rename the fixture accordingly. Document the working URLs in `README.md` and update the fetcher constants.

- [ ] **Step 2: Write the failing test**

`tests/test_release_blogs.py`:
```python
from pathlib import Path

from fetchers import validate_envelope
from fetchers.release_blogs import parse_feed, build_envelope

FIXTURE = Path(__file__).parent / "fixtures" / "anthropic_feed.xml"


def test_parse_feed_returns_items():
    items = parse_feed(FIXTURE.read_bytes(), source_label="anthropic")
    assert len(items) > 0
    for item in items:
        assert item["url"].startswith("http")
        assert item["title"]
        assert item["signals"]["vendor"] == "anthropic"


def test_build_envelope_wraps_items():
    items = parse_feed(FIXTURE.read_bytes(), source_label="anthropic")
    env = build_envelope(items)
    validate_envelope(env)
    assert env["source"] == "release_blogs"


def test_malformed_feed_returns_empty_list():
    items = parse_feed(b"<not-xml>", source_label="anthropic")
    assert items == []
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_release_blogs.py -v
```
Expected: FAIL — module not found.

- [ ] **Step 4: Implement `fetchers/release_blogs.py`**

```python
"""Release blogs fetcher — parses RSS/Atom from vendor feeds."""

from __future__ import annotations

import json
import sys
from typing import Any

import feedparser
import requests

from fetchers import make_envelope

FEEDS = [
    ("anthropic", "https://www.anthropic.com/news/rss.xml"),
    ("openai", "https://openai.com/blog/rss.xml"),
    ("deepmind", "https://deepmind.google/blog/rss.xml"),
]

TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (daily-ai-brief)"


def fetch_raw() -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    for label, url in FEEDS:
        try:
            r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
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
    for entry in parsed.get("entries", []):
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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_release_blogs.py -v
```
Expected: all 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/anthropic_feed.xml tests/test_release_blogs.py fetchers/release_blogs.py
git commit -m "feat: release blogs fetcher"
```

---

## Task 8: `update_seen.py` state script

**Files:**
- Create: `state/seen.json`
- Create: `tests/test_update_seen.py`
- Create: `scripts/update_seen.py`

- [ ] **Step 1: Initialize empty state file**

```bash
echo '{}' > state/seen.json
```

- [ ] **Step 2: Write the failing test**

`tests/test_update_seen.py`:
```python
import json
from pathlib import Path

from scripts.update_seen import update_seen


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def test_new_item_added(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text("{}")
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([
        {"url": "https://a.example", "title": "A"},
    ]))
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    assert summary["added"] == 1
    data = _load(state)
    assert data["https://a.example"]["days"] == 1
    assert data["https://a.example"]["first_seen"] == "2026-04-15"
    assert data["https://a.example"]["last_seen"] == "2026-04-15"


def test_bumped_when_seen_yesterday(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text(json.dumps({
        "https://a.example": {
            "first_seen": "2026-04-13",
            "last_seen": "2026-04-14",
            "days": 2,
            "title": "A",
        }
    }))
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([{"url": "https://a.example", "title": "A"}]))
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    assert summary["bumped"] == 1
    data = _load(state)
    assert data["https://a.example"]["days"] == 3
    assert data["https://a.example"]["last_seen"] == "2026-04-15"


def test_reset_on_gap(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text(json.dumps({
        "https://a.example": {
            "first_seen": "2026-04-10",
            "last_seen": "2026-04-12",
            "days": 2,
            "title": "A",
        }
    }))
    selected = tmp_path / "selected.json"
    selected.write_text(json.dumps([{"url": "https://a.example", "title": "A"}]))
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    # Gap of 3 days → treated as resurfaced, reset to day 1
    data = _load(state)
    assert data["https://a.example"]["days"] == 1
    assert data["https://a.example"]["first_seen"] == "2026-04-15"
    assert summary["added"] == 1


def test_prune_older_than_7_days(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text(json.dumps({
        "https://old.example": {
            "first_seen": "2026-04-01",
            "last_seen": "2026-04-07",
            "days": 5,
            "title": "Old",
        },
        "https://fresh.example": {
            "first_seen": "2026-04-14",
            "last_seen": "2026-04-14",
            "days": 1,
            "title": "Fresh",
        },
    }))
    selected = tmp_path / "selected.json"
    selected.write_text("[]")
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    data = _load(state)
    assert "https://old.example" not in data
    assert "https://fresh.example" in data
    assert summary["pruned"] == 1


def test_corrupt_state_backed_up(tmp_path):
    state = tmp_path / "seen.json"
    state.write_text("not json")
    selected = tmp_path / "selected.json"
    selected.write_text("[]")
    summary = update_seen(str(state), str(selected), today="2026-04-15")
    # Should not raise; should reset state
    assert summary["corrupt_backup"] is not None
    assert Path(summary["corrupt_backup"]).exists()
    data = _load(state)
    assert data == {}
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_update_seen.py -v
```
Expected: FAIL — `ModuleNotFoundError: scripts.update_seen`.

- [ ] **Step 4: Implement `scripts/update_seen.py`**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_update_seen.py -v
```
Expected: all 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add state/seen.json tests/test_update_seen.py scripts/update_seen.py
git commit -m "feat: seen.json state management"
```

---

## Task 9: `/brief` slash command

**Files:**
- Create: `.claude/commands/brief.md`

- [ ] **Step 1: Write the slash command**

`.claude/commands/brief.md`:

````markdown
---
description: Generate today's AI trend brief for daily-ai-brief
---

You are running the `/brief` command for `daily-ai-brief`. Follow this procedure exactly.

## Step 1 — Prep
- Compute `TODAY` = today's date in `YYYY-MM-DD` format (Asia/Seoul).
- If `daily/$TODAY/brief.md` already exists, ask the user whether to overwrite. If they decline, abort.
- Create `daily/$TODAY/raw/` if it doesn't exist.

## Step 2 — Run fetchers in parallel
Issue these four Bash commands in parallel (single message, multiple tool calls):

```
python -m fetchers.github_trending > daily/$TODAY/raw/github_trending.json
python -m fetchers.hacker_news > daily/$TODAY/raw/hacker_news.json
python -m fetchers.huggingface > daily/$TODAY/raw/huggingface.json
python -m fetchers.release_blogs > daily/$TODAY/raw/release_blogs.json
```

Each fetcher has a 60-second timeout. If a fetcher exits non-zero, note the source as `unavailable` but continue. If all four fail, abort with a message to the user.

## Step 3 — Read context
Read these files:
- `interests.md`
- `state/seen.json` (treat missing file or empty object as `{}`)
- All four raw JSON files from `daily/$TODAY/raw/`

## Step 4 — Filter by interests
For each item across all four envelopes:
- Check if it matches any of the five categories in `interests.md`.
- Use keyword matching as a first pass, then apply semantic judgment. A hit on the single word "agent" is NOT enough — require a phrase like "agent framework", "multi-agent", or an explicit category keyword.
- Respect each category's `Exclude` list and the `Global exclude` list.
- Record the matched category for each kept item.

## Step 5 — Annotate dedup state
For each kept item, look up its URL in `seen.json`:
- Not present → mark as `new`.
- Present with `last_seen` ≥ yesterday → mark as `day N` where `N = days + 1`.
- Present but older (gap ≥ 2 days) → treat as `new` (resurfaced).

## Step 6 — Select TOP 5
Apply these criteria in order:
1. Multi-source signal — an item appearing in 2+ sources today ranks highest.
2. Category diversity — avoid 5 items from one category; aim for 3–4 categories represented.
3. Interest relevance — weight by how many keywords hit.
4. Freshness — `new` > `day 2` > `day 3+`.
Items already at `day 3+` must not enter TOP 5 unless they represent a genuinely breaking update (e.g., a new sub-release).

## Step 7 — Write `brief.md`
Write to `daily/$TODAY/brief.md` using this exact template (fill the placeholders):

```markdown
# $TODAY AI 트렌드 브리프

## 🔥 오늘의 TOP 5

1. **<title>** — <한 줄 해설: 왜 중요한가 (Korean, ~40 chars)>
   sources: <comma-separated source names>
   <url>

2. ...

## 📋 카테고리별 나머지

### 에이전트 프레임워크
- **<title>** [<source>] — <1줄 한국어 요약> (<new | day N>)
  <url>

### LLM 하네스·평가
- ...

### MCP
- ...

### 코딩 에이전트
- ...

### 프롬프트·컨텍스트 엔지니어링
- ...

## 📌 Still trending (day 2+)
- **<title>** [day N] — <short reminder>
  <url>

## ⚠️ 소스 상태
- github_trending: ok (N items / M matched)
- hacker_news: ok (N items / M matched)
- huggingface: ok (N items / M matched)
- release_blogs: ok (N items / M matched)
```

Rules:
- All summaries and commentary in Korean.
- URLs on their own line.
- Skip any empty category section.
- If no items match interests at all, write a fallback section listing the raw top 3 of each source.

## Step 8 — Save selected items
Write `daily/$TODAY/selected.json` — a JSON array of all items included in the brief (both TOP 5 and carousels), each as `{"url": "...", "title": "..."}`.

## Step 9 — Update state
Run: `python scripts/update_seen.py state/seen.json daily/$TODAY/selected.json`

## Step 10 — Commit
```
git add -f daily/$TODAY
git add state/seen.json
git commit -m "brief: $TODAY"
```

## Step 11 — Report
Tell the user: "Brief written to daily/$TODAY/brief.md — TOP 5 + N carousel items. Source status: ..."
````

- [ ] **Step 2: Commit**

```bash
git add .claude/commands/brief.md
git commit -m "feat: /brief slash command"
```

---

## Task 10: End-to-end verification

**Files:**
- (No new code — verification only)

- [ ] **Step 1: Install dependencies and run full test suite**

```bash
cd /home/ljk9121/projects/daily-ai-brief
python -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
pytest -v
```
Expected: all tests PASS (≥20 tests across 5 test files).

- [ ] **Step 2: Run each fetcher end-to-end and inspect JSON**

```bash
source .venv/bin/activate
mkdir -p /tmp/daily-ai-brief-smoke/raw
python -m fetchers.github_trending > /tmp/daily-ai-brief-smoke/raw/github_trending.json
python -m fetchers.hacker_news > /tmp/daily-ai-brief-smoke/raw/hacker_news.json
python -m fetchers.huggingface > /tmp/daily-ai-brief-smoke/raw/huggingface.json
python -m fetchers.release_blogs > /tmp/daily-ai-brief-smoke/raw/release_blogs.json
python -c "
import json, pathlib
for p in pathlib.Path('/tmp/daily-ai-brief-smoke/raw').glob('*.json'):
    d = json.loads(p.read_text())
    print(f'{p.name}: source={d[\"source\"]} items={len(d[\"items\"])}')"
```
Expected: each fetcher prints an envelope with ≥1 item (except possibly `release_blogs` if all vendor feeds are down). `huggingface` should have ≥15 items.

- [ ] **Step 3: Dry-run `update_seen.py`**

```bash
echo '[{"url": "https://example.com/a", "title": "A"}]' > /tmp/selected.json
python scripts/update_seen.py /tmp/smoke-seen.json /tmp/selected.json 2>&1 || true
# Initialize empty first
echo '{}' > /tmp/smoke-seen.json
python scripts/update_seen.py /tmp/smoke-seen.json /tmp/selected.json
cat /tmp/smoke-seen.json
```
Expected: state file contains the URL with `days: 1`.

- [ ] **Step 4: Final commit with verification note**

```bash
cd /home/ljk9121/projects/daily-ai-brief
git log --oneline
```
Expected: 10+ commits showing the progression from scaffolding → each fetcher → state → slash command.

- [ ] **Step 5: Clean up smoke test artifacts**

```bash
rm -rf /tmp/daily-ai-brief-smoke /tmp/selected.json /tmp/smoke-seen.json
```

---

## Success criteria

- `pytest -v` passes with at least 20 tests green
- All four fetchers produce valid JSON envelopes when run against live sources (any one vendor feed failure in `release_blogs` is acceptable)
- `update_seen.py` correctly handles new / bumped / reset / prune / corrupt cases
- `/brief` slash command file exists at `.claude/commands/brief.md` and specifies the full 11-step workflow
- `interests.md` is declarative markdown the user can edit without touching code
- Git log shows per-component commits
