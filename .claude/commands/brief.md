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
.venv/bin/python -m fetchers.github_trending > daily/$TODAY/raw/github_trending.json
.venv/bin/python -m fetchers.hacker_news > daily/$TODAY/raw/hacker_news.json
.venv/bin/python -m fetchers.huggingface > daily/$TODAY/raw/huggingface.json
.venv/bin/python -m fetchers.release_blogs > daily/$TODAY/raw/release_blogs.json
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
Run: `.venv/bin/python scripts/update_seen.py state/seen.json daily/$TODAY/selected.json`

## Step 10 — Commit
```
git add -f daily/$TODAY
git add state/seen.json
git commit -m "brief: $TODAY"
```

## Step 11 — Report
Tell the user: "Brief written to daily/$TODAY/brief.md — TOP 5 + N carousel items. Source status: ..."
