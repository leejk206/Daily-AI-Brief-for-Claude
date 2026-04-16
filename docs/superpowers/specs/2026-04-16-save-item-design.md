# Save Item — Design Spec

날짜: 2026-04-16
대상 프로젝트: `daily-ai-brief-for-claude`

## 목표

`/brief`로 생성된 `brief.md` 안 항목 중, 사용자가 자연어로 "저장해/북마크/나중에 볼래" 같은 의사를 표현하면 Claude가 해당 항목을 찾아 카테고리별 마크다운 파일에 누적 저장한다. 저장된 항목은 `/saved` 슬래시 커맨드로 조회한다.

## 범위

- **저장 대상**: `daily/*/brief.md` 전체 (오늘자 + 과거 모든 브리프)
- **저장 내용**: brief.md의 제목·한 줄 요약·URL·출처를 그대로 복사 (웹 재요약 없음)
- **트리거**: 자연어 의도 탐지 — 고정 키워드나 슬래시 커맨드 없음
- **분류**: `interests.md`의 5개 카테고리 또는 `uncategorized`
- **중복**: 같은 URL이면 조용히 스킵

## 아키텍처

세 계층, 기존 프로젝트 패턴과 동일.

```
사용자 발화 ("저장해")
   ↓
Claude (오케스트레이션 — CLAUDE.md 지시에 따라)
   ├─ 1. 의도 탐지
   ├─ 2. brief.md에서 대상 항목 식별
   ├─ 3. 카테고리 판정
   └─ 4. scripts/save_item.py 호출
             ↓
      scripts/save_item.py (결정적)
          ├─ state/saved.json 로드
          ├─ URL 중복 → SKIP exit 0
          └─ saved/<category>.md prepend + saved.json 업데이트
```

- **결정적 레이어**: `scripts/save_item.py`가 파일 I/O와 중복 체크를 담당
- **상태 레이어**: `state/saved.json` — URL 키 + 메타데이터 (기존 `seen.json`과 구조 유사)
- **오케스트레이션 레이어**: Claude가 의도·대상·카테고리 판정, 슬래시 커맨드로 조회

## 데이터 구조

### `state/saved.json`

```json
{
  "version": 1,
  "items": [
    {
      "url": "https://openai.com/index/the-next-evolution-of-the-agents-sdk",
      "title": "The next evolution of the Agents SDK",
      "summary": "OpenAI가 샌드박스·모델 네이티브 하네스 도입",
      "source": "release_blogs",
      "category": "agent-frameworks",
      "brief_date": "2026-04-16",
      "saved_at": "2026-04-16T14:23:11+09:00"
    }
  ]
}
```

- 키 필드: `url` (중복 판정 기준)
- `items`는 최신이 맨 앞 (prepend)
- `brief_date`: 항목이 등장한 brief.md 날짜 / `saved_at`: 저장 시각 (KST ISO8601)
- `source`: `release_blogs | github_trending | huggingface | hacker_news`
- `category`: `agent-frameworks | llm-harness-eval | mcp | coding-agents | prompt-context-engineering | uncategorized`

### `saved/<category>.md`

```markdown
# <category> — 저장된 항목

## 2026-04-16 저장

### The next evolution of the Agents SDK
- **요약**: OpenAI가 샌드박스·모델 네이티브 하네스 도입
- **출처**: release_blogs
- **brief 날짜**: 2026-04-16
- **URL**: https://openai.com/index/the-next-evolution-of-the-agents-sdk

---

## 2026-04-14 저장

### ...
```

- 파일 상단 헤더 (`# <category> — 저장된 항목`) 아래에 새 항목 prepend
- 항목 구분자: `---`
- 날짜 섹션 (`## YYYY-MM-DD 저장`)은 같은 날 여러 항목을 저장하면 같은 날짜 블록 아래에 쌓이고, 다른 날이면 새 날짜 섹션을 만듦

## 컴포넌트

### 1) `scripts/save_item.py` (신규)

**호출**:
```bash
.venv/bin/python -m scripts.save_item \
  --url "https://..." \
  --title "..." \
  --summary "..." \
  --source release_blogs \
  --category agent-frameworks \
  --brief-date 2026-04-16 \
  --state-path state/saved.json \
  --saved-dir saved
```

**동작**:
1. `state/saved.json` 로드 (없거나 손상이면 `{"version":1,"items":[]}`로 초기화, 손상 시 기존 파일은 `.corrupt-YYYYMMDDHHMMSS` 백업 — `update_seen.py` 패턴 그대로)
2. `items` 중 `url` 일치 항목 있으면:
   - `stdout`: `SKIP: already saved on <saved_at>`
   - `exit 0`
3. 신규면:
   - `saved_at` = `datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")`
   - `items` 맨 앞에 push (최신이 위)
   - `saved/<category>.md`가 없으면 헤더만 있는 새 파일 생성
   - 파일 내 가장 최신 `## YYYY-MM-DD 저장` 블록이 오늘 날짜면 그 블록 맨 앞에 항목 추가 (구분자 `---` 포함), 아니면 새 날짜 블록 생성
   - `state/saved.json` 저장
4. `stdout`: `SAVED: <title> → saved/<category>.md`
5. **종료 코드**: 성공(중복 포함) = 0, 인자/I/O 오류 = 비-0

**인자 검증**:
- `--category`는 `interests.md`에 있는 5개 슬러그 또는 `uncategorized`만 허용. 다른 값이면 비-0으로 실패.
- 필수 인자 누락 시 usage 출력 후 `exit 2`

**JST vs KST**: `Asia/Seoul` 타임존 사용. Python 3.9+ `zoneinfo` 모듈 활용.

### 2) `CLAUDE.md` (신규 — 프로젝트 루트)

Claude가 이 프로젝트의 모든 세션에서 자동으로 읽는 파일. 저장 의도 탐지·처리 절차를 기술.

내용 요약:

```markdown
# Project: daily-ai-brief-for-claude

## 저장 의도 처리

사용자가 자연어로 "저장해", "북마크", "나중에 볼래", "기억해둬",
"담아둬" 류의 발화를 하면 저장 절차를 실행한다.

### 절차

1. **대상 식별**:
   - 직전 대화에서 언급된 brief 항목 우선
   - 여러 후보가 있거나 애매하면 한 번만 "어느 항목인가요?" 라고 확인
   - 사용자가 제목/URL을 함께 말하면 그걸 우선
   - 현재 세션에 없으면 `grep -l "<URL 또는 제목 키워드>" daily/*/brief.md`로 과거 brief 검색

2. **항목 메타 추출** (brief.md 원문에서):
   - title, summary(한 줄 해설), URL, sources, brief_date(디렉토리명)
   - TOP 5 섹션 포맷: `N. **<title>** — <summary>\n   sources: <source>\n   <url>`
   - 카테고리 섹션 포맷: `- **<title>** [<source>] — <summary> (<new|day N>)\n  <url>`

3. **카테고리 판정**:
   - 항목이 brief.md의 카테고리 섹션 (`### 에이전트 프레임워크` 등) 하에 있으면 그 카테고리의 슬러그 사용
   - 한국어 섹션명 → 슬러그 매핑:
     - 에이전트 프레임워크 → agent-frameworks
     - LLM 하네스·평가 → llm-harness-eval
     - MCP → mcp
     - 코딩 에이전트 → coding-agents
     - 프롬프트·컨텍스트 엔지니어링 → prompt-context-engineering
   - TOP 5 섹션의 항목이면 `interests.md` 키워드 매칭으로 카테고리 결정.
     두 개 이상 매칭되면 가장 많이 매칭된 것, 동점이면 위 순서.
   - 어느 것도 매칭 안 되면 `uncategorized`

4. **스크립트 호출**:
   `.venv/bin/python -m scripts.save_item --url ... --title ... --summary ... --source ... --category ... --brief-date ...`

5. **결과 보고**: 스크립트 stdout을 사용자에게 그대로 보여줌.
```

### 3) `.claude/commands/saved.md` (신규)

`/saved` 슬래시 커맨드. 저장 항목 조회.

**인자 파싱**:
- `/saved` → `state/saved.json` 읽어 최근 10개 역순 표시
- `/saved <category>` → `saved/<category>.md`가 있으면 그 파일 렌더링, 없으면 "저장 항목 없음"
- `/saved <category> <N>` → `state/saved.json`에서 해당 카테고리 최신 N개만

**출력 형식** (기본, 카테고리 무관):

```markdown
# 📌 최근 저장 항목

1. [agent-frameworks] **The next evolution of the Agents SDK**
   요약: OpenAI가 샌드박스·모델 네이티브 하네스 도입
   출처: release_blogs · brief: 2026-04-16 · 저장: 2026-04-16 14:23
   https://openai.com/index/...

2. ...

(총 N개 저장됨 · `/saved <category>`로 필터)
```

### 4) 디렉토리·파일 초기화

- `saved/` 디렉토리는 첫 저장 시 자동 생성 (스크립트가 `mkdir -p`)
- `state/saved.json`은 첫 호출 시 자동 생성
- `.gitignore`: 아무것도 추가하지 않음 (저장 내역은 커밋 대상)

## 오류 처리

| 상황 | 동작 |
|------|------|
| `state/saved.json` 손상 JSON | 기존 파일을 `.corrupt-<timestamp>`로 백업 후 빈 상태로 시작 (`update_seen.py`와 동일) |
| `--category` 값이 허용 슬러그 아님 | stderr에 오류 출력, exit 2 |
| 필수 인자 누락 | usage 출력, exit 2 |
| 대상 brief.md 항목을 Claude가 못 찾음 | 사용자에게 "어느 URL 또는 제목인가요?" 1회 확인 후 재시도 |
| 카테고리 판정 실패 | `uncategorized` 사용 — 실패 아님 |
| 같은 URL 중복 | stdout `SKIP: ...`, exit 0 |

## 테스트

`tests/test_save_item.py`에 pytest로 작성. 기존 `test_archive_top5.py` 패턴 따라:

1. `test_new_item_saved` — 빈 상태에 신규 항목 1개 저장 → `items` 1개, md 파일 생성, 제목·URL 존재
2. `test_duplicate_url_skipped` — 이미 저장된 URL 재저장 → `items` 변화 없음, md 파일도 그대로, stdout에 `SKIP`
3. `test_prepend_order` — 항목 2개 순차 저장 → `items[0]`이 나중에 저장된 것
4. `test_same_day_appends_to_existing_date_block` — 같은 날 2번째 저장 → 단일 `## 2026-04-16 저장` 블록 안에 둘 다 존재
5. `test_different_day_creates_new_date_block` — 다른 날 저장 → 새 날짜 섹션 생성
6. `test_unknown_category_rejected` — `--category xyz` → exit 비-0
7. `test_uncategorized_accepted` — `--category uncategorized` → 정상 저장
8. `test_corrupt_state_backed_up` — 손상 JSON → `.corrupt-*` 백업 생성, 빈 상태로 계속
9. `test_missing_state_file_created` — `state/saved.json` 없을 때 자동 생성
10. `test_saved_dir_autocreated` — `saved/` 없을 때 자동 생성

수동 검증:
- 오늘 brief.md에서 한 항목 저장 → `/saved agent-frameworks` 조회 → 보이는지 확인
- 동일 항목 재저장 → SKIP 메시지 확인
- `/saved` (인자 없음) 조회 → 리스트 형식 확인

## 통합 지점

### 기존 `.claude/commands/brief.md`
- **변경 없음**. `/brief` 커맨드는 그대로 두고, 저장 로직은 `CLAUDE.md`가 전 세션에서 담당.
- 근거: 저장 의도는 `/brief` 직후뿐 아니라 다른 대화 맥락에서도 발생 가능 (예: "어제 brief에 있던 그 논문 저장해")

### `README.md`
- 섹션 추가: "관심 항목 저장" — 자연어 트리거 예시 + `/saved` 커맨드 사용법 간단 설명

### Git
- `scripts/save_item.py`, `.claude/commands/saved.md`, `CLAUDE.md`, `tests/test_save_item.py`, `saved/*.md`, `state/saved.json`, `README.md` 수정분, 본 스펙 문서 모두 커밋

## 비목표 (YAGNI)

- 태그·평점·노트 필드 없음 (요청 시 추후 추가)
- 전체 텍스트 재요약·웹 페치 없음
- 다중 사용자·원격 동기화 없음
- 저장 항목 삭제·수정 UI 없음 (사용자가 직접 md 파일 편집하면 됨)
- 백업·복구 로직 없음 (Git 자체가 이력 역할)
- `/brief` 실행 중 "실시간 북마크" 같은 특수 UI 없음 — 일반 대화 흐름으로 통합
