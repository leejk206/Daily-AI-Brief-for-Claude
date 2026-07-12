# 2026-07-13 AI 트렌드 브리프

## 🔥 오늘의 TOP 5

1. **What xAI's Grok build CLI sends to xAI: A wire-level analysis** — 코딩 CLI가 코드·시크릿을 통째로 전송한다는 실측 분석
   sources: hacker_news, dcinside(커뮤니티 반향)
   https://gist.github.com/cereblab/dc9a40bc26120f4540e4e09b75ffb547

2. **Claude Code sends 33k tokens before reading the prompt; OpenCode sends 7k** — 하네스별 시스템 프롬프트 오버헤드 실측, 컨텍스트 비용 직결
   sources: hacker_news
   https://systima.ai/blog/claude-code-vs-opencode-token-overhead

3. **Old and new apps, via modern coding agents** — 테렌스 타오가 코딩 에이전트로 앱을 만든 실전 기록
   sources: hacker_news
   https://terrytao.wordpress.com/2026/07/11/old-and-new-apps-via-modern-coding-agents/

4. **Dicklesworthstone/destructive_command_guard** — 에이전트의 위험한 git·shell 명령을 차단하는 가드레일, 하루 444스타
   sources: github_trending
   https://github.com/Dicklesworthstone/destructive_command_guard

5. **Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing** — 롱컨텍스트 비용을 줄이는 선형 어텐션 4종 비교 분석
   sources: huggingface
   https://huggingface.co/papers/2607.07953

## 📋 카테고리별 나머지

### 프런티어 모델·주요 발표
- **GPT-5.6 is now the preferred model in Microsoft 365 Copilot** [release_blogs] — GPT-5.6이 M365 Copilot 기본 모델로 승격 (day 2)
  https://openai.com/index/gpt-5-6-preferred-model-microsoft-365-copilot
- **Introducing GPT-Live** [release_blogs] — ChatGPT 음성을 구동하는 신세대 보이스 모델 (day 2)
  https://openai.com/index/introducing-gpt-live
- **Introducing a way to reflect on how you use Claude** [anthropic_news] — 사용자가 자신의 Claude 사용 패턴을 되돌아보는 기능 (new)
  https://www.anthropic.com/news/reflect-with-claude
- **Inviting hard questions** [anthropic_news] — Anthropic이 자사에 대한 어려운 질문을 공개 초청 (new)
  https://www.anthropic.com/news/hard-questions
- **Ben Bernanke appointed to Anthropic's Long-Term Benefit Trust** [anthropic_news] — 전 연준 의장이 Anthropic 장기이익신탁에 합류 (day 2)
  https://www.anthropic.com/news/ben-bernanke
- **UST is bringing Claude to physical AI** [anthropic_news] — UST가 Claude를 피지컬 AI 영역으로 확장 (day 2)
  https://www.anthropic.com/news/ust-claude

### 에이전트 프레임워크
- **Shubhamsaboo/awesome-llm-apps** [github_trending] — 바로 돌려보는 AI 에이전트·RAG 앱 100선, 하루 450스타 (new)
  https://github.com/Shubhamsaboo/awesome-llm-apps
- **Automating the Design of Embodied Agent Architectures** [huggingface] — 지각·메모리·계획 모듈 구성을 자동 탐색하는 연구 (new)
  https://huggingface.co/papers/2606.30111
- **Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning** [huggingface] — 롱호라이즌 에이전트용 비동기 RL 파이프라인 (new)
  https://huggingface.co/papers/2607.07508
- **Remember When It Matters: Proactive Memory Agent for Long-Horizon Agents** [huggingface] — 긴 트라젝토리에 묻힌 정보를 선제적으로 끌어올리는 메모리 에이전트 (day 2)
  https://huggingface.co/papers/2607.08716

### LLM 하네스·평가
- **AgentLens: Production-Assessed Trajectory Reviews for Coding Agent Evaluation** [huggingface] — 통과/실패 1비트가 아닌 에이전트 궤적 전체를 평가하는 벤치마크 (day 2)
  https://huggingface.co/papers/2607.06624
- **UniClawBench: A Universal Benchmark for Proactive Agents on Real-World Tasks** [huggingface] — 실제 도구를 쓰는 능동형 에이전트 범용 벤치마크 (day 2)
  https://huggingface.co/papers/2607.08768
- **CausalDS: Benchmarking Causal Reasoning in Data-Science Agents** [huggingface] — 데이터사이언스 에이전트의 인과추론을 재는 벤치마크 (new)
  https://huggingface.co/papers/2607.08093
- **Introducing GeneBench-Pro** [release_blogs] — 유전체·생물학 실전 데이터셋 기반 OpenAI 신규 벤치마크 (new)
  https://openai.com/index/introducing-genebench-pro

### 코딩 에이전트
- **Nutlope/hallmark** [github_trending] — Claude Code·Cursor·Codex용 안티 AI-슬롭 디자인 스킬 (new)
  https://github.com/Nutlope/hallmark
- **ColeMurray/background-agents** [github_trending] — 오픈소스 백그라운드 코딩 에이전트 시스템 (new)
  https://github.com/ColeMurray/background-agents
- **SWE-Review: Closing the Loop on Issue Resolution with Agentic Code Review** [huggingface] — PR 생성 후 리뷰·수정까지 닫는 에이전틱 코드리뷰 (day 2)
  https://huggingface.co/papers/2607.06065
- **Migrating a production AI agent to GPT-5.6: 2.2x faster, 27% cheaper** [hacker_news] — 프로덕션 에이전트를 GPT-5.6으로 옮긴 실측 리포트 (new)
  https://ploy.ai/blog/migrating-a-production-ai-agent-to-gpt-5-6

### 프롬프트·컨텍스트 엔지니어링
- **Sparse Delta Memory: Scaling the State of Linear RNNs through Sparsity** [huggingface] — 희소성으로 선형 어텐션의 롱컨텍스트 회상력을 키움 (new)
  https://huggingface.co/papers/2607.07386
- **Jet-Long: Efficient Long-Context Extension with Dynamic Bifocal RoPE** [huggingface] — 사전학습 윈도우를 넘는 컨텍스트 확장 기법 (day 2)
  https://huggingface.co/papers/2607.07740
- **LLM-as-a-Tutor: Policy-Aware Prompt Adaptation for Non-Verifiable RL** [huggingface] — 학습 중 프롬프트 자체를 정책에 맞춰 적응시키는 RL (new)
  https://huggingface.co/papers/2607.04412

## 📌 Still trending (day 2+)
- **GPT-5.6 is now the preferred model in Microsoft 365 Copilot** [day 2] — GPT-5.6 엔터프라이즈 확산 신호
  https://openai.com/index/gpt-5-6-preferred-model-microsoft-365-copilot
- **Introducing GPT-Live** [day 2] — 보이스 모델 세대교체
  https://openai.com/index/introducing-gpt-live
- **Remember When It Matters: Proactive Memory Agent** [day 2] — 에이전트 메모리 연구 계속 주목
  https://huggingface.co/papers/2607.08716
- **AgentLens** [day 2] — 코딩 에이전트 궤적 평가 벤치마크
  https://huggingface.co/papers/2607.06624
- **UniClawBench** [day 2] — 능동형 에이전트 벤치마크
  https://huggingface.co/papers/2607.08768
- **SWE-Review** [day 2] — 에이전틱 코드리뷰 루프
  https://huggingface.co/papers/2607.06065
- **Jet-Long** [day 2] — 롱컨텍스트 확장 기법
  https://huggingface.co/papers/2607.07740

## 💬 커뮤니티 동향 (DCInside 특이점갤)
- **속보) 알트만 : GPT 5.6 Sol이 세계 최고 모델인 이유** — 알트만 발언 정리, 갤 최대 호응(추천 116·1.4만 조회)
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1311723&exception_mode=recommend&page=1
- **그록 빌드, "모든 코드, 비밀, 데이터 업로드"** — 오늘 TOP 1 Grok CLI 전송 이슈의 국내 커뮤니티 반향
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1312883&exception_mode=recommend&page=1
- **개인적인 모델 체감 (7월)** — 7월 기준 주요 모델 실사용 체감 비교
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1313775&exception_mode=recommend&page=1
- **공식문서 참고한 5.6 업데이트 관련 사용 가이드** — 공식문서 기반 GPT-5.6 실무 사용 가이드
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1306577&exception_mode=recommend&page=1
- **GPT-5.6 3종 수능 일반/고난도 결과** — GPT-5.6 3종 모델의 수능 벤치마크 실측
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1310284&exception_mode=recommend&page=1

## ⚠️ 소스 상태
- github_trending: ok (17 items / 4 matched)
- hacker_news: ok (30 items / 4 matched)
- huggingface: ok (60 items / 10 matched)
- release_blogs: ok (60 items / 3 matched)
- anthropic_news: ok (10 items / 4 matched)
- dcinside: ok (30 items / 5 curated)
