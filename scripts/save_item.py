"""Save a brief.md item to saved/<category>.md with URL-keyed dedup.

Usage: python -m scripts.save_item \\
    --url URL --title TITLE --summary SUMMARY \\
    --source {github_trending,hacker_news,huggingface,release_blogs} \\
    --category SLUG --brief-date YYYY-MM-DD \\
    [--state-path state/saved.json] [--saved-dir saved]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

VALID_SOURCES = {"github_trending", "hacker_news", "huggingface", "release_blogs"}
VALID_CATEGORIES = {
    "agent-frameworks",
    "llm-harness-eval",
    "mcp",
    "coding-agents",
    "prompt-context-engineering",
    "uncategorized",
}

KST = ZoneInfo("Asia/Seoul")


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


def _empty_state() -> dict[str, Any]:
    return {"version": 1, "items": []}


def _load_state(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return _empty_state(), None
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or "items" not in data:
            raise ValueError("malformed")
        return data, None
    except (json.JSONDecodeError, ValueError):
        ts = dt.datetime.now(KST).strftime("%Y%m%d%H%M%S")
        backup = path.with_suffix(path.suffix + f".corrupt-{ts}")
        shutil.copy(path, backup)
        return _empty_state(), str(backup)


def _save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def _find_existing(state: dict[str, Any], url: str) -> dict[str, Any] | None:
    for item in state["items"]:
        if item.get("url") == url:
            return item
    return None


def _format_entry(entry: dict[str, Any]) -> str:
    return (
        f"### {entry['title']}\n"
        f"- **요약**: {entry['summary']}\n"
        f"- **출처**: {entry['source']}\n"
        f"- **brief 날짜**: {entry['brief_date']}\n"
        f"- **URL**: {entry['url']}\n\n"
        f"---\n"
    )


def _category_header(category: str) -> str:
    return f"# {category} — 저장된 항목\n"


def _today_date_str(now: dt.datetime) -> str:
    return now.date().isoformat()


def _prepend_to_category_md(
    md_path: Path, category: str, entry: dict[str, Any], today: str
) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    date_header = f"## {today} 저장\n"
    entry_block = _format_entry(entry)

    if not md_path.exists():
        md_path.write_text(
            f"{_category_header(category)}\n{date_header}\n{entry_block}"
        )
        return

    text = md_path.read_text()
    lines = text.splitlines(keepends=True)

    # Find header line index (first line starting with "# ")
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            header_end = i + 1
            while header_end < len(lines) and lines[header_end].strip() == "":
                header_end += 1
            break

    # Find first "## " (most recent date block)
    first_date_idx = None
    for i in range(header_end, len(lines)):
        if lines[i].startswith("## "):
            first_date_idx = i
            break

    if first_date_idx is not None and lines[first_date_idx].strip() == f"## {today} 저장":
        insert_at = first_date_idx + 1
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        block = entry_block if entry_block.endswith("\n") else entry_block + "\n"
        new_lines = lines[:insert_at] + [block] + lines[insert_at:]
    else:
        new_block = f"{date_header}\n{entry_block}"
        new_lines = lines[:header_end] + [new_block] + lines[header_end:]

    md_path.write_text("".join(new_lines))


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if e.code is not None else 2

    state_path = Path(args.state_path)
    state, corrupt_backup = _load_state(state_path)
    if corrupt_backup:
        print(f"WARNING: corrupt state backed up to {corrupt_backup}", file=sys.stderr)

    existing = _find_existing(state, args.url)
    if existing is not None:
        print(f"SKIP: already saved on {existing.get('saved_at', '<unknown>')}")
        return 0

    now = dt.datetime.now(KST).isoformat(timespec="seconds")
    entry = {
        "url": args.url,
        "title": args.title,
        "summary": args.summary,
        "source": args.source,
        "category": args.category,
        "brief_date": args.brief_date,
        "saved_at": now,
    }
    state["items"].insert(0, entry)
    _save_state(state_path, state)

    saved_dir = Path(args.saved_dir)
    md_path = saved_dir / f"{args.category}.md"
    today = _today_date_str(dt.datetime.now(KST))
    _prepend_to_category_md(md_path, args.category, entry, today)

    print(f"SAVED: {args.title} -> {args.saved_dir}/{args.category}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
