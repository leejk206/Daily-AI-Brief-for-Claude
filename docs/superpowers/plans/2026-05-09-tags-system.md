# Tags System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tag-based search/filter system to daily-ai-brief — Claude tags every brief item during `/brief`, carries tags into saved items, and lets users query past briefs/saved items via natural language.

**Architecture:** Three-file system: `AGENTS.md` (tagging policy doc, read by Claude), `tags.md` (canonical + candidate tag registry), `state/tags.json` (URL→tag-data central index, source of truth). The Python data layer (`scripts/tags_state.py`, modified `save_item.py`) is fully testable; LLM tagging behavior happens in Claude's `/brief` and `/save` flows and is verified manually.

**Tech Stack:** Python 3.11+ (stdlib only — `pathlib`, `json`, `argparse`, `zoneinfo`, `shutil`, `datetime`), pytest 8.3.3.

**Spec reference:** `docs/superpowers/specs/2026-05-09-tags-system-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `scripts/tags_state.py` | Create | Pure data-layer helpers for `state/tags.json` (load with corruption backup, save, upsert with tag-union, get) |
| `tests/test_tags_state.py` | Create | Unit tests for the data layer |
| `state/tags.json` | Create | Empty seed `{"version": 1, "items": {}}` |
| `AGENTS.md` | Create | Tagging policy: when, how, naming, promotion, anti-patterns |
| `tags.md` | Create | Canonical (~12 seed tags) + empty Candidate section |
| `scripts/save_item.py` | Modify | Add `--tags` arg, write `tags` field to entry, append `**태그**:` line in md when tags present |
| `tests/test_save_item.py` | Modify | Extend with `--tags` cases (with/without/empty) |
| `.claude/commands/brief.md` | Modify | Insert "Step 7.5 — 항목 태깅"; update Step 10 git add |
| `CLAUDE.md` | Modify | Reference AGENTS.md; add tagging step in `/save` flow; add backfill + NL-search procedures |
| `daily/<date>/brief.md` × past briefs + `state/saved.json` | Backfill (runtime) | One-time tagging of all past brief items + the legacy saved item, executed by Claude |

**Decomposition rationale:** Data layer (`tags_state.py`) is small and focused — single responsibility (read/write the index). `save_item.py` mod is local (add one optional arg + one output line). Doc files (`AGENTS.md`, `tags.md`, command files) are static and don't get tests. The actual LLM tagging logic lives in Claude's prompts (`brief.md`, `CLAUDE.md`), not in Python.

---

## Task 1: Data Layer — `scripts/tags_state.py`

**Files:**
- Create: `scripts/tags_state.py`
- Test: `tests/test_tags_state.py`

- [ ] **Step 1.1: Write failing test for empty load**

Create `tests/test_tags_state.py`:

```python
import json
from pathlib import Path

from scripts import tags_state


def test_load_missing_file_returns_empty_state(tmp_path):
    state, backup = tags_state.load(tmp_path / "tags.json")
    assert state == {"version": 1, "items": {}}
    assert backup is None
```

- [ ] **Step 1.2: Run to verify it fails**

```bash
.venv/bin/pytest tests/test_tags_state.py::test_load_missing_file_returns_empty_state -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.tags_state'`

- [ ] **Step 1.3: Create minimal `scripts/tags_state.py`**

```python
"""state/tags.json read/write helpers — single-responsibility data layer."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def _empty_state() -> dict[str, Any]:
    return {"version": 1, "items": {}}


def load(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return _empty_state(), None
    try:
        data = json.loads(path.read_text())
        if (
            not isinstance(data, dict)
            or "items" not in data
            or not isinstance(data["items"], dict)
        ):
            raise ValueError("malformed")
        return data, None
    except (json.JSONDecodeError, ValueError):
        ts = dt.datetime.now(KST).strftime("%Y%m%d%H%M%S")
        backup = path.with_suffix(path.suffix + f".corrupt-{ts}")
        shutil.copy(path, backup)
        return _empty_state(), str(backup)
```

- [ ] **Step 1.4: Run to verify pass**

```bash
.venv/bin/pytest tests/test_tags_state.py::test_load_missing_file_returns_empty_state -v
```

Expected: PASS

- [ ] **Step 1.5: Add tests for valid load + corruption backup**

Append to `tests/test_tags_state.py`:

```python
def test_load_valid_json(tmp_path):
    p = tmp_path / "tags.json"
    p.write_text(json.dumps({
        "version": 1,
        "items": {
            "https://x.example": {
                "title": "T", "summary": "S",
                "category": "mcp", "source": "hacker_news",
                "brief_date": "2026-05-01",
                "tags": ["mcp-server"],
                "tagged_at": "2026-05-01T09:00:00+09:00",
            }
        }
    }))
    state, backup = tags_state.load(p)
    assert backup is None
    assert state["items"]["https://x.example"]["tags"] == ["mcp-server"]


def test_load_corrupt_backs_up_and_returns_empty(tmp_path):
    p = tmp_path / "tags.json"
    p.write_text("{not valid json")
    state, backup = tags_state.load(p)
    assert state == {"version": 1, "items": {}}
    assert backup is not None
    assert ".corrupt-" in backup
    assert Path(backup).exists()


def test_load_malformed_shape_backs_up(tmp_path):
    p = tmp_path / "tags.json"
    p.write_text(json.dumps([1, 2, 3]))  # not a dict
    state, backup = tags_state.load(p)
    assert state == {"version": 1, "items": {}}
    assert backup is not None
```

- [ ] **Step 1.6: Run new tests, confirm pass**

```bash
.venv/bin/pytest tests/test_tags_state.py -v
```

Expected: 3 PASS

- [ ] **Step 1.7: Add failing tests for save + upsert + get**

Append:

```python
def test_save_creates_parent_dirs(tmp_path):
    p = tmp_path / "deep" / "nested" / "tags.json"
    tags_state.save(p, {"version": 1, "items": {}})
    assert p.exists()
    assert json.loads(p.read_text()) == {"version": 1, "items": {}}


def test_upsert_new_item():
    state = {"version": 1, "items": {}}
    tags_state.upsert_item(
        state, "https://a.example",
        title="A", summary="sum",
        category="mcp", source="hacker_news",
        brief_date="2026-05-09",
        tags=["mcp-server", "tool-use"],
    )
    item = state["items"]["https://a.example"]
    assert item["title"] == "A"
    assert item["category"] == "mcp"
    assert item["brief_date"] == "2026-05-09"
    assert sorted(item["tags"]) == ["mcp-server", "tool-use"]
    assert "tagged_at" in item


def test_upsert_existing_merges_tags_and_preserves_brief_date():
    state = {
        "version": 1,
        "items": {
            "https://a.example": {
                "title": "A", "summary": "s",
                "category": "mcp", "source": "hacker_news",
                "brief_date": "2026-04-15",
                "tags": ["mcp-server"],
                "tagged_at": "2026-04-15T09:00:00+09:00",
            }
        },
    }
    tags_state.upsert_item(
        state, "https://a.example",
        title="A2", summary="s2",  # ignored on update
        category="other", source="other",  # ignored on update
        brief_date="2026-05-09",  # ignored — first-touch wins
        tags=["tool-use"],
    )
    item = state["items"]["https://a.example"]
    assert sorted(item["tags"]) == ["mcp-server", "tool-use"]
    assert item["brief_date"] == "2026-04-15"  # preserved
    assert item["title"] == "A"  # preserved
    assert item["category"] == "mcp"  # preserved
    assert item["tagged_at"] != "2026-04-15T09:00:00+09:00"  # refreshed


def test_get_item():
    state = {"version": 1, "items": {"u": {"tags": ["x"]}}}
    assert tags_state.get_item(state, "u") == {"tags": ["x"]}
    assert tags_state.get_item(state, "missing") is None
```

- [ ] **Step 1.8: Run them, expect failures for the missing functions**

```bash
.venv/bin/pytest tests/test_tags_state.py -v
```

Expected: `test_save_creates_parent_dirs`, `test_upsert_*`, `test_get_item` FAIL with `AttributeError`

- [ ] **Step 1.9: Implement save / upsert_item / get_item**

Append to `scripts/tags_state.py`:

```python
def save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def upsert_item(
    state: dict[str, Any],
    url: str,
    *,
    title: str,
    summary: str,
    category: str,
    source: str,
    brief_date: str,
    tags: list[str],
) -> None:
    """Insert new item or merge tags into existing.

    On update: tags = union(existing, new); brief_date / title / summary /
    category / source preserved (first-touch wins); tagged_at refreshed.
    """
    now = dt.datetime.now(KST).isoformat(timespec="seconds")
    existing = state["items"].get(url)
    if existing is None:
        state["items"][url] = {
            "title": title,
            "summary": summary,
            "category": category,
            "source": source,
            "brief_date": brief_date,
            "tags": sorted(set(tags)),
            "tagged_at": now,
        }
    else:
        merged = sorted(set(existing.get("tags", [])) | set(tags))
        existing["tags"] = merged
        existing["tagged_at"] = now


def get_item(state: dict[str, Any], url: str) -> dict[str, Any] | None:
    return state["items"].get(url)
```

- [ ] **Step 1.10: Run all tests, expect all pass**

```bash
.venv/bin/pytest tests/test_tags_state.py -v
```

Expected: 7 PASS

- [ ] **Step 1.11: Commit**

```bash
git add scripts/tags_state.py tests/test_tags_state.py
git commit -m "feat(tags): add tags_state data layer with corruption backup and tag-union upsert"
```

---

## Task 2: Seed `state/tags.json`

**Files:**
- Create: `state/tags.json`

- [ ] **Step 2.1: Create empty seed**

Write `state/tags.json`:

```json
{
  "version": 1,
  "items": {}
}
```

- [ ] **Step 2.2: Verify it loads cleanly**

```bash
.venv/bin/python -c "from pathlib import Path; from scripts import tags_state; s, b = tags_state.load(Path('state/tags.json')); print(s, b)"
```

Expected: `{'version': 1, 'items': {}} None`

- [ ] **Step 2.3: Commit**

```bash
git add state/tags.json
git commit -m "chore(tags): seed empty state/tags.json"
```

---

## Task 3: Tag Registry — `tags.md`

**Files:**
- Create: `tags.md`

- [ ] **Step 3.1: Create `tags.md` with seed canonical tags**

Write `tags.md`:

```markdown
# Tags Registry

이 파일은 daily-ai-brief의 canonical 태그 사전입니다.
신규 태그는 candidate 섹션에 들어가고, 누적 2회 사용되면 canonical로 승격됩니다.

운영 규칙은 `AGENTS.md` 참조.

## Canonical

### rl
강화학습·RLHF·GRPO 등 학습 알고리즘 측면

### multi-agent
복수 에이전트 오케스트레이션·협업·통신

### mcp-server
MCP 서버 구현·운영·툴 제공

### benchmark
평가 벤치마크·리더보드·평가 프레임워크

### paper
arXiv·HuggingFace papers 류 학술 publication

### cli-agent
터미널 기반 코딩·작업 에이전트

### local-inference
로컬 모델 추론 엔진·경량 inference 스택

### tool-use
LLM 도구 호출·function calling 측면

### prompt-engineering
프롬프트·시스템 프롬프트·context 설계

### coding-platform
코딩 에이전트 플랫폼·IDE 통합 제품

### claude-code
Claude Code 관련 항목

### web-agent
브라우저·웹 자동화 에이전트

## Candidate

(빈 섹션. /brief 시 신규 태그 자동 추가됨)
```

- [ ] **Step 3.2: Commit**

```bash
git add tags.md
git commit -m "docs(tags): add tags.md registry with 12 seed canonical tags"
```

---

## Task 4: Tagging Policy — `AGENTS.md`

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 4.1: Create `AGENTS.md`**

Write `AGENTS.md`:

```markdown
# AGENTS — Tagging Policy for Claude

이 파일은 Claude가 daily-ai-brief 항목에 태그를 부여할 때 따르는 정책입니다.
`/brief`, `/save`, 백필, 자연어 검색 시 매번 참조하세요.

## 1. 언제 태깅하나

| 트리거 | 동작 |
|--------|------|
| `/brief` Step 7.5 | brief.md의 모든 항목(TOP 5 + 카테고리별)에 자동 태깅 |
| `/save` (NL 트리거) | `state/tags.json`에서 URL 조회 → 있으면 그 태그 carry over, 없으면 즉석 태깅(fallback) |
| 백필 (사용자 트리거) | 지정된 과거 brief.md 파일들의 모든 항목 + state/saved.json 항목 처리 |

## 2. 태그 선정 규칙

- 항목당 **1~5개**.
- `tags.md`의 **Canonical**에서 우선 선택.
- 적당한 게 없으면 **Candidate**에서 선택.
- 둘 다 없으면 **새 태그 제안** → `tags.md`의 Candidate 섹션에 추가.

## 3. 승격 규칙 (Candidate → Canonical)

새 태그를 항목에 부여한 직후:
1. `state/tags.json`의 모든 기존 항목의 `tags` 배열에서 이 태그 사용 횟수 카운트
2. **이번 사용 포함 누적 2회 이상**이면 `tags.md`의 Candidate 섹션에서 제거 + Canonical 섹션에 추가 (헤더 + 한 줄 설명)
3. 1회면 Candidate에 남겨둠

## 4. 이름 규약

- 소문자, 하이픈만. 스페이스·언더스코어·CamelCase 금지.
- **영문만**. 한글 태그 금지 (검색 일관성).
- 최대 20자.
- 예: `mcp-server` ✓ / `MCP_Server` ✗ / `MCP 서버` ✗

## 5. 금지 패턴

- **카테고리 슬러그 금지**: `agent-frameworks`, `llm-harness-eval`, `mcp`, `coding-agents`, `prompt-context-engineering` — 카테고리와 중복.
- **너무 일반적인 태그 금지**: `ai`, `llm`, `tech`, `news` — 모든 항목에 해당.
- **일회성 고유명사 금지**: 회사·제품명은 반복 사용 가능성 있을 때만 태그화 (예: `claude-code` ✓ / `simplex-startup-001` ✗).

## 6. 폭주 방지

`/brief` 1회에서 **신규 태그 ≥ 5개** 발생 시 사용자에게 WARNING 출력. 사용자 검토 후 진행.

## 7. 운영 절차 (Claude가 따라야 할 코드 호출)

태깅 결과를 `state/tags.json`에 반영할 때:

```python
from pathlib import Path
from scripts import tags_state

state, backup = tags_state.load(Path("state/tags.json"))
if backup:
    print(f"WARNING: corrupt tags.json backed up to {backup}")

tags_state.upsert_item(
    state, url,
    title=title, summary=summary,
    category=category, source=source,
    brief_date=brief_date,
    tags=tags,
)

tags_state.save(Path("state/tags.json"), state)
```

`tags.md` 갱신은 Edit 툴로 직접 수행 (Canonical/Candidate 섹션 헤더 아래 알파벳순 권장, 엄격하지 않음).
```

- [ ] **Step 4.2: Commit**

```bash
git add AGENTS.md
git commit -m "docs(tags): add AGENTS.md tagging policy for Claude"
```

---

## Task 5: `save_item.py` — Add `--tags` Support

**Files:**
- Modify: `scripts/save_item.py`
- Modify: `tests/test_save_item.py`

- [ ] **Step 5.1: Add failing test for `--tags` writes to JSON**

Append to `tests/test_save_item.py`:

```python
def test_save_with_tags_writes_to_json(tmp_path):
    args = _save_args(tmp_path) + ["--tags", "rl,multi-agent"]
    result = _run(*args)
    assert result.returncode == 0, result.stderr
    state_path = tmp_path / "state" / "saved.json"
    data = json.loads(state_path.read_text())
    assert data["items"][0]["tags"] == ["rl", "multi-agent"]


def test_save_without_tags_arg_writes_empty_list(tmp_path):
    result = _run(*_save_args(tmp_path))
    assert result.returncode == 0, result.stderr
    data = json.loads((tmp_path / "state" / "saved.json").read_text())
    assert data["items"][0]["tags"] == []


def test_save_with_tags_writes_md_tag_line(tmp_path):
    args = _save_args(tmp_path) + ["--tags", "rl,multi-agent"]
    _run(*args)
    md = (tmp_path / "saved" / "agent-frameworks.md").read_text()
    assert "**태그**: rl, multi-agent" in md


def test_save_without_tags_no_md_tag_line(tmp_path):
    _run(*_save_args(tmp_path))
    md = (tmp_path / "saved" / "agent-frameworks.md").read_text()
    assert "**태그**" not in md


def test_save_normalizes_tag_whitespace_and_empty(tmp_path):
    args = _save_args(tmp_path) + ["--tags", " rl , , multi-agent ,"]
    result = _run(*args)
    assert result.returncode == 0, result.stderr
    data = json.loads((tmp_path / "state" / "saved.json").read_text())
    assert data["items"][0]["tags"] == ["rl", "multi-agent"]
    md = (tmp_path / "saved" / "agent-frameworks.md").read_text()
    assert "**태그**: rl, multi-agent" in md
```

- [ ] **Step 5.2: Run new tests, confirm all fail**

```bash
.venv/bin/pytest tests/test_save_item.py::test_save_with_tags_writes_to_json tests/test_save_item.py::test_save_without_tags_arg_writes_empty_list tests/test_save_item.py::test_save_with_tags_writes_md_tag_line tests/test_save_item.py::test_save_without_tags_no_md_tag_line tests/test_save_item.py::test_save_normalizes_tag_whitespace_and_empty -v
```

Expected: 5 FAIL — `--tags` unrecognized arg / KeyError on `tags`

- [ ] **Step 5.3: Add `--tags` arg to parser**

In `scripts/save_item.py`, find `_build_parser` (around line 34) and add after the `--saved-dir` line:

```python
    p.add_argument(
        "--tags",
        default="",
        help="Comma-separated tag list (e.g. 'rl,multi-agent'). Empty whitespace and duplicate-empty tokens are dropped.",
    )
```

- [ ] **Step 5.4: Add tag-parsing helper and wire into entry**

In `scripts/save_item.py`, add this helper above `_format_entry`:

```python
def _parse_tags(raw: str) -> list[str]:
    return [t.strip() for t in raw.split(",") if t.strip()]
```

Then in `main()` (around line 159 where the `entry` dict is built), change:

```python
    entry = {
        "url": args.url,
        "title": args.title,
        "summary": args.summary,
        "source": args.source,
        "category": args.category,
        "brief_date": args.brief_date,
        "saved_at": now,
    }
```

to:

```python
    entry = {
        "url": args.url,
        "title": args.title,
        "summary": args.summary,
        "source": args.source,
        "category": args.category,
        "brief_date": args.brief_date,
        "saved_at": now,
        "tags": _parse_tags(args.tags),
    }
```

- [ ] **Step 5.5: Update `_format_entry` to render tag line conditionally**

In `scripts/save_item.py`, replace the existing `_format_entry`:

```python
def _format_entry(entry: dict[str, Any]) -> str:
    lines = [
        f"### {entry['title']}\n",
        f"- **요약**: {entry['summary']}\n",
    ]
    if entry.get("tags"):
        lines.append(f"- **태그**: {', '.join(entry['tags'])}\n")
    lines.extend([
        f"- **출처**: {entry['source']}\n",
        f"- **brief 날짜**: {entry['brief_date']}\n",
        f"- **URL**: {entry['url']}\n\n",
        f"---\n",
    ])
    return "".join(lines)
```

- [ ] **Step 5.6: Run new tests, confirm pass**

```bash
.venv/bin/pytest tests/test_save_item.py -v
```

Expected: All tests PASS (existing + new). Total ~12 PASS.

- [ ] **Step 5.7: Run full test suite — confirm no regressions**

```bash
.venv/bin/pytest -v
```

Expected: All previously-passing tests still PASS.

- [ ] **Step 5.8: Commit**

```bash
git add scripts/save_item.py tests/test_save_item.py
git commit -m "feat(save_item): add --tags arg and conditional tag line in saved md"
```

---

## Task 6: Update `/brief` Command — Insert Step 7.5

**Files:**
- Modify: `.claude/commands/brief.md`

- [ ] **Step 6.1: Insert Step 7.5 between Step 7 and Step 8**

In `.claude/commands/brief.md`, find the line `## Step 8 — Save selected items` and insert this block immediately before it:

```markdown
## Step 7.5 — 항목 태깅

`AGENTS.md`와 `tags.md`의 정책에 따라 brief.md의 모든 항목(TOP 5 + 카테고리별 + Still trending)에 태그를 부여한다.

1. 다음 파일을 읽는다:
   - `AGENTS.md` (태깅 정책)
   - `tags.md` (현재 어휘)
   - `state/tags.json` (없으면 빈 인덱스 — `scripts.tags_state.load()` 사용)

2. brief.md의 각 항목에 대해:
   - `state/tags.json`에 URL이 이미 있으면 → 태그 합집합 갱신 (`scripts.tags_state.upsert_item()`이 알아서 처리)
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
```

- [ ] **Step 6.2: Update Step 10 git add to include new files**

In `.claude/commands/brief.md`, find the Step 10 commit block:

```
git add -f daily/$TODAY
git add state/seen.json state/archive.json
git commit -m "brief: $TODAY"
```

Replace with:

```
git add -f daily/$TODAY
git add state/seen.json state/archive.json state/tags.json tags.md
git commit -m "brief: $TODAY"
```

- [ ] **Step 6.3: Update Step 11 reporting to mention tagging**

In `.claude/commands/brief.md`, find Step 11 and replace with:

```markdown
## Step 11 — Report
Tell the user: "Brief written to daily/$TODAY/brief.md — TOP 5 + N carousel items. Source status: ... Tags: M items tagged, K new (J promoted to canonical)."

신규 태그가 ≥ 5개면 WARNING으로 사용자에게 검토 요청.
```

- [ ] **Step 6.4: Verify brief.md still parseable as markdown** (visual check)

```bash
grep -E "^## Step" .claude/commands/brief.md
```

Expected: shows Steps 1, 2, 3, 4, 5, 6, 7, 7.5, 8, 9, 10, 11 in order.

- [ ] **Step 6.5: Commit**

```bash
git add .claude/commands/brief.md
git commit -m "feat(brief): add Step 7.5 tagging and update commit/report steps"
```

---

## Task 7: Update `CLAUDE.md` — Save Flow + Backfill + NL Search

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 7.1: Add AGENTS.md reference at the top**

In `CLAUDE.md`, find the line `This is a personal daily AI trend briefing system.` and insert immediately after it:

```markdown

태깅 정책은 `AGENTS.md`, 태그 어휘는 `tags.md`, 태그 데이터는
`state/tags.json`에 있습니다. 모든 태깅 작업 전에 `AGENTS.md`를 참조하세요.
```

- [ ] **Step 7.2: Insert tagging step into save flow**

In `CLAUDE.md`, find the section header `**4. 스크립트 호출**` and insert this block immediately before it:

```markdown
**3.5. 태그 결정**

- `state/tags.json`을 읽어 해당 URL이 있는지 확인 (`scripts.tags_state.load()` + `get_item()`).
- **있으면**: 그 항목의 `tags`를 그대로 사용.
- **없으면** (legacy/백필 안 된 항목): `AGENTS.md` 정책 따라 즉석 태깅. 결정된 tags를 `state/tags.json`에도 추가 (`upsert_item` + `save`).
- 결정된 tags를 다음 단계의 `--tags` 인자로 전달 (콤마 구분).

```

- [ ] **Step 7.3: Update the script-call command to include --tags**

In `CLAUDE.md`, find the script-call code block:

```bash
python -m scripts.save_item \
  --url "<url>" \
  --title "<title>" \
  --summary "<summary>" \
  --source <source> \
  --category <slug> \
  --brief-date <yyyy-mm-dd>
```

Replace with:

```bash
python -m scripts.save_item \
  --url "<url>" \
  --title "<title>" \
  --summary "<summary>" \
  --source <source> \
  --category <slug> \
  --brief-date <yyyy-mm-dd> \
  --tags "<tag1,tag2>"
```

- [ ] **Step 7.4: Update commit step to include tag-related files**

In `CLAUDE.md`, find:

```bash
git add state/saved.json saved/<category>.md
git commit -m "save: <title>"
```

Replace with:

```bash
git add state/saved.json saved/<category>.md state/tags.json tags.md
git commit -m "save: <title>"
```

(state/tags.json·tags.md는 fallback 태깅으로 갱신됐을 수 있음. 변경 없으면 `git add`는 noop이라 안전.)

- [ ] **Step 7.5: Add backfill section**

At the end of `CLAUDE.md`, append:

```markdown

## 태그 백필 (Tag Backfill)

사용자가 다음과 같이 트리거하면 과거 brief 항목들에 태그를 부여:
- "2026-04-15 brief 백필해줘"
- "지난 일주일 brief 다 백필"
- "전체 백필"

### 절차

1. **대상 식별**
   - 단일 날짜: `daily/<date>/brief.md` 1개
   - 기간: 해당 날짜 범위의 brief.md들
   - 전체: `daily/*/brief.md` 모두 + `state/saved.json`의 항목 중 `state/tags.json`에 URL이 없는 것

2. **항목 추출** — 각 brief.md에서:
   - TOP 5 섹션의 5개 항목 (`N. **title** — summary` + sources + url)
   - 카테고리별 섹션의 항목들 (`- **title** [source] — summary (new|day N)` + url)
   - Still trending은 카테고리 섹션과 중복 가능성 있으니 URL로 dedup

3. **태깅** — 각 항목에 대해 `AGENTS.md` 정책 따라 1~5개 태그 선정. tags.md에 신규 태그 추가/승격 규칙 동일.

4. **state/tags.json 갱신** — `scripts.tags_state.upsert_item` + `save`.

5. **결과 보고**
```
백필 완료:
- N개 brief, M개 항목 태깅
- 신규 candidate 태그: [...]
- canonical 승격: [...]
- 실패: <항목별 사유>
```

6. **커밋**
```bash
git add state/tags.json tags.md
git commit -m "tags: backfill <date or range>"
```

## 태그 기반 자연어 검색

사용자가 다음과 같이 질의하면 태그 데이터로 답:
- "MCP 관련 저장한 거 보여줘"
- "RL 태그 달린 항목 다 찾아줘"
- "최근 일주일 multi-agent 항목"

### 절차

1. **태그 정규화** — 질의에서 태그 후보 추출. tags.md의 canonical/candidate 참조해 정규화 (예: "강화학습" → `rl`, "멀티에이전트" → `multi-agent`).

2. **인덱스 검색** — `state/tags.json`을 읽고 매칭 항목 필터:
   - 단일 태그: `tags`에 해당 태그 포함된 항목
   - 다중 태그: 사용자가 "AND"로 의도했는지 "OR"인지 확인 (애매하면 1회 질의)
   - "저장한 것만"이라는 의도가 있으면 `state/saved.json`의 URL과 교집합

3. **결과 출력** (시간 역순):

```
# 🏷️ <태그명> 항목 (총 N개)

1. **<title>** (<brief_date>, <category>) [저장됨/새 발견]
   요약: <summary>
   <url>
```
```

- [ ] **Step 7.6: Verify CLAUDE.md is well-formed**

```bash
grep -c "^##" CLAUDE.md
```

Expected: count includes new sections (저장 의도 처리, 저장 항목 조회, 태그 백필, 태그 기반 자연어 검색 + subsections).

- [ ] **Step 7.7: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): add tagging step in save flow + backfill + NL search procedures"
```

---

## Task 8: Sanity-Test the End-to-End Save Path

This task is verification, not new code. Confirms Tasks 1, 5, 7 wire together correctly using the real CLI.

**Files:**
- (No file changes)

- [ ] **Step 8.1: Dry-run save with explicit tags against a tmp state**

```bash
.venv/bin/python -m scripts.save_item \
  --url "https://test.example/sanity" \
  --title "Sanity Test Item" \
  --summary "Verifying end-to-end save with tags" \
  --source hacker_news \
  --category mcp \
  --brief-date 2026-05-09 \
  --tags "mcp-server,test-only" \
  --state-path /tmp/sanity-saved.json \
  --saved-dir /tmp/sanity-saved
```

Expected stdout: `SAVED: Sanity Test Item -> /tmp/sanity-saved/mcp.md`

- [ ] **Step 8.2: Inspect outputs**

```bash
cat /tmp/sanity-saved.json
echo ---
cat /tmp/sanity-saved/mcp.md
```

Expected: JSON has `"tags": ["mcp-server", "test-only"]`. Markdown has the line `- **태그**: mcp-server, test-only`.

- [ ] **Step 8.3: Cleanup**

```bash
rm -rf /tmp/sanity-saved /tmp/sanity-saved.json
```

(No commit — verification only.)

---

## Task 9: Backfill Past Briefs and Legacy Saved Item

This is a **runtime task**, not code. Claude executes it interactively after Tasks 1–7 are merged. Included here so the migration is not forgotten.

**Files:**
- Modify (data only): `state/tags.json`, `tags.md`

- [ ] **Step 9.1: Confirm scope with the user**

Ask the user: "백필 대상은 `daily/` 하위 12개 brief 전체 + `state/saved.json`의 1개 legacy 항목으로 진행할까요?"

- [ ] **Step 9.2: Run backfill via the CLAUDE.md procedure**

Follow `CLAUDE.md` § "태그 백필" — section added in Task 7.5. Process all dates from `daily/2026-04-15/` through `daily/2026-05-08/` plus the saved item.

- [ ] **Step 9.3: Sanity-check the resulting `state/tags.json`**

```bash
.venv/bin/python -c "
import json
from pathlib import Path
data = json.loads(Path('state/tags.json').read_text())
print(f'Total items: {len(data[\"items\"])}')
print(f'Sample item: {next(iter(data[\"items\"].values()))}')
"
```

Expected: 100+ items (12 briefs × ~8–15 items each), each with non-empty tags.

- [ ] **Step 9.4: Sanity-check `tags.md`**

```bash
grep -c "^### " tags.md
```

Expected: at least 12 (initial seed) + several added candidates/promotions during backfill.

- [ ] **Step 9.5: Commit**

```bash
git add state/tags.json tags.md
git commit -m "tags: backfill 2026-04-15..2026-05-08 + legacy saved item"
```

---

## Self-Review

**Spec coverage:**
- ✅ AGENTS.md (Task 4) / tags.md (Task 3) / state/tags.json (Task 2) all covered
- ✅ Hybrid vocabulary (Task 4 §3) — promotion rule documented
- ✅ Central index storage (Task 1, Task 2)
- ✅ /brief Step 7.5 (Task 6)
- ✅ /save tag carry-over with fallback (Task 7.2 + Task 5)
- ✅ Backfill procedure (Task 7.5 added to CLAUDE.md, Task 9 executes)
- ✅ Natural-language search (Task 7.5)
- ✅ Error handling: corruption backup (Task 1.5), tag union on dup URL (Task 1.7), legacy save no `--tags` (Task 5.1)
- ✅ Tests: data layer (Task 1) + save_item with tags (Task 5) + manual verification (Task 8)
- ✅ Out-of-scope (vector embedding, auto recategorization, etc.) — not present in plan ✓

**Placeholder scan:** No "TBD/TODO/implement later" — every step has concrete code or exact command.

**Type consistency:**
- `tags_state.upsert_item` signature consistent across Task 1.7, 1.9, AGENTS.md (Task 4.1), brief.md Step 7.5 (Task 6.1), CLAUDE.md (Task 7.2). ✓
- `_parse_tags` defined and used (Task 5.4). ✓
- `state/tags.json` shape `{"version": 1, "items": {url: {...}}}` consistent across Task 1, 2, 4, 6, 7. ✓

No issues found.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-09-tags-system.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task (Tasks 1–8), review between tasks, fast iteration. Task 9 (backfill) runs interactively after the code is in.

2. **Inline Execution** — Execute Tasks 1–8 in this session using executing-plans, batch with checkpoints for review.

Which approach?
