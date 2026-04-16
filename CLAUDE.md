# Project: daily-ai-brief-for-claude

This is a personal daily AI trend briefing system. The `/brief` command
generates `daily/<date>/brief.md`. Users can then ask to save any item
from any past brief for later review.

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

**4. 스크립트 호출**

```bash
python -m scripts.save_item \
  --url "<url>" \
  --title "<title>" \
  --summary "<summary>" \
  --source <source> \
  --category <slug> \
  --brief-date <yyyy-mm-dd>
```

`.venv/bin/python`이 있으면 그걸 우선 사용, 없으면 시스템 `python`.

**5. 결과 보고**

스크립트 stdout을 사용자에게 그대로 보여줌. stderr에 WARNING이 있으면 함께 표시.

스크립트 실행이 성공하면 반드시 파일을 git에 커밋:
```bash
git add state/saved.json saved/<category>.md
git commit -m "save: <title>"
```

## 저장 항목 조회

사용자가 "저장한 것 보여줘", "뭐 저장했지", "saved" 등 조회 의사를 보이면
`/saved` 커맨드를 실행하도록 안내하거나 직접 `.claude/commands/saved.md` 절차를 따름.
