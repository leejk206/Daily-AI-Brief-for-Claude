# 2026-07-28 AI 트렌드 브리프

## 🔥 오늘의 TOP 5

1. **Anthropic: 오픈웨이트 모델에 대한 우리의 입장** — 프런티어 랩이 오픈웨이트 정책을 공식 선언, HN 1444댓글
   sources: anthropic_news, hacker_news, dcinside
   https://www.anthropic.com/news/position-open-weights-models

2. **Kimi K3: Open Frontier Intelligence** — 2.8T MoE·104B 활성·네이티브 비전·1M 컨텍스트 오픈 모델
   sources: huggingface, hacker_news
   https://huggingface.co/moonshotai/Kimi-K3

3. **Benchmarking Opus 5 on SlopCodeBench** — Opus 5를 실무형 코딩 벤치로 검증한 실측 리포트
   sources: hacker_news
   https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md

4. **microsoft/agent-governance-toolkit** — OWASP Agentic Top 10 전부 커버하는 에이전트 거버넌스 툴킷
   sources: github_trending
   https://github.com/microsoft/agent-governance-toolkit

5. **Agentic Context Management** — 에이전트 실패의 주범은 추론력이 아니라 컨텍스트 관리라는 주장
   sources: huggingface
   https://huggingface.co/papers/2607.21503

## 📋 카테고리별 나머지

### 프런티어 모델·주요 발표
- **upstage/Solar-Open2-250B** [huggingface] — 업스테이지의 250B급 오픈웨이트 신모델 공개 (new)
  https://huggingface.co/upstage/Solar-Open2-250B
- **poolside/Laguna-S-2.1** [huggingface] — poolside의 코드 특화 계열 신모델, 다운로드 6.7만 (new)
  https://huggingface.co/poolside/Laguna-S-2.1
- **thinkingmachines/Inkling** [huggingface] — Thinking Machines의 첫 멀티모달 공개 모델, 좋아요 1.6천 (new)
  https://huggingface.co/thinkingmachines/Inkling
- **microsoft/Fara1.5-27B** [huggingface] — MS의 27B 이미지-텍스트 모델, 컴퓨터 유즈 계열 후속 (new)
  https://huggingface.co/microsoft/Fara1.5-27B
- **Inviting hard questions** [anthropic_news] — Anthropic이 AI에 대한 가장 어려운 질문을 공개 모집 (new)
  https://www.anthropic.com/news/hard-questions

### 에이전트 프레임워크
- **Multi-Head Latent Control** [huggingface] — 추론 시점에 에이전트 의사결정을 제어하는 통합 인터페이스 (new)
  https://huggingface.co/papers/2607.14277
- **Multi-Agent Protocol Distillation** [huggingface] — 프로프라이어터리→오픈소스 에이전틱 검색 성능 격차 메우기 (new)
  https://huggingface.co/papers/2607.24280
- **JarvisHub** [huggingface] — 캔버스 네이티브 멀티모달 창작 에이전트용 오픈 하네스 (new)
  https://huggingface.co/papers/2607.23588
- **Molt** [huggingface] — 에이전틱 RL 실험을 위한 PyTorch 네이티브 학습 프레임워크 (new)
  https://huggingface.co/papers/2607.21653
- **Skill Self-Play** [huggingface] — 스킬을 공진화시켜 LLM 능력 한계를 밀어올리는 자기진화 학습 (new)
  https://huggingface.co/papers/2607.22529
- **IDEAgent** [huggingface] — 연구 아이디어 생성을 품질-다양성 탐색으로 푸는 에이전트 (new)
  https://huggingface.co/papers/2607.22375
- **StateAct** [huggingface] — 스크린샷 대신 프로그램 상태를 먼저 보는 장기 컴퓨터유즈 에이전트 (new)
  https://huggingface.co/papers/2607.22798
- **andrewyng/aisuite** [github_trending] — 여러 생성 AI 제공자를 하나의 인터페이스로 묶는 라우팅 레이어 (new)
  https://github.com/andrewyng/aisuite

### LLM 하네스·평가
- **Codifying the Judge** [huggingface] — LLM-as-a-judge를 프로그램으로 증류해 비용·지연·불투명성 해결 (new)
  https://huggingface.co/papers/2607.22561
- **DataPrep-Bench** [huggingface] — LLM을 '학습 데이터 준비자'로 평가하는 첫 통합 벤치마크 (new)
  https://huggingface.co/papers/2607.20465
- **A Frozen 12B Beats Frontier Models on Verified Work** [huggingface] — 모델을 얼린 채 검증 가능한 작업에서 100% 정확도 주장 (new)
  https://huggingface.co/papers/2607.23806
- **A $500 RL fine-tune of a 9B open model beat frontier models** [hacker_news] — 500달러 RL 파인튜닝으로 카탈로그 리뷰 태스크에서 프런티어 추월 (new)
  https://fermisense.com/when-machines-take-the-wheel/
- **Don't ask an LLM for a confidence score** [hacker_news] — LLM 자기보고 확신도는 신뢰할 수 없다는 실무 경고 (new)
  https://justinflick.com/2026/07/27/llm-confidence-scores.html
- **SceneActBench** [huggingface] — VLM 에이전트가 3D 씬을 보고 실제로 조작할 수 있는지 측정 (new)
  https://huggingface.co/papers/2607.22393
- **Reasoning Denoiser** [huggingface] — 추론 트레이스를 디노이징해 환각을 탐지하는 기법 (new)
  https://huggingface.co/papers/2607.22098
- **FinanceComplexQA** [huggingface] — 산업급 금융 문서에서 에이전틱 추론을 평가하는 벤치 (new)
  https://huggingface.co/papers/2607.19238

### 코딩 에이전트
- **bradautomates/claude-video** [github_trending] — Claude에 영상 시청 능력을 붙이는 도구, 하루 989스타 (new)
  https://github.com/bradautomates/claude-video
- **Kwaipilot/KAT-Coder-V2.5-Dev** [huggingface] — Kwaipilot의 코딩 특화 모델 신버전 (new)
  https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev

### 프롬프트·컨텍스트 엔지니어링
- **The Physics of Multi-Turn Long-Horizon Planning** [huggingface] — 멀티턴 장기 계획 능력을 프리트레이닝부터 분해 분석 (new)
  https://huggingface.co/papers/2607.24720
- **Sample-Efficient Learning from Agent Experience** [huggingface] — 에이전트 경험을 적은 샘플로 학습에 되먹이는 방법 (new)
  https://huggingface.co/papers/2607.21051

## 💬 커뮤니티 동향 (DCInside 특이점갤)
- **FrontierMath 두번째 Open Problem 해결** — AI가 미해결 수학 문제를 또 하나 풀었다는 소식 정리
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1343993&exception_mode=recommend&page=1
- **4배 싼 가격으로 ARC-AGI-3에서 97% 달성** — 비용 대비 추론 성능 급개선 사례 공유
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1344266&exception_mode=recommend&page=1
- **Opus 5 3D RTS 원샷** — Opus 5로 3D RTS를 원샷 생성한 실사용 데모 반응
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1344086&exception_mode=recommend&page=1
- **엔트로픽) 오픈 웨이트 모델에 대한 우리의 입장** — 오늘 TOP 1 발표에 대한 국내 커뮤니티 해석·반응
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1343520&exception_mode=recommend&page=1
- **엔비디아, 수츠케버의 AI 랩 'SSI'에 투자** — 엔비디아 50억달러 SSI 투자설과 그 함의 토론
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1343490&exception_mode=recommend&page=1

## ⚠️ 소스 상태
- github_trending: ok (12 items / 3 matched)
- hacker_news: ok (30 items / 5 matched)
- huggingface: ok (70 items / 23 matched)
- release_blogs: ok (60 items / 0 matched — 해당 발표 전부 과거 TOP 5 아카이브 중복)
- anthropic_news: ok (13 items / 2 matched)
- dcinside: ok (30 items / 5 curated)
