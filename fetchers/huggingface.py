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
