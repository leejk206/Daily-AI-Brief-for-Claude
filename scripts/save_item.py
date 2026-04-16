"""Save a brief.md item to saved/<category>.md with URL-keyed dedup.

Usage: python -m scripts.save_item \\
    --url URL --title TITLE --summary SUMMARY \\
    --source {github_trending,hacker_news,huggingface,release_blogs} \\
    --category SLUG --brief-date YYYY-MM-DD \\
    [--state-path state/saved.json] [--saved-dir saved]
"""

from __future__ import annotations

import argparse
import sys

VALID_SOURCES = {"github_trending", "hacker_news", "huggingface", "release_blogs"}
VALID_CATEGORIES = {
    "agent-frameworks",
    "llm-harness-eval",
    "mcp",
    "coding-agents",
    "prompt-context-engineering",
    "uncategorized",
}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="save_item", add_help=True)
    p.add_argument("--url", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--source", required=True, choices=sorted(VALID_SOURCES))
    p.add_argument("--category", required=True, choices=sorted(VALID_CATEGORIES))
    p.add_argument("--brief-date", required=True)
    p.add_argument("--state-path", default="state/saved.json")
    p.add_argument("--saved-dir", default="saved")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if e.code is not None else 2
    # Stub — real logic in later tasks
    del args
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
