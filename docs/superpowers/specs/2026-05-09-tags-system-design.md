# Tags System Design

- **날짜**: 2026-05-09
- **저자**: jk_lee + Claude
- **상태**: 설계 승인 (구현 plan 작성 단계 진입 예정)

## 배경

`daily-ai-brief`는 매일 아침 GitHub/HN/HuggingFace/release blogs에서 항목을 수집해 `interests.md`의 5개 카테고리로 분류하고 brief.md를 생성한다. 현재 분류 단위는 **카테고리 1개/항목**(파일 단위 굵은 분류)이며, `state/seen.json`은 URL 기반 dedup만 한다.

문제: 누적되는 brief 항목과 saved 항목에 대해 **세밀한 검색·필터링이 불가능**하다. "MCP 서버 관련 저장한 거 보여줘" 같은 자연어 질의를 카테고리만으로는 답할 수 없고, grep은 동의어·표현 변형에 약하다.

## 목표

세밀한 태그 어휘를 도입해, 사용자가 자연어로 과거 brief·saved 항목을 검색·필터링할 수 있게 한다.

**비목적**:
- 벡터 임베딩 기반 의미 검색 (별도 검토 후 기각)
- 자동 카테고리 재분류 (interests.md 카테고리 그대로 둠)
- 태그 정확도 자동 평가
- 태그 사용 통계 대시보드

## 핵심 결정

| 결정 | 선택 | 사유 |
|------|------|------|
| 도입 동기 | **검색·필터링** | 누적 항목 회수 가능성 향상이 가장 절실 |
| 태깅 범위 | **과거 brief 수동 백필 + 앞으로 자동** | 일회성 백필로 과거 자산 활성화, 미래 분은 운영 자동화 |
| 어휘 관리 | **하이브리드** (canonical + candidate, 2회 사용 시 승격) | 초기 일관성 + 시간 따른 자연 확장 |
| 데이터 저장 | **중앙 인덱스 `state/tags.json`** | 단일 파일 검색이라 빠름. 기존 state 패턴과 일관 |
| 검색 UX | **자연어 질의** | 새 명령어 추가 부담 없음. Claude가 인덱스 직접 읽음 |

## 아키텍처

### 파일 구조 변경

```
daily-ai-brief/
├── AGENTS.md              ← 신규: 태깅 정책 (Claude가 매 /brief·/save·백필 시 참조)
├── tags.md                ← 신규: 태그 사전 (canonical + candidate)
├── state/
│   └── tags.json          ← 신규: URL → 태그 매핑 인덱스 (진실의 원천)
├── CLAUDE.md              ← 갱신: AGENTS.md 참조 추가, 자연어 검색 절차 추가
├── .claude/commands/
│   └── brief.md           ← 갱신: Step 7.5 — 태깅 추가
└── scripts/
    ├── save_item.py       ← 갱신: --tags 인자 추가, saved.json·md에 태그 함께 저장
    └── tags_state.py      ← 신규: state/tags.json 읽기·쓰기 헬퍼 (loader, merger, corruption backup)
```

### 역할 분담

| 파일 | 역할 | 누가 갱신 |
|------|------|-----------|
| `AGENTS.md` | "어떻게 태깅할지" 정책 (정적 문서) | 사람 (드물게) |
| `tags.md` | 태그 사전 (canonical/candidate 섹션) | Claude (/brief 시), 사람 (큐레이션) |
| `state/tags.json` | 모든 항목의 태그 데이터 (진실의 원천) | Claude (/brief, 백필 시) |

**충돌 시 우선순위**: 어휘는 `tags.md`(사람 통제), 데이터는 `state/tags.json`. 둘이 충돌하면 tags.md를 따름.

## 컴포넌트

### `AGENTS.md` (신규)

태깅 정책 문서. Claude가 `/brief`, `/save`, 백필, 자연어 검색 시 매번 참조.

**포함 내용**:
1. **언제 태깅하나** — `/brief` Step 7.5 (자동), 백필 시 (사용자 트리거 후 수동), `/save` 시는 기존 태그 carry over만
2. **태그 선정 규칙**
   - 항목당 1~5개
   - `tags.md`의 canonical에서 우선 선택
   - 적당한 게 없으면 candidate에서 선택
   - 둘 다 없으면 새 태그 제안 (소문자, 하이픈, 영문, ≤20자) → candidate 섹션에 추가
3. **승격 규칙** — candidate 태그가 사용되면 `state/tags.json`에서 과거 사용 횟수 확인 → 누적 2회 이상이면 canonical로 이동 (Claude가 `tags.md` 편집)
4. **금지 패턴**
   - 카테고리 슬러그 사용 금지 (`agent-frameworks`, `mcp` 등 — 카테고리와 중복)
   - 너무 일반적 태그 금지 (`ai`, `llm` 등 — 모든 항목에 해당)
   - 일회성 고유명사 금지 (반복 사용 가능성 있을 때만 OK: `claude-code`, `mcp-server`)
5. **이름 규약**
   - 소문자, 하이픈만 (스페이스·언더스코어·CamelCase 금지)
   - 영문만 (한글 태그 금지 — 검색 일관성)

### `tags.md` (신규)

```markdown
# Tags Registry

이 파일은 daily-ai-brief의 canonical 태그 사전입니다.
신규 태그는 candidate 섹션에 들어가고, 누적 2회 사용되면 canonical로 승격됩니다.

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

**초기 시드 ~12개**. 과거 12개 brief 검토 결과 자주 등장한 토픽 기준.

### `state/tags.json` (신규)

```json
{
  "version": 1,
  "items": {
    "https://deepmind.google/blog/alphaevolve-impact/": {
      "title": "AlphaEvolve: Gemini-powered coding agent...",
      "summary": "DeepMind 코딩 에이전트의 산업·과학 임팩트 사례",
      "category": "coding-agents",
      "source": "deepmind",
      "brief_date": "2026-05-08",
      "tags": ["coding-agent", "research"],
      "tagged_at": "2026-05-08T07:32:11+09:00"
    }
  }
}
```

URL이 키 (이미 dedup됨). 항목은 시간이 지나도 누적 (삭제 안 함). category 필드는 **태깅 시점 카테고리**를 박제.

## 데이터 흐름

### Flow 1: `/brief` (자동 태깅)

기존 Step 7과 8 사이에 **Step 7.5 — 항목 태깅** 삽입:

1. `tags.md`, `AGENTS.md` 읽기
2. `state/tags.json` 읽기 (없으면 빈 인덱스)
3. brief.md의 모든 항목(TOP 5 + 카테고리별)에 대해:
   - AGENTS.md 정책 따라 1~5개 태그 선정
   - tags.md에 없는 새 태그면:
     - state/tags.json에서 과거 사용 횟수 카운트
     - 누적 2회 이상 → tags.md의 canonical 섹션에 추가
     - 1회 → tags.md의 candidate 섹션에 추가
   - `{url, title, summary, category, source, brief_date, tags, tagged_at}`을 state/tags.json에 추가
4. state/tags.json, tags.md 저장

이후 Step 8(selected.json, top5.json), Step 9(state 갱신), Step 10(commit) 진행. Step 10의 `git add`에 `state/tags.json`, `tags.md` 포함.

### Flow 2: `/save` (태그 carry over)

CLAUDE.md의 저장 의도 처리 절차(Step 4 직전)에 태그 결정 단계 추가. Claude가:
1. `state/tags.json`에서 해당 URL 조회
2. **있으면** → 그 항목의 tags를 그대로 사용
3. **없으면** (legacy 항목 또는 백필 안 된 항목) → AGENTS.md 정책 따라 즉석 태깅(fallback). 태깅 결과를 `state/tags.json`에도 추가
4. 결정된 tags를 `--tags "tag1,tag2"` 인자로 `save_item.py` 호출 시 전달

`scripts/save_item.py` 수정:
- `--tags` 인자 추가 (콤마 구분 문자열, optional, 기본 빈 리스트)
- 받은 tags를 `state/saved.json`의 항목 객체에 `tags: [...]` 필드로 저장
- saved/<category>.md의 항목 블록에 태그 줄 추가 (태그 있을 때만):

```markdown
### AlphaEvolve: ...
- **요약**: ...
- **태그**: coding-agent, research
- **출처**: deepmind
- **brief 날짜**: 2026-05-08
- **URL**: ...
```

태그 줄은 **태그가 있을 때만** 추가 (legacy 호환).

### Flow 3: 백필 (수동, 사용자 트리거)

CLAUDE.md에 절차 추가. 사용자가 자연어로 트리거:
- "2026-04-15 brief 백필해줘"
- "지난 일주일 brief 다 백필"
- "전체 백필"

Claude가 하는 일:
1. 대상 brief.md 파일들 식별 (`daily/<date>/brief.md`)
2. 각 brief.md의 모든 항목 추출 (TOP 5 + 카테고리별)
3. AGENTS.md 정책 따라 태깅 (Flow 1과 동일 로직)
4. state/tags.json, tags.md 갱신
5. **saved.json 항목도 같이 처리** — saved.json의 모든 항목 중 state/tags.json에 없는 URL은 태깅
6. 결과 보고: "N개 brief, M개 항목 태깅. 신규 candidate 태그: [...]"
7. git commit: `tags: backfill <date or range>`

별도 스크립트 없음. Claude가 직접 수행.

### Flow 4: 자연어 검색

CLAUDE.md에 "태그 기반 조회" 절 추가.

사용자 트리거 패턴:
- "MCP 관련 저장한 거 보여줘"
- "RL 태그 달린 항목 다 찾아줘"
- "최근 일주일 multi-agent 항목"

Claude가 하는 일:
1. 질의에서 태그 후보 추출 (tags.md 참조해 정규화 — "강화학습" → `rl`)
2. `state/tags.json`을 읽어 매칭 항목 필터
3. 필요시 `state/saved.json`과 교집합 (저장된 것만 보고 싶다는 의도면)
4. 시간순으로 출력:

```
# 🏷️ rl 태그 항목 (총 12개)

1. **AlphaEvolve...** (2026-05-08, coding-agents) [저장됨]
   요약: ...
   https://...
```

## 에러 처리

| 케이스 | 처리 |
|-------|------|
| `state/tags.json` 손상 | `state/tags.json.corrupt-<timestamp>` 백업 후 빈 인덱스로 시작. WARNING 출력. 진행 계속 |
| `tags.md`에서 태그 중복 (canonical+candidate) | canonical 우선, candidate에서 자동 제거. WARNING |
| 같은 URL이 여러 brief에 등장 | 태그 합집합 갱신. brief_date는 최초 시점 유지. tagged_at만 갱신 |
| 백필 중 일부 항목 실패 | 다른 항목 계속 진행. 결과 보고에 실패 명시. 부분 성공 그대로 commit |
| 신규 태그 폭주 (1회 /brief에서 ≥5개 신규) | WARNING — 사용자에게 보고하고 검토 요청 |
| saved.json에 있지만 tags.json에 없는 URL | `/save` 시 fallback 즉시 태깅 + 백필 시 saved.json도 처리 (이중 안전망) |

## 테스팅

### 자동 테스트 (pytest)

**`tests/test_save_item_with_tags.py`** — 기존 `test_save_item.py` 확장
- `--tags "rl,multi-agent"` 인자로 저장 시 saved.json·saved/<category>.md 양쪽에 태그 반영
- `--tags` 미지정 또는 빈 문자열 시 saved.json에 `tags: []`, md에 태그 줄 없음 (legacy 호환)
- 잘못된 형식의 `--tags` (공백, 빈 토큰 등) 정규화 확인
- 참고: Claude의 fallback 태깅 동작은 LLM 출력이라 자동 테스트 대상 아님

**`tests/test_tags_state.py`** — 신규
- `state/tags.json` 읽기·쓰기
- URL 키 중복 시 합집합 갱신 (tags 머지, brief_date 유지, tagged_at 갱신)
- 손상 파일 자동 백업

### 수동 검증

LLM 출력이라 자동화 의미 작음:
- `/brief` Step 7.5의 태깅 품질
- 백필 결과 정확성
- 자연어 검색 응답 적절성

→ 첫 1주일은 매일 brief 후 state/tags.json diff와 tags.md 변경사항 사용자가 직접 검토. 이상한 태깅 발견 시 AGENTS.md 정책 보강.

### 회귀 테스트

기존 테스트 모두 통과:
- `tests/test_save_item.py` (legacy 호환)
- `tests/test_update_seen.py`
- `tests/test_archive_top5.py`

`save_item.py`의 출력 포맷 변경은 태그 있을 때만 추가하므로 기존 테스트 그대로 통과해야 함.

## 마이그레이션 단계 (구현 순서 제안)

1. AGENTS.md, tags.md (canonical 시드 + 빈 candidate) 작성
2. `state/tags.json` 빈 파일 생성 + 읽기·쓰기 헬퍼 (`scripts/tags_state.py`)
3. `scripts/save_item.py`에 태그 carry over 추가 + 테스트
4. `.claude/commands/brief.md`에 Step 7.5 추가
5. CLAUDE.md에 백필·자연어 검색 절차 추가
6. 과거 12개 brief 백필 (사용자 트리거)
7. 1주일 운영 후 회고 — 태그 품질·정책 보강

## 명시적 비목적 (Out of Scope)

- 벡터 임베딩 기반 의미 검색
- 카테고리 자동 재분류
- 태그 그래프·관계 (synonym, parent-child) — 발견 시 사람이 수동 머지
- 태그 사용 통계 대시보드
- 태깅 정확도 자동 평가
- `tags.md` 자동 정리·압축 (필요해지면 그때)
