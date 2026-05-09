# Project: daily-ai-brief-for-claude

This is a personal daily AI trend briefing system. The `/brief` command
generates `daily/<date>/brief.md`. Users can then ask to save any item
from any past brief for later review.

태깅 정책은 `AGENTS.md`, 태그 어휘는 `tags.md`, 태그 데이터는
`state/tags.json`에 있습니다. 모든 태깅 작업 전에 `AGENTS.md`를 참조하세요.

## 저장 의도 처리 (Save Intent Handling)

사용자가 자연어로 다음과 같은 저장 의사를 표현하면 저장 절차를 실행합니다:
- "저장해", "저장해줘", "북마크", "북마크해"
- "나중에 볼래", "나중에 보게", "기억해둬", "담아둬"

### 절차

**1. 대상 식별**

- 직전 대화에서 언급·출력된 brief 항목을 우선 대상으로 함
- 여러 후보가 있거나 애매하면 "어느 항목인가요?" 라고 1회 확인
- 사용자가 제목/URL을 함께 말하면 그걸 우선
- 현재 세션에 없으면 `grep -rl "<URL 또는 제목 일부>" daily/*/brief.md`로 과거 brief 검색

**2. 항목 메타 추출** (brief.md 원문에서)

brief.md에는 두 가지 형식이 있음.

TOP 5 섹션 포맷:
```
N. **<title>** — <summary>
   sources: <source>
   <url>
```

카테고리 섹션 포맷:
```
- **<title>** [<source>] — <summary> (<new|day N>)
  <url>
```

뽑을 필드: title, summary, url, source, brief_date (brief.md의 상위 디렉토리 이름, 예: `daily/2026-04-16/brief.md` → `2026-04-16`).

**3. 카테고리 판정**

- 항목이 brief.md의 카테고리 섹션 아래에 있으면 그 섹션의 한국어 헤더를 슬러그로 변환:
  - 에이전트 프레임워크 → `agent-frameworks`
  - LLM 하네스·평가 → `llm-harness-eval`
  - MCP → `mcp`
  - 코딩 에이전트 → `coding-agents`
  - 프롬프트·컨텍스트 엔지니어링 → `prompt-context-engineering`
- TOP 5 섹션 항목이면 `interests.md`의 키워드로 매칭하여 가장 많은 키워드가 맞는 카테고리를 선택. 동점이면 위 나열 순서.
- 어느 것도 매칭 안 되면 `uncategorized`.

**3.5. 태그 결정**

- `state/tags.json`을 읽어 해당 URL이 있는지 확인 (`scripts.tags_state.load()` + `get_item()`).
- **있으면**: 그 항목의 `tags`를 그대로 사용.
- **없으면** (legacy/백필 안 된 항목): `AGENTS.md` 정책 따라 즉석 태깅. 결정된 tags를 `state/tags.json`에도 추가 (`upsert_item` + `save`).
- 결정된 tags를 다음 단계의 `--tags` 인자로 전달 (콤마 구분).

**4. 스크립트 호출**

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

`.venv/bin/python`이 있으면 그걸 우선 사용, 없으면 시스템 `python`.

**5. 결과 보고**

스크립트 stdout을 사용자에게 그대로 보여줌. stderr에 WARNING이 있으면 함께 표시.

스크립트 실행이 성공하면 반드시 파일을 git에 커밋:
```bash
git add state/saved.json saved/<category>.md state/tags.json tags.md
git commit -m "save: <title>"
```

(state/tags.json·tags.md는 fallback 태깅으로 갱신됐을 수 있음. 변경 없으면 `git add`는 noop이라 안전.)

## 저장 항목 조회

사용자가 "저장한 것 보여줘", "뭐 저장했지", "saved" 등 조회 의사를 보이면
`/saved` 커맨드를 실행하도록 안내하거나 직접 `.claude/commands/saved.md` 절차를 따름.

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
