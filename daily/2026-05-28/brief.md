# 2026-05-28 AI 트렌드 브리프

## 🔥 오늘의 TOP 5

1. **I think Anthropic and OpenAI have found product-market fit** — Simon Willison이 Claude/Codex 도달 단계를 정리, HN 844pt
   sources: hacker_news
   https://news.ycombinator.com/item?id=48296794

2. **Agent Explorative Policy Optimization for Multimodal Agentic Reasoning** — 멀티모달 에이전틱 추론용 탐험적 정책 최적화
   sources: huggingface
   https://huggingface.co/papers/2605.28774

3. **Gamma-World: Generative Multi-Agent World Modeling Beyond Two Players** — 다수 플레이어용 생성형 멀티에이전트 월드모델
   sources: huggingface
   https://huggingface.co/papers/2605.28816

4. **MemTrace: Tracing and Attributing Errors in Large Language Model Memory Systems** — LLM 메모리 시스템의 오류를 추적·귀속하는 디버깅 프레임워크
   sources: huggingface
   https://huggingface.co/papers/2605.28732

5. **Cisco and OpenAI redefine enterprise engineering with Codex** — Cisco가 Codex로 AI-네이티브 개발·결함 자동 수정에 스케일링
   sources: release_blogs
   https://openai.com/index/cisco

## 📋 카테고리별 나머지

### 에이전트 프레임워크
- **Self-Improving Language Models with Bidirectional Evolutionary Search** [huggingface] — 양방향 진화 탐색 기반 자가 개선 LM (new)
  https://huggingface.co/papers/2605.28814
- **ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence** [huggingface] — 증거 사슬 기반 인간 수준 자율 연구 에이전트 (new)
  https://huggingface.co/papers/2605.26340
- **Rethinking Memory as Continuously Evolving Connectivity** [huggingface] — 정적 저장소가 아닌 연속 진화 연결성으로서의 에이전트 메모리 (new)
  https://huggingface.co/papers/2605.28773
- **QUACK: Auditing Communicated Knowledge in Multimodal Social Deduction Agents** [huggingface] — 사회 추리 게임에서 멀티에이전트 통신·신념 감사 (new)
  https://huggingface.co/papers/2605.27068
- **AgensFlow: A Coordination-Policy Substrate for Multi-Agent Systems** [huggingface] — 멀티에이전트 조정 결정을 학습하는 정책 기판 (new)
  https://huggingface.co/papers/2605.27466
- **ESC-Skills: Discovering and Self-Evolving Skills for Emotional Support Conversations** [huggingface] — 감정 지원 대화용 스킬 발견·자가 진화 프레임워크 (new)
  https://huggingface.co/papers/2605.27908
- **AgentFugue: Agent Scaling for Long-Horizon Tasks through Collective Reasoning** [huggingface] — 같은 과제에 다수 피어 에이전트를 스케일아웃하는 집단 추론 (new)
  https://huggingface.co/papers/2605.24486
- **SkillGrad: Optimizing Agent Skills Like Gradient Descent** [huggingface] — 경사하강처럼 에이전트 스킬을 최적화하는 진화 기법 (new)
  https://huggingface.co/papers/2605.27760
- **CUA-Gym: Scaling Verifiable Training Environments and Tasks for Computer-Use Agents** [huggingface] — 컴퓨터 사용 에이전트용 검증 가능 RL 환경·태스크 (day 2)
  https://huggingface.co/papers/2605.25624
- **Personalize-then-Store: Benchmarking and Learning Personalized Memory for Long-horizon Agents** [huggingface] — 장기 에이전트의 개인화 메모리 벤치마크 (day 2)
  https://huggingface.co/papers/2605.25535
- **SAM: State-Adaptive Memory for Long-Horizon Reasoning Agent** [huggingface] — 장기 추론용 상태 적응형 메모리 (day 2)
  https://huggingface.co/papers/2605.24468

### LLM 하네스·평가
- **LiveBrowseComp: Are Search Agents Searching, or Just Verifying What They Already Know?** [huggingface] — 검색 에이전트의 내재 지식 의존도(IKD) 진단 (new)
  https://huggingface.co/papers/2605.28721
- **HRBench: Benchmarking Thinking-Mode Switch Strategies in Hybrid-Reasoning LLMs** [huggingface] — 하이브리드 추론 LLM의 사고 모드 스위치 벤치마크 (new)
  https://huggingface.co/papers/2605.28398
- **VibeSearchBench: Benchmarking Long-horizon Proactive Search in the Wild** [huggingface] — 장기·선제적 웹 검색 평가-경험 갭을 메우는 벤치마크 (new)
  https://huggingface.co/papers/2605.27882
- **Agentic CLEAR: Automating Multi-Level Evaluation of LLM Agents** [huggingface] — LLM 에이전트의 다층 자동 평가 (day 2)
  https://huggingface.co/papers/2605.22608
- **VitaBench 2.0: Evaluating Personalized and Proactive Agents in Long-Term User Interactions** [huggingface] — 장기 사용자 상호작용에서 개인화·선제 에이전트 평가 (day 2)
  https://huggingface.co/papers/2605.27141
- **RankJudge: A Multi-Turn LLM-as-a-Judge Synthetic Benchmark Generator** [huggingface] — 다턴 LLM-judge 합성 벤치마크 생성기 (day 2)
  https://huggingface.co/papers/2605.21748

### 코딩 에이전트
- **Chachamaru127/claude-code-harness** [github_trending] — Claude Code 전용 자율 Plan→Work→Review 사이클 하네스 (new)
  https://github.com/Chachamaru127/claude-code-harness
- **Learn from Weaknesses: Automated Domain Specialization for Small Computer-Use Agents** [huggingface] — 소형 CUA의 도메인별 약점을 자동 특화 (new)
  https://huggingface.co/papers/2605.28775
- **Verus-SpecGym: An Agentic Environment for Evaluating Specification Autoformalization** [huggingface] — 형식 검증으로 코딩 에이전트 정확성 보장 (new)
  https://huggingface.co/papers/2605.26457
- **Warp's big bet on building open source with GPT-5.5** [release_blogs] — Warp가 GPT-5.5로 로컬·클라우드·OSS 코딩 에이전트 통합 (new)
  https://openai.com/index/warp
- **Leonxlnx/taste-skill** [github_trending] — AI에 "취향"을 부여해 진부한 생성을 막는 스킬 파일 (new)
  https://github.com/Leonxlnx/taste-skill
- **ECHO: Terminal Agents Learn World Models for Free** [huggingface] — 터미널 stdout·로그를 감독 신호로 활용하는 CLI 에이전트 (day 2)
  https://huggingface.co/papers/2605.24517

### 프롬프트·컨텍스트 엔지니어링
- **Investigating how prompt politeness affects LLM accuracy (2025)** [hacker_news] — 프롬프트 공손함이 LLM 정확도에 미치는 영향 측정 (new)
  https://news.ycombinator.com/item?id=48276429
- **hardikpandya/stop-slop** [github_trending] — 글에서 AI 티 나는 표현을 제거하는 스킬 파일 (new)
  https://github.com/hardikpandya/stop-slop
- **Language Models Need Sleep** [huggingface] — 컨텍스트를 빠른 가중치로 응축하는 수면 같은 통합 메커니즘 (day 2)
  https://huggingface.co/papers/2605.26099
- **Share More, Search Less: Collaborative Parallel Thinking for Efficient Test-Time Scaling** [huggingface] — 병렬 추론 분기 간 발견 공유로 효율 개선 (day 2)
  https://huggingface.co/papers/2605.27030

## 📌 Still trending (day 2+)
- **CUA-Gym: Verifiable Training Environments for Computer-Use Agents** [day 2] — 검증 가능 CUA 학습 환경, 어제에 이어 노출
  https://huggingface.co/papers/2605.25624
- **Agentic CLEAR: Automating Multi-Level Evaluation of LLM Agents** [day 2] — 다층 자동 평가 프레임워크, 어제에 이어 노출
  https://huggingface.co/papers/2605.22608
- **ECHO: Terminal Agents Learn World Models for Free** [day 2] — CLI 에이전트의 자가 학습 월드 모델, 어제에 이어 노출
  https://huggingface.co/papers/2605.24517
- **Language Models Need Sleep** [day 2] — 컨텍스트 통합 메커니즘 제안, 어제에 이어 노출
  https://huggingface.co/papers/2605.26099

## ⚠️ 소스 상태
- github_trending: ok (17 items / 3 matched)
- hacker_news: ok (30 items / 2 matched)
- huggingface: ok (61 items / 20 matched)
- release_blogs: ok (40 items / 2 matched)
