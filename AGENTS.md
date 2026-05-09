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
4. 같은 태그가 Canonical과 Candidate 양쪽에 동시에 있는 게 발견되면 (예: 사람이 수동 편집으로 추가) Candidate에서 제거하고 Canonical 유지

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
