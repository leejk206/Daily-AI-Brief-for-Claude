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

## 관심 항목 저장

`/brief` 결과 중 나중에 다시 보고 싶은 항목이 있으면 자연어로 말하세요:

- "그 Gemma 논문 저장해"
- "TOP 5 첫 번째 북마크"
- "나중에 볼 수 있게 담아둬"

Claude가 직전 brief에서 항목을 찾아 `saved/<category>.md`에 누적합니다.
과거 brief의 항목도 "어제 그 논문 저장해" 같은 식으로 요청 가능합니다.

저장된 항목 조회:

```
/saved                        # 최근 10개 전체
/saved agent-frameworks       # 해당 카테고리 파일 전체
/saved mcp 5                  # mcp 최근 5개
```

중복 URL은 조용히 스킵됩니다. 카테고리는 `interests.md`의 5개 + `uncategorized`.

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

## Release blog feeds

At the time of writing, Anthropic does not publish an RSS feed for its news/engineering blog. `fetchers/release_blogs.py` currently pulls from:

- OpenAI — `https://openai.com/news/rss.xml`
- Google DeepMind — `https://deepmind.google/blog/rss.xml`

Add additional vendors by editing the `FEEDS` list in `fetchers/release_blogs.py`.
