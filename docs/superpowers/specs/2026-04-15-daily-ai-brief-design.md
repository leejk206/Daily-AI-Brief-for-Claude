# daily-ai-brief — Design Spec

- **Date:** 2026-04-15
- **Author:** ljk9121 (with Claude Code brainstorming)
- **Status:** Approved for implementation

## 1. Goals & Scope

`daily-ai-brief` is a personal CLI-triggered AI trend briefing system. Every morning the user runs `/brief` in Claude Code and receives a Korean-language summary of notable items from four sources across five interest areas (agent frameworks, LLM eval harnesses, MCP, coding agents, prompt/context engineering). The system doubles as a portfolio piece for AI orchestrator / harness engineer job preparation: it deliberately showcases the separation between deterministic fetchers and LLM-judgment orchestration, a declarative interests file, state-based dedup, and fixture-based fetcher tests.

**In-scope (MVP):**
- Four sources: GitHub Trending, Hacker News (Algolia API), Hugging Face trending, official release RSS (Anthropic, OpenAI, Google DeepMind, Meta AI)
- Deterministic Python fetchers producing structured JSON
- Declarative `interests.md` edited by the user
- `/brief` slash command orchestrated by Claude Code: filtering, ranking, summarizing, writing, committing
- 7-day dedup with "still trending (day N)" annotation via `state/seen.json`
- Daily archival: `daily/YYYY-MM-DD/{raw/*.json, brief.md}`
- Fixture-based pytest for every fetcher
- Local git repo, daily commits

**Out-of-scope (MVP):**
- Schedulers, cron, notifications, email, web UI
- X/Twitter, Reddit, arXiv, Discord, HF Spaces as standalone sources
- Multi-agent orchestration (L4) — reserved for post-MVP expansion
- CI, automatic deployment

## 2. Architecture

### Layered design

```
Layer 1 — Deterministic Fetchers (Python)
  fetchers/{github_trending,hacker_news,huggingface,release_blogs}.py
  · Each is a runnable script: `python -m fetchers.<name>` → stdout JSON
  · No LLM involvement, no conditional logic about relevance
  · Emits schema-conformant JSON to daily/<date>/raw/<name>.json

Layer 2 — State (Deterministic)
  state/seen.json — 7-day URL history with first_seen / last_seen / days counter
  scripts/update_seen.py — updates seen.json from the day's brief

Layer 3 — Orchestration (Claude Code slash command)
  .claude/commands/brief.md — the /brief prompt
  · Runs fetchers, reads raw JSON + interests.md + seen.json
  · Matches interests, dedups, annotates still-trending items
  · Selects TOP 5 with "why it matters" commentary
  · Groups rest by category
  · Writes brief.md, updates seen.json, commits
```

### Core principles

1. **Deterministic / LLM split** — fetchers never see a prompt; LLM never sees raw HTML. This boundary is the whole point of the system architecturally and the main portfolio talking point.
2. **Interests are data, not code** — `interests.md` defines the five categories with keywords and exclusion terms. Changing interests never requires code edits.
3. **Reproducibility** — `daily/<date>/raw/*.json` is sufficient to re-generate that day's brief without hitting the network.
4. **Claude Code is the planner** — `/brief` is a hand-off of one day's work, not a text generator. It runs subprocesses, reads files, makes judgments, writes files, and commits.

### Directory layout

```
daily-ai-brief/
├── .claude/commands/brief.md
├── fetchers/
│   ├── __init__.py
│   ├── github_trending.py
│   ├── hacker_news.py
│   ├── huggingface.py
│   └── release_blogs.py
├── tests/
│   ├── fixtures/
│   │   ├── github_trending.html
│   │   ├── hacker_news_algolia.json
│   │   ├── huggingface_models.json
│   │   ├── huggingface_papers.json
│   │   └── anthropic_feed.xml
│   └── test_fetchers.py
├── scripts/update_seen.py
├── state/seen.json
├── daily/YYYY-MM-DD/{raw/*.json, brief.md}
├── docs/superpowers/specs/2026-04-15-daily-ai-brief-design.md
├── interests.md
├── requirements.txt
├── pytest.ini
├── README.md
└── .gitignore
```

## 3. Components

### 3.1 `interests.md`

User-editable markdown. Structured so both human and Claude can read it unambiguously.

```markdown
# My Interests

## Categories

### agent-frameworks
Keywords: langgraph, crewai, autogen, claude agent sdk, agent framework, multi-agent, agentic
Exclude: —

### llm-harness-eval
Keywords: inspect_ai, lm-evaluation-harness, braintrust, eval, benchmark, harness, leaderboard
Exclude: blockchain, crypto

### mcp
Keywords: model context protocol, mcp server, mcp client, mcp tool
Exclude: —

### coding-agents
Keywords: claude code, cursor, windsurf, aider, coding agent, pair programming, IDE assistant
Exclude: —

### prompt-context-engineering
Keywords: prompt engineering, context engineering, system prompt, prompting, context window, RAG retrieval strategy
Exclude: midjourney, image prompt, stable diffusion prompt

## Global exclude
NFT, airdrop, token sale, meme coin
```

Claude reads this file at the start of every `/brief` run and uses it to filter and categorize.

### 3.2 Fetchers

Each fetcher is a Python module runnable via `python -m fetchers.<name>`. All emit JSON to stdout conforming to a shared envelope:

```json
{
  "source": "github_trending",
  "fetched_at": "2026-04-15T09:00:00+09:00",
  "items": [
    {
      "id": "github:owner/repo",
      "title": "owner/repo",
      "url": "https://github.com/owner/repo",
      "description": "...",
      "signals": {"stars": 12345, "stars_today": 320, "language": "Python"},
      "category_hint": null
    }
  ]
}
```

- **`github_trending.py`** — scrapes `https://github.com/trending?since=daily`, extracts top 25 repos. Uses `requests` + `beautifulsoup4`. Retry 3x with backoff.
- **`hacker_news.py`** — queries `https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30`, plus a second query with `numericFilters=created_at_i>{24h ago}` for fresh posts. Merges and dedups by `objectID`.
- **`huggingface.py`** — queries `https://huggingface.co/api/models?sort=trendingScore&limit=20` and `https://huggingface.co/api/daily_papers?date=<today>`. Emits each as a separate item with `signals.type: "model" | "paper"`.
- **`release_blogs.py`** — parses RSS feeds via `feedparser`:
  - Anthropic: `https://www.anthropic.com/news/rss.xml` (verify during implementation)
  - OpenAI: `https://openai.com/blog/rss.xml` (verify)
  - Google DeepMind: `https://deepmind.google/blog/rss.xml` (verify)
  - Meta AI: best-effort, may fall back to a blog index
  Filters entries from the last 48 hours. If a feed URL is wrong at implementation time, substitute with the correct one and document it in README.

All fetchers:
- Exit 0 on success, non-zero with an error message on stderr otherwise
- Never raise uncaught exceptions; always emit valid JSON envelope (even an empty `items` array on total failure)
- Accept no arguments

### 3.3 State

**`state/seen.json` schema:**

```json
{
  "https://github.com/langchain-ai/langgraph": {
    "first_seen": "2026-04-13",
    "last_seen": "2026-04-15",
    "days": 3,
    "title": "langchain-ai/langgraph"
  }
}
```

**`scripts/update_seen.py`:**
- Input: path to today's `brief.md` (or the filtered items Claude saved to a sidecar JSON)
- Action: for each URL, upsert entry (increment `days` if `last_seen` was yesterday, reset if gap), prune entries whose `last_seen` is > 7 days ago
- Emits summary to stdout (`added: N, bumped: N, pruned: N`)

To avoid parsing the markdown, `/brief` also writes `daily/<date>/selected.json` — the list of items that made it into the brief with their URLs. `update_seen.py` consumes that.

### 3.4 `/brief` slash command (`.claude/commands/brief.md`)

Defines the orchestration workflow. Skeleton:

```markdown
---
description: Generate today's AI trend brief
---

You are running `/brief` for daily-ai-brief. Follow this procedure exactly.

## Step 1 — Prep
- Let TODAY = today's date in YYYY-MM-DD (Asia/Seoul)
- If daily/$TODAY/brief.md already exists, ask the user whether to overwrite
- Create daily/$TODAY/raw/ if missing

## Step 2 — Run fetchers
Run these four commands in parallel, redirecting stdout to the raw/ folder:
- python -m fetchers.github_trending > daily/$TODAY/raw/github_trending.json
- python -m fetchers.hacker_news > daily/$TODAY/raw/hacker_news.json
- python -m fetchers.huggingface > daily/$TODAY/raw/huggingface.json
- python -m fetchers.release_blogs > daily/$TODAY/raw/release_blogs.json

If a fetcher exits non-zero, note the source as "unavailable" but continue.

## Step 3 — Read context
- Read interests.md
- Read state/seen.json (empty {} if missing)
- Read all four raw JSON files

## Step 4 — Filter
For each item across all sources, decide whether it matches any category in interests.md.
Use keyword matching as a first pass, but apply semantic judgment:
a hit on "agent" alone is not enough; "agent framework" or "multi-agent system" is.
Respect Global exclude terms.

## Step 5 — Annotate dedup state
For each kept item, check seen.json:
- Not present → mark "new"
- Present with last_seen ≥ today-1 → mark "day N" where N = days + 1
- Present but older → treat as new (resurfaced)

## Step 6 — Select TOP 5
Criteria (in order):
1. Multi-source signal (appeared in 2+ sources today)
2. Category diversity (avoid 5 items from the same category)
3. Interest relevance weight
4. Freshness (new > day 2 > day 3+)
Items already at "day 3+" cannot be in TOP 5 unless genuinely breaking.

## Step 7 — Compose brief.md
Use this template:

    # YYYY-MM-DD AI 트렌드 브리프

    ## 🔥 오늘의 TOP 5
    1. **<title>** — <한 줄 해설: 왜 중요한가>
       sources: <comma-separated>
       <url>

    ## 📋 카테고리별 나머지

    ### 에이전트 프레임워크
    - **<title>** [<source>] — <1줄 요약> (<new | day N>)
      <url>

    ### (… other categories only if they have items …)

    ## 📌 Still trending (day 2+)
    - ...

    ## ⚠️ 소스 상태
    - github_trending: ok (25 items)
    - ...

All summaries in Korean. URLs on their own line.

## Step 8 — Save selected items
Write daily/$TODAY/selected.json with the list of items included in the brief.

## Step 9 — Update state
Run: python scripts/update_seen.py daily/$TODAY/selected.json

## Step 10 — Commit
git add daily/$TODAY state/seen.json
git commit -m "brief: $TODAY"

Report to the user: "Brief written to daily/$TODAY/brief.md (TOP 5 + N more items)."
```

### 3.5 Tests

Fixture-based pytest. No network. For each fetcher:
- A fixture file captured once from the real source and committed
- A test that calls the fetcher's internal `parse(fixture_content)` function and asserts:
  - Returns an envelope conforming to the shared schema
  - `items` is non-empty
  - Each item has required fields
  - Source-specific assertions (e.g., GitHub items have `signals.stars`)

Plus tests for `scripts/update_seen.py`: new item, bumped day, gap reset, prune >7 days, corrupt input fallback.

Not tested: the slash command itself (it's a prompt). Its correctness depends on fetcher correctness + Claude's judgment, which is not automatable in MVP.

## 4. Data flow (one `/brief` run)

```
User types /brief
   │
   ▼
Claude reads .claude/commands/brief.md
   │
   ▼
Claude runs 4 fetchers in parallel (Bash tool)
   │
   ▼
Raw JSONs land in daily/<today>/raw/
   │
   ▼
Claude reads raw JSONs + interests.md + state/seen.json
   │
   ▼
Claude filters by interest match
   │
   ▼
Claude annotates dedup state
   │
   ▼
Claude selects TOP 5 with reasoning
   │
   ▼
Claude writes brief.md and selected.json
   │
   ▼
Claude runs update_seen.py
   │
   ▼
Claude runs git add && git commit
   │
   ▼
Claude reports to user
```

## 5. Error handling

| Failure | Handling |
|---|---|
| Single fetcher network error | Fetcher emits empty items envelope + stderr message. `/brief` continues with other sources, notes "unavailable" in the brief's source-status section. |
| Single fetcher parse error (e.g., site HTML changed) | Fetcher logs exception to stderr, emits empty items envelope, exits non-zero. Test suite catches this kind of breakage the next time tests run. |
| All 4 fetchers fail | `/brief` aborts before writing brief.md, tells the user to check network/fetcher and retry. No git commit. |
| No items match interests | `brief.md` is still written with a note ("오늘은 관심사에 해당하는 강한 시그널이 적습니다") plus the raw top 3 of each source as a courtesy fallback. |
| `state/seen.json` missing | Treated as `{}`. |
| `state/seen.json` corrupt JSON | `update_seen.py` backs up the corrupt file to `state/seen.json.corrupt-<timestamp>` and starts fresh. `/brief` warns the user. |
| `daily/<today>/` already exists when `/brief` runs | Claude asks the user whether to overwrite before proceeding. |
| Fetcher exceeds reasonable runtime | Each fetcher should complete in under 30 seconds; Claude sets a 60-second Bash timeout per fetcher. |
| `interests.md` missing | `/brief` aborts with a clear message: "interests.md not found — see README for format." |

## 6. Testing strategy

**Fetcher tests** (`tests/test_fetchers.py`):
- Refactor each fetcher so its HTTP/network call is one function (`fetch_raw() -> bytes`) and its parsing is another (`parse(raw: bytes) -> dict`). Tests call only `parse()` with a fixture.
- Fixtures live in `tests/fixtures/` and are real captured responses, committed.
- Each fetcher has at least: happy path, empty response, malformed-but-parseable response.

**State tests** (`tests/test_update_seen.py`):
- New item → added with `days=1`
- Item seen yesterday → `days` incremented, `last_seen` updated
- Item seen 3 days ago (gap) → reset to `days=1`, `first_seen` updated
- Item not seen for >7 days → pruned on any run
- Corrupt `seen.json` → backed up, empty state used

**Run with:** `pytest -v`

**Not tested in MVP:** The slash command prompt itself. Verified manually by running `/brief` once and inspecting `daily/<today>/brief.md`.

## 7. Implementation order (for the plan)

1. Project scaffolding: `requirements.txt`, `pytest.ini`, `.gitignore`, `README.md`
2. `interests.md` with the user's five categories
3. Shared envelope schema documented in `fetchers/__init__.py`
4. Each fetcher: write fixture → write parse test → write parse function → write fetch_raw → make test pass
5. `scripts/update_seen.py` with its tests
6. `.claude/commands/brief.md` slash command
7. End-to-end dry run: execute each fetcher manually, verify JSON shape, then simulate the brief step with one sample
8. Initial git commit of the scaffolding, then a second commit per component

## 8. Non-goals / explicit rejections

- No cron. The act of running `/brief` daily is what the user is tracking with git log.
- No Twitter/X, Reddit, arXiv. The user's rationale: signals hitting these will also surface via HN or HF Papers, so adding them is noise for marginal coverage.
- No multi-agent orchestration in MVP. Single-pass `/brief` is enough to prove the pattern; L4 is reserved for a second iteration when the base is stable.
- No webpage. Markdown + git log are the UI.
