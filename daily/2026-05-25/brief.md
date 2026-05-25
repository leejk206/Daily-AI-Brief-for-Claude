# 2026-05-25 AI 트렌드 브리프

## 🔥 오늘의 TOP 5

1. **Co-Scientist: 다중 에이전트 AI 연구 파트너** — Gemini 기반 multi-agent 연구 가속, 과학 발견 자동화 본격화
   sources: release_blogs
   https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate

2. **DeepSeek Reasonix** — 캐싱 최적화·저비용으로 튜닝된 DeepSeek 네이티브 코딩 에이전트
   sources: hacker_news
   https://esengine.github.io/DeepSeek-Reasonix/

3. **anthropics/claude-cookbooks** — Anthropic 공식 Claude 사용 레시피·노트북 모음, 실전 패턴 학습용
   sources: github_trending
   https://github.com/anthropics/claude-cookbooks

4. **Constraint Decay: 백엔드 코드 생성에서의 LLM 에이전트 취약성** — 제약 조건 누적 시 LLM 에이전트 성능 급락 정량 분석
   sources: hacker_news
   https://arxiv.org/abs/2605.06445

5. **garrytan/gstack** — Garry Tan의 23개 도구로 구성된 Claude Code 운영 템플릿 (CEO·Designer·PM 등 역할별)
   sources: github_trending
   https://github.com/garrytan/gstack

## 📋 카테고리별 나머지

### 에이전트 프레임워크
- **From Raw Experience to Skill Consumption** [huggingface] — 모델이 직접 생성·재사용하는 에이전트 스킬에 대한 체계적 연구 (new)
  https://huggingface.co/papers/2605.23899
- **SkillOpt: Self-Evolving Agent Skills** [huggingface] — 에이전트 스킬을 최적화하듯 학습하는 executive 전략 프레임워크 (new)
  https://huggingface.co/papers/2605.23904
- **HINT-SD: Long-Horizon Agents** [huggingface] — 긴 호라이즌 LLM 에이전트의 sparse reward 학습용 targeted hindsight self-distillation (new)
  https://huggingface.co/papers/2605.17873
- **PhotoFlow: Agentic 3D Virtual Photography** [huggingface] — 3D 씬에서 에이전트가 카메라 포즈를 추론·촬영하는 missions 프레임워크 (new)
  https://huggingface.co/papers/2605.23771
- **Efficient Agentic Reasoning Through Self-Regulated Simulative Planning** [huggingface] — 적응형 plan/act 토글로 에이전트 계산 효율 개선 (day 3)
  https://huggingface.co/papers/2605.22138
- **ClinSeekAgent** [huggingface] — 임상 의사결정용 멀티모달 증거 수집 에이전트 (day 2)
  https://huggingface.co/papers/2605.20176
- **Lean Refactor** [huggingface] — Lean 증명을 안전하게 refactor하는 retrieval-augmented agentic 시스템 (day 3)
  https://huggingface.co/papers/2605.20244
- **GenEvolve: Self-Evolving Image Generation Agents** [huggingface] — 도구 오케스트레이션으로 이미지 생성 능력을 진화시키는 에이전트 (day 2)
  https://huggingface.co/papers/2605.21605
- **One Sentence, One Drama** [huggingface] — 멀티에이전트로 짧은 드라마 영상 생성, 스크립트·연출 분업 (day 2)
  https://huggingface.co/papers/2605.22144

### LLM 하네스·평가
- **VGenST-Bench** [huggingface] — 능동적 비디오 합성을 통한 시공간 추론 벤치마크 (new)
  https://huggingface.co/papers/2605.22570
- **LLMs as Noisy Channels: Shannon 관점의 스케일링 법칙** [huggingface] — 단조 power law 한계를 노이즈 채널 관점으로 재정식화 (new)
  https://huggingface.co/papers/2605.23901
- **Rule2DRC** [huggingface] — LLM 에이전트의 DRC 스크립트 합성 능력을 실행 기반으로 평가 (day 2)
  https://huggingface.co/papers/2605.15669
- **OmniPro** [huggingface] — omni-modal 스트리밍 비디오 이해 능력 벤치마크 (day 2)
  https://huggingface.co/papers/2605.18577
- **SpaceDG** [huggingface] — 시각 손상 조건에서 MLLM의 공간 지능을 평가하는 벤치마크 (day 2)
  https://huggingface.co/papers/2605.22536
- **Forecasting Downstream Performance of LLMs With Proxy Metrics** [huggingface] — 사전학습 단계에서 다운스트림 성능을 예측하는 proxy 지표 연구 (day 3)
  https://huggingface.co/papers/2605.18607

### 코딩 에이전트
- **affaan-m/ECC** [github_trending] — Skills·instincts·memory·security를 통합한 에이전트 하네스 최적화 시스템 (new)
  https://github.com/affaan-m/ECC
- **How business operations teams use Codex** [release_blogs] — OpenAI Codex의 비기술 부서 활용 가이드, initiative brief·전략 업데이트 사례 (new)
  https://openai.com/academy/codex-for-work/how-business-operations-teams-use-code

### 프롬프트·컨텍스트 엔지니어링
- **Full Attention Strikes Back** [huggingface] — full attention을 100 step 학습만으로 sparse로 전이, long-context 추론 비용 절감 (new)
  https://huggingface.co/papers/2605.16928

## 📌 Still trending (day 2+)
- **Lum1104/Understand-Anything** [day 4] — 코드 지식 그래프, Claude Code·Codex·Cursor 호환
  https://github.com/Lum1104/Understand-Anything
- **Efficient Agentic Reasoning** [day 3] — 자기조절 시뮬레이션 기반 에이전트 계획
  https://huggingface.co/papers/2605.22138
- **Lean Refactor** [day 3] — Lean 증명 agentic refactor
  https://huggingface.co/papers/2605.20244
- **Forecasting Downstream Performance** [day 3] — LLM 사전학습 단계 성능 예측
  https://huggingface.co/papers/2605.18607
- **ClinSeekAgent** [day 2] — 임상 multimodal 증거 수집 에이전트
  https://huggingface.co/papers/2605.20176
- **One Sentence, One Drama** [day 2] — 멀티에이전트 드라마 생성
  https://huggingface.co/papers/2605.22144
- **GenEvolve** [day 2] — 자기진화형 이미지 생성 에이전트
  https://huggingface.co/papers/2605.21605
- **Rule2DRC** [day 2] — LLM 에이전트 DRC 스크립트 합성 벤치
  https://huggingface.co/papers/2605.15669
- **OmniPro** [day 2] — omni-modal 스트리밍 비디오 벤치
  https://huggingface.co/papers/2605.18577
- **SpaceDG** [day 2] — 시각 손상 공간 지능 벤치
  https://huggingface.co/papers/2605.22536

## ⚠️ 소스 상태
- github_trending: ok (17 items / 4 matched)
- hacker_news: ok (30 items / 2 matched)
- huggingface: ok (70 items / 16 matched)
- release_blogs: ok (40 items / 2 matched)
