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

## Release blog feeds

At the time of writing, Anthropic does not publish an RSS feed for its news/engineering blog. `fetchers/release_blogs.py` currently pulls from:

- OpenAI — `https://openai.com/news/rss.xml`
- Google DeepMind — `https://deepmind.google/blog/rss.xml`

Add additional vendors by editing the `FEEDS` list in `fetchers/release_blogs.py`.
