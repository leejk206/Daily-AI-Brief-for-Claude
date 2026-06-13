---
description: Generate today's AI trend brief for daily-ai-brief
---

You are running the `/brief` command for `daily-ai-brief`. Follow this procedure exactly.

## Step 1 — Prep
- Compute `TODAY` = today's date in `YYYY-MM-DD` format (Asia/Seoul).
- If `daily/$TODAY/brief.md` already exists, ask the user whether to overwrite. If they decline, abort.
- Create `daily/$TODAY/raw/` if it doesn't exist.

## Step 2 — Run fetchers in parallel
Issue these six Bash commands in parallel (single message, multiple tool calls):

```
.venv/bin/python -m fetchers.github_trending > daily/$TODAY/raw/github_trending.json
.venv/bin/python -m fetchers.hacker_news > daily/$TODAY/raw/hacker_news.json
.venv/bin/python -m fetchers.huggingface > daily/$TODAY/raw/huggingface.json
.venv/bin/python -m fetchers.release_blogs > daily/$TODAY/raw/release_blogs.json
.venv/bin/python -m fetchers.anthropic_news > daily/$TODAY/raw/anthropic_news.json
.venv/bin/python -m fetchers.dcinside > daily/$TODAY/raw/dcinside.json
```

`release_blogs`는 OpenAI(ChatGPT)·DeepMind·Gemini 공식 블로그 RSS를 합쳐서 낸다.
`anthropic_news`는 Anthropic 공식 뉴스(RSS 부재 → HTML 스크래핑), `dcinside`는 특이점
마이너 갤러리 개념글(커뮤니티 — 노이즈 많음)이다.

Each fetcher has a 60-second timeout. If a fetcher exits non-zero, note the source as `unavailable` but continue. If all six fail, abort with a message to the user.

## Step 3 — Read context
Read these files:
- `interests.md`
- `state/seen.json` (treat missing file or empty object as `{}`)
- `state/archive.json` (treat missing file or empty object as `{}`) — permanent TOP 5 archive
- All six raw JSON files from `daily/$TODAY/raw/`

## Step 4 — Filter by interests
For each item across all six envelopes:
- **Hard exclude:** If the item's URL is present in `archive.json`, drop it immediately. These were past TOP 5s and must NEVER reappear in any future brief, even as a carousel item.
- Check if it matches any of the categories in `interests.md`.
- Use keyword matching as a first pass, then apply semantic judgment. A hit on the single word "agent" is NOT enough — require a phrase like "agent framework", "multi-agent", or an explicit category keyword.
- Respect each category's `Exclude` list and the `Global exclude` list.
- Record the matched category for each kept item.
- **`frontier-models`는 "반드시 잡는" 헤드라인 레인이다.** 플래그십 모델 출시 발표나 중대한 모델 접속·정책 사건이 ① 공식 벤더(anthropic_news / release_blogs)에서 발표됐거나 ② 2개 이상 출처에 떴으면, 다른 카테고리에 안 걸려도 **반드시 surface**하고 Step 6에서 TOP 5 상위로 올린다. 단 같은 사건이 여러 URL로 중복되면(공식 발표 + status + 트윗 등) 가장 표준적인 공식 URL 1개로 합친다. 원raw 체크포인트·양자화·파인튜닝 리포(예: `*/gemma-4-12B-it`, `*-GGUF`)는 출시 발표 본문이 아니므로 제외한다.

### Step 4b — DCInside 커뮤니티 항목 큐레이션
`dcinside` 소스 항목은 위 카테고리 필터를 강제하지 않고 **별도로 큐레이션**한다:
- 공식/카테고리 항목과 섞지 말 것. brief.md의 별도 "커뮤니티 동향" 섹션(Step 7)에만 넣는다.
- AI·특이점·모델 동향과 **실질적으로 관련 있고 읽을 가치가 있는 글만** 추린다(밈·잡담·단순 질문·정치 글 제외). 보통 **0~5개**면 충분하며, 없으면 섹션째 생략한다.
- `recommend`/`replies`/`views` signals를 참고해 호응이 큰 글을 우선한다.
- TOP 5에는 절대 넣지 않는다(커뮤니티 글은 공식 출처가 아님). seen/archive 상태 추적·태깅 대상도 아니다.

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

### 프런티어 모델·주요 발표
- **<title>** [<source>] — <1줄 한국어 요약> (<new | day N>)
  <url>

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

## 💬 커뮤니티 동향 (DCInside 특이점갤)
- **<title>** — <1줄 한국어 요약: 무슨 얘기인지/왜 볼 만한지>
  <url>

## ⚠️ 소스 상태
- github_trending: ok (N items / M matched)
- hacker_news: ok (N items / M matched)
- huggingface: ok (N items / M matched)
- release_blogs: ok (N items / M matched)
- anthropic_news: ok (N items / M matched)
- dcinside: ok (N items / K curated)
```

Rules:
- All summaries and commentary in Korean.
- URLs on their own line.
- Skip any empty category section.
- "커뮤니티 동향" 섹션은 Step 4b에서 추린 DCInside 항목만 넣고, 추린 게 없으면 섹션째 생략한다.
- If no items match interests at all, write a fallback section listing the raw top 3 of each source.

## Step 7.5 — 항목 태깅

`AGENTS.md`와 `tags.md`의 정책에 따라 brief.md의 모든 항목(TOP 5 + 카테고리별 + Still trending)에 태그를 부여한다.

1. 다음 파일을 읽는다:
   - `AGENTS.md` (태깅 정책)
   - `tags.md` (현재 어휘)
   - `state/tags.json` (없으면 빈 인덱스 — `scripts.tags_state.load()` 사용)

2. brief.md의 각 항목에 대해:
   - `state/tags.json`에 URL이 이미 있으면 → 태그 합집합 갱신 (`scripts.tags_state.upsert_item()`이 알아서 처리). Still trending 항목은 거의 항상 이 분기 — title/summary/category/source 등 메타는 첫 등장 시점 값으로 박제되어 있으니 다시 조회 불필요.
   - 없으면 → AGENTS.md 정책 따라 1~5개 태그 선정
   - 신규 태그(현 tags.md에 없는 것)면:
     - `state/tags.json`의 모든 기존 항목 tags에서 사용 횟수 카운트
     - 이번 사용 포함 누적 2회 이상 → `tags.md`의 Canonical 섹션에 추가
     - 1회 → `tags.md`의 Candidate 섹션에 추가

3. 모든 항목에 대해 `tags_state.upsert_item()` 호출 후 `tags_state.save()` 한 번.

4. 1회 brief에서 신규 태그가 5개 이상이면 Step 11 보고에 WARNING 추가.

운영 코드 예시 (인라인 Python으로 실행):

```python
from pathlib import Path
from scripts import tags_state

state, backup = tags_state.load(Path("state/tags.json"))
if backup:
    print(f"WARNING: corrupt tags.json backed up to {backup}")

# (Claude가 brief 항목별로 tags 결정한 뒤)
for item in tagged_items:
    tags_state.upsert_item(
        state, item["url"],
        title=item["title"], summary=item["summary"],
        category=item["category"], source=item["source"],
        brief_date=TODAY,
        tags=item["tags"],
    )

tags_state.save(Path("state/tags.json"), state)
```

## Step 8 — Save selected items
Write two files:
- `daily/$TODAY/selected.json` — JSON array of all items in the brief (TOP 5 + carousels), each as `{"url": "...", "title": "..."}`.
- `daily/$TODAY/top5.json` — JSON array of just the TOP 5 items (same shape, ordered 1→5).

## Step 9 — Update state
Run both in order:
```
.venv/bin/python scripts/update_seen.py state/seen.json daily/$TODAY/selected.json
.venv/bin/python scripts/archive_top5.py state/archive.json daily/$TODAY/top5.json
```

## Step 10 — Commit
```
git add -f daily/$TODAY
git add state/seen.json state/archive.json state/tags.json tags.md
git commit -m "brief: $TODAY"
```

## Step 11 — Report
Tell the user: "Brief written to daily/$TODAY/brief.md — TOP 5 + N carousel items. Source status: ... Tags: M items tagged, K new (J promoted to canonical)."

신규 태그가 ≥ 5개면 WARNING으로 사용자에게 검토 요청.
