# 2026-07-29 AI 트렌드 브리프

## 🔥 오늘의 TOP 5

1. **Kimi K3: Open Frontier Intelligence (테크 리포트)** — 2.8T MoE·104B 활성·1M 컨텍스트 오픈 프런티어 모델의 설계 공개
   sources: huggingface, hacker_news
   https://huggingface.co/papers/2607.24653

2. **Codex Security** — OpenAI가 코딩 에이전트 보안 자료를 공개, HN 최상위 화제
   sources: hacker_news
   https://github.com/openai/codex-security

3. **Introducing Gemini 3.6 Flash, 3.5 Flash-Lite, and 3.5 Flash Cyber** — 구글이 Flash 계열 3종 동시 공개, 보안 특화 모델 포함
   sources: release_blogs
   https://deepmind.google/blog/introducing-gemini-3-6-flash-3-5-flash-lite-and-3-5-flash-cyber/

4. **A New Role for Relevance: Guiding Corpus Interaction in Agentic Search** — top-k 검색을 넘어 코퍼스를 직접 탐색하는 에이전틱 검색 패러다임
   sources: huggingface
   https://huggingface.co/papers/2607.24223

5. **Keep It InMind: Benchmarking the Implicit-Association Blind Spot in Agent Memory** — 에이전트 장기기억의 "질의와 안 닮은 기억" 사각지대를 벤치마크화
   sources: huggingface
   https://huggingface.co/papers/2607.24368

## 📋 카테고리별 나머지

### 프런티어 모델·주요 발표
- **Kimi K3 Architecture Overview and Notes** [hacker_news] — Sebastian Raschka의 K3 아키텍처(Delta Attention·Attention Residuals) 해설 (new)
  https://sebastianraschka.com/blog/2026/kimi-k3-architecture-notes.html
- **Safety and alignment in an era of long-horizon models** [release_blogs] — 장시간 실행 모델 배포에서 관찰한 실패 사례와 보완책 정리 (new)
  https://openai.com/index/safety-alignment-long-horizon-models
- **Shieldstral** [huggingface] — 3B 정책 적응형 멀티모달 안전 분류기, 7배 큰 모델과 동급 성능 (new)
  https://huggingface.co/papers/2607.25857
- **Nanbeige4.2-3B** [huggingface] — 소형 텍스트 생성 모델, 하루 1.9만 다운로드로 급부상 (new)
  https://huggingface.co/Nanbeige/Nanbeige4.2-3B

### 에이전트 프레임워크
- **A Vocabulary for Multi-Agent Automated Research Systems** [huggingface] — 자동 연구 멀티에이전트 시스템의 설계 선택을 기술하는 공통 어휘 제안 (new)
  https://huggingface.co/papers/2607.22682
- **Towards Robust Reinforcement Learning for Small-Scale Language Model Agents** [huggingface] — 70~500M SLM 에이전트 RL 정렬의 불안정 원인을 체계 분석 (new)
  https://huggingface.co/papers/2607.25091

### 코딩 에이전트
- **book-to-skill** [github_trending] — 기술서적 PDF를 Claude Code 스킬로 변환, 오늘 +423 스타 (new)
  https://github.com/virgiliojr94/book-to-skill
- **CodeNib: A Multi-View Data System for Serving Repository Context to Coding Agents** [huggingface] — 커밋 단위 재사용 인덱스로 코딩 에이전트의 반복 탐색 비용 절감 (new)
  https://huggingface.co/papers/2607.25431
- **Interview with Boris Cherny [video]** [hacker_news] — Claude Code 제작자 인터뷰, 코딩 에이전트 설계 배경 (new)
  https://www.youtube.com/watch?v=qyPCVqFUyDo
- **Scientific computing in the age of agentic AI** [release_blogs] — 유전체학 등 과학 코드 현대화에 코딩 에이전트를 쓴 현장 보고서 (new)
  https://openai.com/index/scientific-computing-agentic-ai

### 프롬프트·컨텍스트 엔지니어링
- **Visual prompt engineering for video models** [huggingface] — 비디오 파운데이션 모델에도 프롬프트 엔지니어링이 통하는지 검증 (new)
  https://huggingface.co/papers/2607.25537
- **OmniDelta: Skill-Driven Budget Allocation for Token Compression in OmniLLMs** [huggingface] — 옴니모달 LLM의 토큰 압축 예산을 스킬 단위로 동적 배분 (new)
  https://huggingface.co/papers/2607.25669

## 📌 Still trending (day 2+)
- **upstage/Solar-Open2-250B** [day 2] — 업스테이지 250B 오픈 모델, 다운로드 지속 상승
  https://huggingface.co/upstage/Solar-Open2-250B
- **poolside/Laguna-S-2.1** [day 2] — poolside 코드 특화 모델 최신판
  https://huggingface.co/poolside/Laguna-S-2.1
- **microsoft/Fara1.5-27B** [day 2] — MS 컴퓨터 유즈 계열 27B 모델
  https://huggingface.co/microsoft/Fara1.5-27B
- **thinkingmachines/Inkling** [day 2] — Thinking Machines 신규 공개 모델
  https://huggingface.co/thinkingmachines/Inkling
- **Kwaipilot/KAT-Coder-V2.5-Dev** [day 2] — 코딩 에이전트용 KAT-Coder 개발판
  https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev
- **andrewyng/aisuite** [day 2] — 멀티 LLM 공통 인터페이스 라이브러리
  https://github.com/andrewyng/aisuite
- **Codifying the Judge: Scalable Evaluation via Program Distillation** [day 2] — LLM 심사자를 프로그램으로 증류해 평가 확장
  https://huggingface.co/papers/2607.22561
- **The Physics of Multi-Turn Long-Horizon Planning** [day 2] — 멀티턴 장기 계획 능력의 사전·사후학습 분해
  https://huggingface.co/papers/2607.24720
- **From Proprietary to Open-Source: Multi-Agent Protocol Distillation** [day 2] — 상용 에이전트 프로토콜을 오픈모델로 증류
  https://huggingface.co/papers/2607.24280
- **JarvisHub: An Open Harness for Canvas-Native Multimodal Creative Agents** [day 2] — 캔버스 기반 창작 에이전트용 오픈 하네스
  https://huggingface.co/papers/2607.23588
- **Inviting hard questions** [day 2] — Anthropic이 대중에게 가장 어려운 AI 질문을 공모
  https://www.anthropic.com/news/hard-questions

## 💬 커뮤니티 동향 (DCInside 특이점갤)
- **속보) 구글 딥마인드 알파폴드 팀 사실상 해체** — 알파폴드 조직 개편설, 조회 3.4k로 갤 반응 큼
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1345303&exception_mode=recommend&page=1
- **OpenAI) 발전 속도 조절이 필요하다.** — OpenAI발 "감속" 발언이 갤 전체 논쟁을 촉발한 원문 글
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1344613&exception_mode=recommend&page=1
- **AI2027 시나리오는 현재까지 85% 정확하다** — AI2027 예측 시나리오의 현재 적중률 점검
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1345544&exception_mode=recommend&page=1
- **속보) 허깅페이스 오픈AI 내부모델 공격 타임라인 공개** — HF·OpenAI 평가 중 보안 사고 타임라인 정리
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1344710&exception_mode=recommend&page=1
- **알트만 : "앞으로 더 많은 주체성을 AI에게 넘기게 될것"** — 알트만의 에이전트 자율성 확대 발언 요약
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1345372&exception_mode=recommend&page=1

## ⚠️ 소스 상태
- github_trending: ok (12 items / 2 matched)
- hacker_news: ok (30 items / 3 matched)
- huggingface: ok (70 items / 19 matched)
- release_blogs: ok (60 items / 3 matched)
- anthropic_news: ok (13 items / 1 matched)
- dcinside: ok (30 items / 5 curated)
