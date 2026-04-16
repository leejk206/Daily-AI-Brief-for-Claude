---
description: Show saved brief items
---

You are running the `/saved` command for `daily-ai-brief`.

## Arguments

Parse `$ARGUMENTS` (may be empty):
- empty → list mode
- one word matching a valid category slug → category mode
- `<category> <N>` where N is an integer → category-limited mode

Valid category slugs: `agent-frameworks`, `llm-harness-eval`, `mcp`, `coding-agents`, `prompt-context-engineering`, `uncategorized`.

## List mode (no arguments)

1. Read `state/saved.json`. If missing or `items` is empty, tell the user "저장된 항목이 없습니다." and stop.
2. Take the first 10 items (already sorted newest-first).
3. Render:

```
# 📌 최근 저장 항목

1. [<category>] **<title>**
   요약: <summary>
   출처: <source> · brief: <brief_date> · 저장: <saved_at의 YYYY-MM-DD HH:MM>
   <url>

2. ...

(총 <len(items)>개 저장됨 · `/saved <category>`로 필터)
```

## Category mode

1. If `saved/<category>.md` exists, Read it and output the file body verbatim.
2. Otherwise output "저장 항목 없음: <category>".

## Category-limited mode (`<category> <N>`)

1. Read `state/saved.json`.
2. Filter `items` where `category == <category>`.
3. Take first N.
4. Render in the same list-mode format, prefixed with `# 📌 <category> (최근 N개)`.
