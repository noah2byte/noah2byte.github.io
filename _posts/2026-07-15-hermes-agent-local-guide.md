---
title: "Hermes Agent 설치 및 로컬 모델 한계 정리"
date: 2026-07-15 14:00:00 +0900
categories: [운영 이모저모, LLM]
pin: true
math: true
mermaid: true
---

# Hermes Agent 무료(Zero-Cost) PoC 가이드 — 설치·세팅 전 과정과 제약 사항

> 작성일: 2026-07-16 · 환경: Windows 11 (네이티브), Hermes Agent v0.18.2 (2026.7.7.2), Ollama(127.0.0.1:11434)
> 목적: **API 키·구독 없이, 비용이 전혀 발생하지 않는 구성**으로 Hermes Agent를 설치·세팅하고 검증할 때 참조할 수 있는 실전 기록. 실제 진행 과정에서 겪은 실패와 그 원인, 그리고 무료 구성의 구조적 제약을 함께 정리한다.
> 작성 원칙: 모든 선택 지점에 "무엇을 골랐는가"와 함께 **"왜 골랐는가"를 병기**한다. 이 문서를 보고 재현하는 사람의 환경(하드웨어, 목적)이 다를 수 있으므로, 선택의 결과가 아니라 판단 기준을 전달하는 것이 목표다.

---

## 배경 — 왜 이 PoC를 시작했는가

이 절을 문서 맨 앞에 두는 사유: 뒤에 나오는 모든 선택(무료만 고집한 것, Full setup을 고른 것, 로컬 Ollama를 고집한 것)이 전부 이 배경 하나에서 나왔기 때문이다. 배경 없이 3~5장을 읽으면 "그냥 유료 쓰면 되는데 왜 이렇게까지 하나"로 보이지만, 실제로는 세 가지 제약이 동시에 걸려 있었다.

1. **비용 지원의 부재.** 회사 차원에서 LLM 구독이나 API 비용을 지원받을 수 있는 상황이 아니었다. PoC 단계에서 사비로 API 과금을 감수하기는 부담스러웠고, 그래서 "일단 무료로 얼마나 되는지" 확인하는 것이 첫 단계여야 했다.
2. **기밀 정보 우려.** DevOps 업무의 특성상 인프라 구성, 로그, 설정 파일 등에 사내 기밀 정보가 섞여 들어갈 가능성이 있다. 외부 API(Claude, GPT 등)로 이런 데이터가 나가는 것에 대한 우려가 있어, 최대한 로컬에서 완결되는 구성을 먼저 검증하고 싶었다.
3. **1인 데브옵스의 구조적 과부하.** 인프라 운영을 포함한 업무를 혼자 커버하는 상황에서, 반복 작업을 에이전트에게 위임할 수 있다면 실질적인 여유를 만들 수 있다는 기대가 있었다. Hermes Agent가 매력적이었던 이유도 여기 있다 — 터미널·파일·검색을 아우르는 자율 에이전트라면 온콜 대응, 로그 조사, 반복 설정 작업 같은 것을 상당 부분 맡길 수 있어 보였기 때문이다.

이 세 조건을 한 문장으로 합치면 "비용 없이, 기밀이 새지 않게, 로컬에서 완결되는 DevOps 자동화 에이전트"였다. 이 문서는 그 가설을 실제로 검증한 기록이고, 결론(7장 및 5.4절)은 이 가설이 현재 하드웨어 조건에서는 성립하지 않는다는 것이다.

---

## 1. 기초 개념 — Hermes를 이해하기 위한 최소 지식 (공식 문서 기반)

이 장을 앞에 두는 사유: 뒤에서 다룰 세팅 선택과 실패 분석은 전부 "에이전트란 무엇이고 툴 콜링이 어떻게 도는가"를 전제로 한다. 이 전제 없이 3~5장을 읽으면 "왜 모델을 바꾸라는 건지"가 와닿지 않기 때문에, 개념부터 쌓는다.

### 1.1 AI 에이전트란 — 챗봇과 무엇이 다른가

일반적인 챗봇(LLM 채팅)은 "질문 → 텍스트 답변"으로 끝난다. 모델이 할 수 있는 일은 오직 글쓰기다. 반면 **AI 에이전트는 모델에게 '행동 수단(툴)'을 쥐여주고, 목표가 달성될 때까지 스스로 [판단 → 행동 → 결과 확인]을 반복하게 만든 시스템**이다. "README를 요약해줘"라는 요청에 챗봇은 "파일 내용을 붙여넣어 주세요"라고 답하지만, 에이전트는 직접 파일을 읽고 요약한다.

Hermes Agent는 이 범주의 오픈소스(MIT) 구현체로, Nous Research가 2026년 2월 공개했다. 공식 문서 스스로 Claude Code(Anthropic), Codex(OpenAI), OpenClaw와 같은 부류 — 툴 콜링으로 시스템과 상호작용하는 자율 에이전트 — 로 분류한다.

### 1.2 툴 콜링 — 에이전트의 손과 발

에이전트를 처음 접할 때 가장 흔한 오해가 "모델이 명령을 실행한다"는 것이다. **모델은 아무것도 직접 실행하지 않는다.** 실제 동작은 이렇다:

![툴 콜링의 기본 원리](/assets/img/posts/tool-calling-basics.svg)

1. 프레임워크가 모델에게 "너는 이런 함수들을 부를 수 있다"는 **툴 스키마**(함수 이름·파라미터 명세) 목록을 대화에 함께 실어 보낸다.
2. 모델은 필요하다고 판단하면 답변 대신 **"이 함수를 이 인자로 불러달라"는 JSON 텍스트**를 출력한다 — 이것이 툴 콜(tool call)이며, 어디까지나 요청서다.
3. **실행은 프레임워크(Hermes)가 한다.** 셸 명령, API 호출, 파일 IO 등.
4. 실행 결과가 `tool` role의 메시지로 대화 이력에 주입된다.
5. 모델이 그 결과를 읽고 다음 행동(추가 툴 콜 또는 최종 답변)을 결정한다.

이 구분이 중요한 사유: 이번 PoC의 실패가 정확히 **④→⑤ 사이**에서 났기 때문이다. 모델이 ②(요청서 쓰기)는 형식상 해내면서도 ④로 돌아온 결과를 소화하지 못하는 경우가 존재하며(4장), "툴 지원"이라는 한 단어로는 이 차이가 드러나지 않는다.

### 1.3 에이전트 루프 — 한 턴이 실제로 하는 일

사용자의 메시지 하나에 대해 Hermes는 아래 루프를 최대 150회(기본값) 반복한다:

![에이전트 루프](/assets/img/posts/agent-loop.svg)

주목할 것은 ① 컨텍스트 조립 단계의 무게다. 시스템 프롬프트(SOUL.md), 툴 스키마 약 30종, 관련 스킬 문서, 메모리, 작업 디렉터리의 AGENTS.md, 대화 이력이 **매 바퀴마다** 모델에게 통째로 전달된다. 이번 환경에서는 대화 시작 직후 이미 약 1.2만 토큰이었다. 즉 에이전트의 성능 하한을 결정하는 것은 프레임워크가 아니라 **이 무거운 컨텍스트를 소화하며 판단을 150회 유지할 수 있는 모델의 추론력**이다 — 5장 결론의 복선이 여기에 있다.

### 1.4 Hermes의 구성 요소 — 용어 정리

뒤에서 계속 등장할 개념들이다. 공식 문서 기준으로 정리한다.

| 구성 요소 | 역할 | 비유 |
|---|---|---|
| **LLM 프로바이더** | 추론을 담당하는 모델 연결. Nous Portal(300+ 모델), Anthropic, OpenAI, OpenRouter, 로컬 Ollama/vLLM 등 20+ 중 교체 가능. 내부 트랜스포트 계층이 프로바이더별 메시지·툴 포맷 차이를 흡수 | 두뇌 (갈아끼울 수 있음) |
| **툴(Tool)** | 에이전트의 행동 수단 약 30종 — terminal, file(read/write/patch), execute_code, web_search, browser, vision, TTS, cron, delegate_task 등 | 손과 발 |
| **터미널 백엔드** | 셸 명령이 *어디서* 실행되는가: local, Docker, SSH, Modal, Daytona, Singularity 6종. 격리 수준을 결정 | 작업장 |
| **스킬(Skill)** | 절차 지식을 담은 마크다운 문서. Hermes의 차별점 — 복잡한 작업(대략 5회 이상 툴 콜)을 끝내면 **스스로 스킬을 작성**하고, 사용 중 낡은 스킬을 패치하며, `hermes curator`가 주기적으로 검토·통합·아카이브. agentskills.io 표준 호환 | 업무 매뉴얼 (스스로 씀) |
| **메모리** | 사용자·환경에 대한 지식을 세션을 넘어 축적. FTS5 과거 세션 전문 검색, 외부 프로바이더(Honcho, Mem0 등) 연동 | 장기 기억 |
| **세션** | 대화 단위. SQLite 저장, `hermes --resume <id>`로 이어서 진행 | 회의록 |
| **게이트웨이** | Telegram·Discord·Slack 등 20+ 메시징 플랫폼 연결. 어디서 대화해도 같은 코어·같은 기억 | 창구 |
| **AGENTS.md / SOUL.md** | AGENTS.md는 작업 디렉터리의 프로젝트 컨텍스트로 자동 주입되는 파일, SOUL.md는 에이전트 정체성(시스템 프롬프트 최상단) | 업무 지시서 / 자기소개서 |

### 1.5 전체 아키텍처

위 요소들의 관계를 한 장으로 보면:

![Hermes 전체 아키텍처](/assets/img/posts/hermes-architecture.svg)

핵심은 **모든 인터페이스가 단일 AIAgent 코어(run_agent.py)를 공유**한다는 점이다. CLI에서 시작한 대화를 Telegram에서 이어받아도 같은 세션·스킬·메모리 위에서 동작하는 것이 이 구조 덕분이며, 크론 작업과 서브에이전트도 같은 코어를 쓴다.

그 밖의 부가 기능: 파일 변경 전 자동 체크포인트(`/rollback`으로 복원), 배치 처리·트래젝토리 내보내기(SFT/RL 학습 데이터 생성), MCP 서버 연동.

> 팁: 공식 문서는 LLM 친화적 진입점으로 `/llms.txt`(~17KB 색인)와 `/llms-full.txt`(~1.8MB 전체 문서)를 제공한다. 문서를 파볼 때 이 파일을 LLM에 넣고 질문하는 방식이 효율적이다.

---

## 2. 사전 준비물 (무료 PoC 기준)

| 항목 | 내용 | 비용 |
|---|---|---|
| OS | Windows 10/11 네이티브 지원 (WSL 불필요). 설치기가 uv, Python 3.11, Node.js, ripgrep, ffmpeg, 포터블 Git Bash(MinGit)까지 자동 설치 | 무료 |
| Ollama | 로컬 LLM 서버. `http://127.0.0.1:11434/v1` 로 OpenAI 호환 API 제공 | 무료 |
| 로컬 모델 | **반드시 `tools` capability가 있는 모델**이어야 함 (아래 2.2 참조) | 무료 |
| API 키 | 불필요 (이 가이드의 전제) | ₩0 |

### 2.1 설치 — 인스톨러가 실제로 하는 일 (실측 기록)

Windows PowerShell에서 한 줄이면 된다 (Linux/macOS/WSL2는 `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`):

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

실제 실행 시 인스톨러가 수행한 작업을 순서대로 기록한다 — 무엇이 어디에 깔리는지 알아야 나중에 문제가 생겼을 때 어느 계층을 의심할지 판단할 수 있기 때문이다:

1. **의존성 자동 확보** — 관리형 uv(0.11.29)를 `hermes\bin`에 설치, Python 3.11·Git·Node.js는 기존 설치를 감지해 재사용(Git은 `HERMES_GIT_BASH_PATH`로 등록), ripgrep·ffmpeg는 winget으로 설치. 사용자가 미리 준비할 것이 사실상 없다.
2. **리포 클론 — SSH 실패 시 HTTPS 자동 폴백.** 실제로 SSH 클론이 포트 22 차단으로 실패했는데(`ssh: connect to host github.com port 22: Connection refused`) 인스톨러가 즉시 HTTPS로 전환해 성공했다. 사내망 등 22번 포트가 막힌 환경에서도 설치가 끊기지 않는다는 뜻이다.
3. **venv 생성 + 의존성 99종 설치** — `uv.lock` 기반 **해시 검증(hash-verified)** 설치. 공급망 관점에서 잠긴 버전만 들어온다는 점은 평가할 만하다.
4. **PowerShell 실행 정책 우회** — `npm.ps1`이 실행 정책에 막히자 `npm.cmd`로 자동 전환. Windows 특유의 걸림돌을 인스톨러가 알아서 피해 갔다.
5. **Playwright Chromium 다운로드 (~300MB)** — Chrome for Testing 183.6MiB + Headless Shell 113.6MiB + ffmpeg + winldd. **설치 시간과 디스크의 대부분이 여기서 소모**되므로, 브라우저 자동화를 안 쓸 계획이면 이 단계가 아깝게 느껴질 수 있다 (설치 후 툴에서 끄는 것은 가능).
6. **설정 템플릿 생성** — `.env`, `config.yaml`, 그리고 에이전트 정체성 파일 `SOUL.md`(1.4절)가 템플릿으로 생성된다.
7. **번들 스킬 73종 동기화** — `hermes\skills\`에 github, mlops, productivity 등 카테고리별 스킬이 설치된다.
8. **설치 직후 셋업 위저드 자동 실행** — 별도로 `hermes setup`을 칠 필요 없이 3장의 위저드로 바로 이어진다. 마지막에 PATH 반영을 위해 **터미널 재시작**이 필요하다.

#### 디렉터리 구조 — 무엇이 어디에 생기는가

설치가 끝나면 모든 것이 `%LOCALAPPDATA%\hermes\` 한 폴더 아래에 모인다 (환경변수 `HERMES_HOME`으로 등록됨). 단일 폴더 구조인 것 자체가 장점이다 — 백업은 이 폴더 하나를 복사하면 되고, 완전 제거도 이 폴더를 지우면 거의 끝나기 때문이다.

```
C:\Users\<user>\AppData\Local\hermes\      ← HERMES_HOME (전부 여기에)
│
│  ── 설정 (사용자가 직접 만지는 파일) ──
├── config.yaml                # 모든 설정: 모델·프로바이더·툴·백엔드·압축 등
├── config.yaml.bak.<타임스탬프> # 위저드 실행 때마다 자동 백업된 이전 설정
├── .env                       # 시크릿(API 키) 전용 — 무료 PoC에서는 빈 파일
├── SOUL.md                    # 에이전트 정체성/성격 (시스템 프롬프트 최상단)
│
│  ── 데이터 (에이전트가 쌓는 것) ──
├── sessions\                  # 대화 기록 (SQLite, FTS5 검색 대상)
├── skills\                    # 번들 스킬 73종 + 에이전트가 자가생성한 스킬
├── cron\                      # 예약 작업 정의
├── logs\                      # 실행 로그
│
│  ── 실행체 (건드릴 일 없음) ──
├── bin\                       # 관리형 uv
└── hermes-agent\              # 리포 소스 + venv
    ├── venv\Scripts\          # PATH에 등록됨 — 'hermes' 명령의 실체
    └── .hermes-bootstrap-complete  # 설치 완료 마커

── HERMES_HOME 밖에 생기는 것 (제거 시 따로 지워야 함) ──
C:\Users\<user>\AppData\Local\ms-playwright\        # Chromium 등 브라우저 (~300MB)
C:\Users\<user>\AppData\Local\Programs\Cua\         # cua-driver (설치 성공 시)
```

설정(`config.yaml`)과 시크릿(`.env`)이 분리된 사유도 알아둘 만하다: config는 백업·공유·버전관리해도 되는 파일이고, .env는 절대 공유하면 안 되는 파일이라 처음부터 갈라놓은 설계다. 자동 백업(`config.yaml.bak.*`)이 config에만 만들어지는 것도 같은 이유다.

#### 상황별 참조 가이드 — 언제 어떤 파일을 보는가

| 상황 | 참조/수정 대상 | 방법 |
|---|---|---|
| 현재 설정이 어떻게 되어 있는지 확인 | `config.yaml` | `hermes config` (읽기 전용 요약) |
| 모델·툴·백엔드 등 설정 변경 | `config.yaml` | `hermes config edit` 또는 `hermes setup model/tools/terminal` — 직접 편집도 가능 |
| API 키를 추가해야 할 때 | `.env` | 직접 편집 (예: `OPENROUTER_API_KEY=...`) 후 재시작 |
| 에이전트 말투·정체성 바꾸기 | `SOUL.md` | 직접 편집 — 시스템 프롬프트 최상단에 들어가므로 즉시 반영 |
| 위저드 재실행 후 설정이 꼬였을 때 | `config.yaml.bak.<타임스탬프>` | 해당 백업을 `config.yaml`로 복사해 복원 |
| 지난 대화를 이어가고 싶을 때 | `sessions\` | 종료 화면의 세션 ID로 `hermes --resume <id>` |
| 오류·이상 동작의 원인 추적 | `logs\` | 로그 확인 → 그래도 불명이면 `hermes doctor` |
| 에이전트가 만든 스킬 열람, 직접 스킬 작성 | `skills\` | 마크다운 문서라 에디터로 바로 열람·수정 가능 |
| 예약 작업 확인·관리 | `cron\` | 파일 직접보다 `hermes cron list/create/pause` 권장 |
| 프레임워크 내부 코드를 파보고 싶을 때 | `hermes-agent\` | 에이전트 코어는 `run_agent.py`에서 시작 |
| 디스크 정리 — 큰 덩어리부터 | `ms-playwright\`, `hermes-agent\venv\` | 브라우저 자동화를 안 쓰면 ms-playwright가 최대 회수 지점 |

이 표를 넣는 사유: PoC 중 문제가 생겼을 때 초심자가 가장 오래 헤매는 지점이 "어느 파일을 봐야 하는지 모르는 것"이기 때문이다. 이번 세팅에서도 실제로 config.yaml 확인(3.7절 ①), 백업 복원 경로 안내, 세션 resume ID 안내가 각각 다른 화면에 흩어져 나왔다 — 그것을 한 표로 모은 것이다.

### 2.2 ⚠ 가장 중요한 사전 확인: 모델의 tools 지원

Hermes는 매 요청에 30여 개의 툴 스키마를 함께 전송하는 에이전트다. **모델이 툴 콜링을 지원하지 않으면 첫 대화조차 시작되지 않는다.** 반드시 세팅 전에 확인할 것:

```bash
ollama show <모델명>
# Capabilities에 "tools"가 있어야 함 (completion만 있으면 사용 불가)
```

실제로 이번 환경의 로컬 모델 4종을 전부 확인한 결과다 (Ollama 0.32.0):

| 모델 | 파라미터 | 컨텍스트 | Capabilities | 관문① 판정 |
|---|---|---|---|---|
| gemma3:latest | 4.3B (Q4_K_M) | 131K | completion, vision | **✗ tools 없음** — HTTP 400의 원인 |
| llama3:latest | 8.0B (Q4_0) | 8K | completion | **✗ tools 없음** — 파라미터가 커도 소용없음 |
| gemma:2b | 1.7GB급 | — | — | ✗ (확인할 것도 없는 크기) |
| gemma4:e2b | 5.1B (Q4_K_M) | 131K | completion, vision, audio, **tools, thinking** | △ 유일하게 통과 |

이 표에서 읽어야 할 것 두 가지. 첫째, **당시 gemma4:e2b 선택은 '선택'이 아니라 강제였다** — 로컬 4종 중 tools가 표기된 모델이 그것뿐이었다. 둘째, tools 여부는 **파라미터 크기와 무관하다** — 8B인 llama3에는 없고 5.1B인 gemma4:e2b에는 있다. capability는 모델 크기가 아니라 해당 빌드의 채팅 템플릿에 달린 문제이기 때문이다. 그리고 뒤(4.1절)에서 확인되지만, gemma4:e2b는 `tools`에 `thinking`까지 표기되어 있었음에도 실제 툴 결과 소화에는 실패한다 — **이 표의 capabilities는 '형식 지원' 선언일 뿐, 에이전트로 동작함을 보장하지 않는다.**

첫 시도에서 `gemma3:latest`로 세팅했다가 다음 오류로 즉시 실패했다:

```
BadRequestError [HTTP 400]
registry.ollama.ai/library/gemma3:latest does not support tools
❌ Non-retryable client error (HTTP 400). Aborting.
```

재시도로 해결되지 않는 오류로 정확히 분류되어 중단됐고, 결국 `hermes setup`을 처음부터 다시 돌려 모델을 교체해야 했다. 오류 리포팅 자체는 훌륭하다 — 프로바이더·엔드포인트·컨텍스트 토큰 수·소요 시간까지 표기해 원인 파악이 즉각적이었다.

---

## 3. 세팅 전 과정 상세 (`hermes setup` 위저드 단계별)

아래는 실제 위저드를 진행한 순서 그대로다. 각 단계에서 **무료 PoC라면 무엇을 골라야 하는지**와 그 이유를 함께 적는다. 먼저 이 장을 다 따라 하면 완성되는 목표 구성을 그림으로 보면:

![무료 PoC 목표 구성](/assets/img/posts/free-poc-stack.svg)

전부 로컬 또는 무료 외부 호출로 구성되며(청록), 대신 적색 영역의 기능은 이 구성에 존재하지 않는다 — 무엇을 얻고 무엇을 포기하는 선택인지 시작 전에 알고 진행하기 위함이다.

### 3.1 셋업 방식 선택

```
(●) 1. Quick Setup (Nous Portal) — free OAuth login, no API keys (recommended)
(○) 2. Full setup — configure every provider, tool & option yourself
(○) 3. Blank Slate — everything off except the bare minimum
```

**→ 2번 Full setup 선택.** 기본값이자 "recommended"인 Quick Setup은 Nous Portal OAuth 로그인 경로다. 로그인 자체는 무료지만 모델·툴 게이트웨이가 구독 과금 체계에 연결되는 경로이므로, "완전 무료·로컬 완결" PoC가 목적이라면 Full setup으로 모든 것을 직접 지정하는 편이 통제하기 좋다. 위저드 곳곳에서 "추천" 경로가 Nous Portal 구독으로 수렴하도록 설계되어 있다는 점은 인지하고 진행할 것.

### 3.2 Inference Provider (모델 연결)

프로바이더 선택 화면에는 무려 39개 선택지가 나온다 (Nous Portal, OpenRouter, Anthropic, OpenAI, AWS Bedrock, Azure, DeepSeek, ... , custom, Custom endpoint). 이미 Ollama를 한 번 연결해 두었다면 목록에 이렇게 표시된다:

```
(●) 35. Local Ollama Gemma3 (127.0.0.1:11434/v1) — gemma3:latest  ← currently active
```

**→ 처음이라면 `Custom endpoint`(수동 URL 입력) 선택.** 최초 세팅 시의 실제 흐름은 이랬다:

```
API base URL: http://127.0.0.1:11434/v1
API key [optional]:                          # 비워둠 — Ollama는 키 불필요
Verified endpoint via .../v1/models (4 model(s) visible)   # 입력 즉시 접속 검증

Select API compatibility mode:
  1. Auto-detect [current]   ← 선택
  2. Chat Completions / 3. Responses·Codex / 4. Anthropic Messages
Context length: (blank = auto-detect)
Display name: Local Ollama Gemma3            # 저장될 프로바이더 이름
💾 Saved to custom providers as "Local Ollama Gemma3"
```

주목할 점 두 가지. 첫째, URL을 입력하는 즉시 `/v1/models`를 호출해 **엔드포인트 생존 여부를 검증**해 준다 — Ollama가 안 떠 있으면 여기서 바로 걸러진다. 둘째, API 호환 모드는 **Auto-detect를 선택**했는데, 사유는 Ollama가 표준 OpenAI 호환(`/chat/completions`) 서버라 휴리스틱 감지로 충분하고, Anthropic Messages 등 다른 모드는 해당 형식 전용 백엔드용이기 때문이다. 이렇게 등록하면 custom provider로 저장되어, 이후 재세팅 시에는 목록에 이렇게 나타난다:

```
(●) 35. Local Ollama Gemma3 (127.0.0.1:11434/v1) — gemma3:latest  ← currently active
```

한 가지 혼동 주의: 프로바이더 미설정 상태의 첫 위저드 화면에는 `Current model: anthropic/claude-opus-4.6 / Active provider: none`이라고 표시된다. 이는 연결된 모델이 아니라 **config 템플릿의 기본 표시값**일 뿐이다 — Claude가 무료로 붙어 있다는 뜻이 아니므로 오해하지 말 것.

선택하면 위저드가 **Ollama에서 설치된 모델 목록을 자동으로 fetch**해 보여준다:

```
Fetching available models...
Found 4 model(s):
(●) 1. gemma3:latest (current)
(○) 2. gemma:2b
(○) 3. gemma4:e2b
(○) 4. llama3:latest
```

**타임라인 주의:** 최초 세팅에서는 이 목록에서 `gemma3:latest`를 골랐고, 그 결과가 2.2절의 HTTP 400 즉사였다. 이후 `hermes setup`을 다시 돌려 tools capability가 확인된 `gemma4:e2b`로 교체했다 — 즉 이 화면을 두 번 지나갔다. 처음부터 2.2절의 확인을 거쳤다면 한 번으로 끝났을 일이다.

```
✅ Model set to: gemma4:e2b
   Provider: Local Ollama Gemma3 (http://127.0.0.1:11434/v1)
```

### 3.3 Terminal Backend (셸 실행 위치)

```
(○) 1. Local - run directly on this machine (default)
(○) 2. Docker - isolated container
(○) 3. Modal / 4. SSH / 5. Daytona
(●) 6. Keep current (local)
```

**→ local 유지 (무료).** 단, 이건 편의를 위한 선택이지 안전한 선택이 아니다. local 백엔드는 에이전트가 **내 사용자 계정 권한으로 임의 셸 명령을 직접 실행**한다는 뜻이다. Docker 백엔드도 무료이므로, 검증이 끝나고 본격적으로 굴릴 계획이라면 Docker 격리를 강력 권장한다 (6장 참조).

이후 권장 기본값이 자동 적용된다: Max iterations 150 / Tool progress all / Compression threshold 0.50 / Session reset never.

### 3.4 Messaging Platforms

Telegram, Discord, Slack, WhatsApp, Signal 등 25개 플랫폼 연동 화면. **→ 전부 스킵.** CLI만으로 PoC에 충분하며, 나중에 `hermes setup gateway`로 언제든 추가할 수 있다.

### 3.5 Tool Configuration (툴별 프로바이더 선택) — 무료 PoC의 핵심 구간

CLI용 툴 토글 화면에서 기본 활성 항목(웹 검색, 브라우저, 터미널, 파일, 코드 실행, 비전, 이미지 생성, TTS, 스킬, 메모리, 크론 등)을 확인한 뒤, 프로바이더가 필요한 6개 툴에 대해 개별 선택이 이어진다. **각 화면마다 무료/유료, 로컬/클라우드, 키 필요 여부가 명시**되어 있어 판단이 쉽다.

| 툴 | 무료 PoC 선택 | 이유 / 비고 |
|---|---|---|
| 🌐 Browser Automation | **1. Local Browser** (headless Chromium) | 무료, 키 불필요. "Chromium browser already installed" 확인됨. 유료 대안: Browserbase, Firecrawl 등 |
| 🖱️ Computer Use | cua-driver (백그라운드, 무료) | 커서/포커스를 뺏지 않는 백그라운드 방식. **단, 실제로는 설치가 실패했다** — 아래 참고 |
| 🎨 Image Generation | **10. Skip** | 무료 옵션이 없다. FAL/OpenAI 키 또는 Nous 구독 필요. 무료 PoC에서는 포기해야 하는 기능 |
| 🔊 Text-to-Speech | **1. Microsoft Edge TTS** | 무료, 키 불필요, 품질 준수. 완전 로컬을 원하면 KittenTTS(~25MB)나 Piper(44개 언어)도 무료 |
| 🔍 Web Search | **4. DuckDuckGo (ddgs)** | 무료, 키 불필요. **단 search-only** — 페이지 본문 추출(web_extract)은 안 됨 (6장 제약 참조) |

> ⚠ cua-driver 설치 실패 사례: 위저드가 GitHub 릴리스에서 바이너리를 받다가 실패했는데(`cua-driver installing did not complete. Re-run manually: ...`), 곧바로 `✓ cua-driver (background) - no configuration needed!` 라는 성공처럼 보이는 메시지가 출력됐다. **이 실패는 1차 세팅과 재세팅에서 완전히 동일하게 재현됐다** — 일시적 네트워크 문제가 아니라 Windows 설치 스크립트 자체의 문제로 보인다는 뜻이다. **위저드의 ✓ 표시를 믿지 말고 실제 설치 여부를 확인할 것.** 재설치 명령은 안내문에 나온다:
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.ps1 | iex"
> ```

설정 완료 시 기존 config가 자동 백업된다 (`config.yaml.bak.<타임스탬프>`) — 잘못 건드려도 복원 가능.

### 3.6 셋업 완료 후 상태

```
◆ Tool Availability Summary — 5/9 tool categories available:
 ✓ Vision / ✓ Text-to-Speech (Edge TTS) / ✓ Terminal / ✓ Task Planning / ✓ Skills
 ✗ Web Search & Extract  (extract 프로바이더 키 없음)
 ✗ Browser Automation    (missing npm install -g agent-browser ...)
 ✗ Image Generation      (FAL_KEY or OPENAI_API_KEY 없음)
 ✗ Skills Hub (GitHub)   (GITHUB_TOKEN 없음)
```

여기서 모순 하나: 셋업 중에 Local Browser를 선택하고 Chromium 설치까지 확인됐는데, 최종 요약에는 Browser Automation이 `agent-browser missing`으로 비활성 표기됐다. 로컬 Chromium 경로와 agent-browser 경로가 별개로 체크되는 것으로 보인다. `hermes doctor`로 실상을 확인해야 한다.

### 3.7 세팅 검증 절차

각 단계는 서로 다른 계층을 검증한다 — 어느 계층에서 어긋났는지 특정하기 위해 순서대로 진행한다.

1. `hermes config` — `Model: {'default': 'gemma4:e2b', 'provider': 'custom', 'base_url': 'http://127.0.0.1:11434/v1'}` 확인. **사유: 위저드의 "✅ Model set" 메시지와 실제 config.yaml 반영이 다를 수 있으므로**(이번 세팅에서 cua-driver가 실패했는데 ✓로 표시된 전례), 설정 파일 계층을 먼저 확정한다.
2. `ollama show gemma4:e2b` — capabilities에 tools 포함 확인. **사유: Hermes 설정이 맞아도 모델 계층이 툴을 거부하면 HTTP 400으로 즉사하기 때문** (gemma3 사례).
3. `hermes` 실행 — 시작 배너 좌하단의 모델명이 교체한 모델로 표시되는지 확인 (`gemma4:e2b · Nous Research`). **사유: 런타임이 config를 실제로 읽어들였는지는 실행해야만 확인되므로.**
4. `hermes doctor` — 툴 상태 점검. **사유: 셋업 요약(5/9)과 실제 가용 상태가 불일치하는 사례(Browser Automation)가 있었기 때문.**

시작 배너에서는 사용 가능한 툴(browser, clarify, code_execution, computer_use, cronjob, delegation, file, image_gen 외 9개 툴셋)과 번들 스킬 63종(github, mlops, productivity, research 등 카테고리별)이 표시된다 — 프레임워크가 무엇을 갖추고 있는지 한눈에 볼 수 있는 화면이다.

### 3.8 기능 검증 시나리오 (단계별 난이도 순)

세팅이 끝나면 아래 순서로 테스트하는 것을 권한다. 단순 응답 → 툴 1회 → 툴 결과 통합 순으로 난이도가 올라간다.

1. 일반 대화: "현재 어떤 모델을 사용 중이야?"
2. 터미널 실행: "현재 디렉터리의 파일 목록을 보여줘."
3. 파일 읽기: "README.md를 읽어서 요약해줘."
4. 웹 검색: "Kubernetes 1.35 변경사항을 검색해줘."
5. 브라우저 자동화: "https://kubernetes.io 를 열고 Release Notes 페이지로 이동해줘."
6. 코드 분석: "이 프로젝트를 분석해서 개선점을 알려줘."

---

## 4. 실제 검증 결과 — 무료 로컬 소형 모델의 실패 양상

`gemma4:e2b`로 위 시나리오를 실행한 결과다. 400 오류는 사라졌지만, 에이전트로서는 전 항목 실패했다.

| 테스트 | 기대 동작 | 실제 동작 |
|---|---|---|
| 모델 자기소개 | Hermes 시스템 프롬프트 기반 응답 | "저는 Google에서 훈련한 대규모 언어 모델입니다" — 시스템 프롬프트 무시, 사전학습 정체성으로 회귀 |
| 파일 목록 | terminal 툴 호출 | 툴 미호출, "어느 디렉터리인지 알려달라"고 반문 |
| README 요약 | read_file 툴 호출 | 툴 미호출, 경로를 되물음 |
| K8s 1.35 검색 | 검색 → 결과 요약 | **web_search는 실행됐으나(5.0s)** 결과를 완전히 무시하고 "명령을 아직 주지 않았다"고 응답 |
| 브라우저 이동 | 브라우저 툴 사용 | web_extract 시도 → search-only 백엔드라 실패 → 무관한 응답 |

핵심 관찰: 검색 테스트에서 **파이프라인(툴 스키마 전달 → 툴 실행 → 결과 주입)은 프레임워크 차원에서 정상 동작했다.** 무너진 것은 모델이다 — 그림 2로 보면 ①~④는 돌았고 **④→⑤ 구간에서 끊긴 것**이다. 툴 콜링 "지원 여부"(스키마를 받아 형식에 맞는 호출을 뱉는 능력)와 "에이전틱 역량"(멀티턴 루프에서 툴 결과를 해석하고 다음 행동을 결정하는 능력)은 전혀 다른 문제이며, 소형 모델은 전자를 통과해도 후자에서 무너진다.

추가로 컨텍스트 관련 경고가 매 턴 발생했다:

```
⚠️ Context file AGENTS.md TRUNCATED: 73937 chars exceeds limit of 31457
```

Hermes는 작업 디렉터리의 AGENTS.md를 컨텍스트로 자동 주입하는데, 리포 루트에서 실행하는 바람에 리포의 74K자짜리 AGENTS.md가 딸려 들어와 기본 한도(`context_file_max_chars` ≈ 31.5K자)에서 잘렸다. 소형 모델에게 잘린 대형 컨텍스트는 혼란 요인만 된다. **리포 루트가 아닌 별도 작업 디렉터리에서 실행하면 사라지는 문제다.**

### 4.1 원인 격리: Ollama 모델의 툴 지원 검증법 (최초 3단계 → 4.2절에서 4단계로 개정)

재테스트에서 실패 양상이 바뀌었다. 검색 결과를 무시하는 대신 *"이전 툴 콜의 출력을 달라(Please provide the tool results)"*고 응답 — 즉 맥락은 잡았지만 **툴 결과 자체가 모델에게 보이지 않는 것처럼** 행동했다. 상태바 토큰 수가 검색 후에도 2.05K에서 거의 움직이지 않은 것도 방증이었다. 이러면 모델 추론력 문제와 별개로, **채팅 템플릿이 `tool` role 메시지를 프롬프트로 렌더링하지 못해 결과가 조용히 증발할 가능성**이 생긴다.

이를 Hermes와 무관하게 확정하려면 Ollama에 직접 "툴 결과가 이미 도착한 상태"의 대화를 던져보면 된다:

```powershell
$body = @'
{
  "model": "gemma4:e2b",
  "messages": [
    {"role": "user", "content": "서울 날씨 알려줘"},
    {"role": "assistant", "tool_calls": [{"id": "call_1", "type": "function",
      "function": {"name": "get_weather", "arguments": "{\"city\": \"Seoul\"}"}}]},
    {"role": "tool", "tool_call_id": "call_1", "content": "Seoul: 31C, sunny, humidity 70%"}
  ],
  "stream": false
}
'@
Invoke-RestMethod -Uri http://127.0.0.1:11434/v1/chat/completions -Method Post `
  -ContentType "application/json" -Body $body |
  Select-Object -ExpandProperty choices | ForEach-Object { $_.message.content }
```

**실행 결과: "Please let me know what you would like to ask..."** — 툴 결과(31°C, 맑음)가 손에 쥐어진 상태에서도 이를 전혀 인지하지 못했다. 프레임워크를 완전히 배제한 최소 조건에서의 실패이므로, **원인은 Hermes가 아니라 모델/템플릿 차원으로 확정**됐다. 더 뼈아픈 것은 gemma4:e2b가 `ollama show` 기준 `tools`에 `thinking`까지 표기된 5.1B 모델이었다는 점이다(2.2절 표). gemma3가 아예 HTTP 400을 뱉은 것과 같은 맥락으로, gemma 계열은 "capability 표기"와 "실제 툴 결과 소화 능력"이 일치하지 않았다.

이 과정을 일반화하면, Ollama 로컬 모델을 에이전트 프레임워크에 붙이기 전 검증 절차가 나온다. 처음엔 3단계로 정리했지만, 아래 4.2절에서 실제로 qwen3:8b를 테스트하며 **빠뜨렸던 관문 하나를 더 발견**했다 — 그래서 지금은 4단계다:

![모델 툴 지원 검증 관문](/assets/img/posts/model-verification-gates.svg)
*(그림은 최초 3단계 버전이다. ②와 ③ 사이에 "Hermes 자체 최소 요구사항" 관문이 하나 더 있다는 것이 4.2절의 발견이며, 순서는 아래 목록이 최신이다.)*

1. **`ollama show <모델>`** — capabilities에 `tools` 존재 확인 (없으면 HTTP 400으로 즉사)
2. **Hermes 자체 최소 요구사항 확인** — 컨텍스트 윈도우가 Hermes의 하한(64,000 토큰)을 넘는지 확인 (4.2절 신설 — 이걸 놓쳐서 qwen3:8b가 여기서 막혔다)
3. **격리 테스트** — Ollama API에 tool role 메시지를 직접 던져 소화하는지 확인 (통과 못 하면 프레임워크에 붙여도 무의미)
4. **프레임워크 연결** — 그제서야 Hermes에 붙여 멀티턴 루프 검증

①만 믿고 세팅하면 ③에서 무너지는 모델에 시간을 낭비하게 된다(gemma4:e2b 사례). 이번엔 그와 다른 실패 양상도 나왔다 — ①은 통과했지만 **②에서 아예 막혀 ③·④를 시도조차 못 한 경우**다(qwen3:8b 사례, 아래).

### 4.2 세 번째 시도: qwen3:8b — 예상과 다른 관문에서 조기 탈락

4.1절 말미에는 "Qwen3 등 툴 콜링이 실전 검증된 계열은 격리 테스트(당시 기준 관문②)를 통과할 것"이라고 적었다. 실제로 `ollama pull qwen3:8b` 후 Hermes에 연결해보니, 그 예측을 검증할 기회조차 없이 **더 앞선 단계에서 막혔다.** Hermes 실행 자체가 다음 메시지와 함께 거부됐다:

```
Failed to initialize agent:
Model qwen3:8b has a context window of 40,960 tokens,
which is below the minimum 64,000 required by Hermes Agent.
```

`ollama show qwen3:8b`로 확인한 실측 스펙:

```
architecture        qwen3
parameters          8.2B
context length      40960
quantization        Q4_K_M

Capabilities
  completion
  tools
  thinking
```

**해석.** 관문①(tools capability)은 명백히 통과했다 — `tools`, `thinking`까지 표기되어 있다. 그런데도 대화를 시작조차 못 했다. 이유는 gemma 계열의 실패(모델이 결과를 소화 못함, 4.1절)와 완전히 다른 층위다. **Hermes Agent 자신이 "에이전트 루프를 정상적으로 돌리려면 최소 64K 컨텍스트가 필요하다"는 하한선을 걸어두고, 이를 밑도는 모델은 아예 실행을 거부한다.** 1.3절(에이전트 루프)에서 짚었듯 시스템 프롬프트+툴 스키마+AGENTS.md만으로 대화 시작 전에 이미 1만 토큰 이상을 먹는 구조이니, Hermes 입장에서는 합리적인 방어 장치다. 이 관문을 4.1절 정리 당시엔 몰랐다 — 그래서 검증 절차를 3단계에서 4단계로 고친 것이 위 개정이다.

**해결 시도한 대안과 각각의 문제 (사유 포함).**

| 대안 | 방법 | 채택하지 않은 사유 |
|---|---|---|
| config.yaml에서 강제 상향 | `model.context_length: 65536` 지정 | Hermes 에러 메시지 자체가 "서버가 실제보다 작게 보고할 때"를 위한 옵션이라고 안내한다. 여기서는 Ollama가 보고한 40960이 **모델 실제 스펙**이므로, 강제로 올려도 실제 처리 능력이 커지는 게 아니라 응답 품질 저하·KV 캐시 폭증·OOM 위험만 커진다 |
| Ollama Modelfile로 `num_ctx` 재정의 | `ollama show --modelfile` → `PARAMETER num_ctx 65536` 수정 → 재빌드 | 기술적으로 가능하지만 RAM 사용량이 그만큼 증가한다. 16GB급 노트북에서 여유가 없다고 판단해 보류 |
| 더 큰 Qwen 모델(14B/32B)로 교체 | `ollama pull qwen3:14b` 등 | 아래 하드웨어 표에서 보듯 이 노트북 사양(RAM 16GB)에서는 14B부터 "매우 부담", 32B는 "사실상 불가"로 판단해 시도하지 않음 |

**현재 하드웨어(노트북, Intel Ultra 5 125U, RAM 16GB) 기준 현실성 판단:**

| 모델 | 현실성 | 근거 |
|---|---|---|
| Qwen3 4B | 여유 있음 | 파라미터가 작아 RAM 부담 적음 |
| Qwen3 8B | 현실적 상한선 | 이번에 실제 테스트한 라인 — 단, Hermes의 64K 요구는 미달 |
| Qwen3 14B | 매우 부담 | RAM 16GB에서 상시 구동은 어려움 |
| Qwen3 32B | 사실상 불가 | 로딩조차 버거운 크기 |
| Gemma4:e2b | 매우 적합 (크기상) | 5.1B로 가볍고 컨텍스트도 131K로 충분 — 다만 4.1절에서 확인했듯 에이전틱 추론력 자체가 부족 |

이 표가 가리키는 결론은 명확하다. **이 노트북에서는 "Hermes의 최소 요구사항(64K)을 만족하면서 동시에 에이전틱 추론이 가능한" 로컬 모델이 존재하지 않는다.** 컨텍스트가 넉넉한 gemma4:e2b는 추론력이 부족하고, 추론력에 여지가 있는 qwen3 계열은 이 하드웨어에서 컨텍스트 요구를 만족하는 크기까지 못 올라간다. 두 조건의 교집합이 현재 장비 위에 없다는 것이 5.4절 결론의 근거다.

---

## 5. 무료 PoC의 제약 사항 총정리

### 5.0 백문이 불여일견 — 대표 실패 장면 (실제 화면 그대로)

이 절을 표와 일반론보다 앞에 두는 사유: "소형 모델은 에이전틱 역량이 부족하다"는 문장보다 실제 화면 하나가 그 한계를 훨씬 정확하게 전달하기 때문이다. 아래는 gemma4:e2b 기반 Hermes에 가장 평범한 요청을 던졌을 때의 출력 전문이다.

```
● Kubernetes 1.35의 주요 변경사항을 검색해서 3줄로 요약해줘.
────────────────────────────────────────
  ┊ 🔍 preparing web_search…
  ┊ 🔍 search    Kubernetes 1.35 major changes  3.0s
╭─ ⚕ Hermes ─────────────────────────────────────────────────╮
    Please provide the tool results you are referring to.
    I need the output from the previous tool calls to
    understand what to process and how to continue with
    your request.
╰────────────────────────────────────────────────────────────╯
 ⚕ gemma4:e2b │ 2.05K/131.1K │ [░░░░░░░░░░] 2% │ …
```

이 짧은 화면에 한계의 전모가 들어 있다. 줄별로 읽으면:

1. **`search  Kubernetes 1.35 major changes  3.0s`** — 프레임워크는 제 몫을 다 했다. 모델의 툴 호출 요청을 받아 실제로 DuckDuckGo 검색을 3.0초간 실행했고, 결과를 tool 메시지로 주입했다. 한국어 요청을 영어 검색어로 바꾼 것도 모델이 해냈다 — 그림 2의 ①~④까지는 정상.
2. **"Please provide the tool results"** — 그런데 모델은 방금 손에 쥐어진 그 결과를 **달라고 요구한다**. 검색 결과가 대화 이력에 들어왔는데도 인지하지 못하는 것. ④→⑤ 구간의 단절이며, 4.1의 격리 테스트로 이것이 Hermes가 아닌 모델/템플릿 차원의 문제임이 확정됐다.
3. **`2.05K/131.1K │ 2%`** — 상태바가 방증이다. 검색 결과가 정상적으로 소비됐다면 토큰 카운터가 움직였어야 하는데 대화 시작 수준에 머물러 있다. 명목 컨텍스트 131K가 있어도 그것을 **쓰지 못하면** 없는 것과 같다.

요컨대 무료 로컬 소형 모델의 한계는 "느리다"나 "답이 어설프다" 수준이 아니라, **에이전트 루프가 단 한 스텝도 완주되지 않는다**는 것이다. 검색·터미널·파일 등 모든 툴이 완벽히 준비되어 있어도, 그 결과를 소화할 두뇌가 없으면 에이전트는 성립하지 않는다. 이것이 아래 구조적 제약의 실물이다.

### 5.1 구조적 제약: 성능 하한은 프레임워크가 아니라 모델이 결정한다

이번 실험의 가장 큰 결론. Hermes 프레임워크 자체는 무료·오픈소스·로컬 완결이 가능하지만, Hermes의 한 턴은 (거대한 시스템 프롬프트 + 30개 툴 스키마 + 스킬 문서 + 메모리 + 대화 이력)을 소화한 뒤 툴 선택 → 결과 해석 → 다음 행동 결정을 최대 150회 반복하는 루프다. 공식 문서가 Nous Portal 카탈로그를 "frontier agentic models"(Claude, GPT, Gemini, DeepSeek, Qwen 등)로 표현하고, 프롬프트 캐싱 최적화가 사실상 Claude(native Anthropic / OpenRouter / Nous Portal) 중심으로 설계된 것도 이 루프가 프론티어급 모델을 전제하기 때문이다.

로컬 소형 모델에서 관찰된 실패를 일반화하면:

1. **시스템 프롬프트 준수 실패** — 긴 지시를 유지하지 못하고 사전학습 페르소나로 회귀
2. **툴 결과 통합 실패** — 툴을 호출해도 결과를 응답에 반영하지 못함. 에이전트 루프가 1스텝에서 끊김
3. **컨텍스트 예산 부족** — 명목 131K 컨텍스트라도, 시스템 프롬프트+툴 스키마만으로 1만 토큰 이상을 점유하면 실효 추론 품질 급락
4. **자기 개선 루프 무력화** — 스킬 자가생성/개선, 메모리 큐레이션 등 Hermes의 차별화 기능은 모델의 메타인지에 의존하므로 소형 모델에서는 사실상 발동하지 않음

따라서 **실사용의 현실적 선택지는 (a) Nous Portal 구독, (b) Anthropic/OpenAI 등 유료 API 키 또는 Claude Pro/ChatGPT Pro OAuth 연동(v0.14.0 subscription proxy), (c) OpenRouter 종량제로 수렴한다.** "무료 오픈소스 에이전트"라는 표현은 프레임워크에 대한 것이지 실사용 경험에 대한 것이 아니다. 로컬로 버티려면 최소 Qwen3 32B, Llama 3.x 70B급 + 이를 돌릴 GPU가 필요한데, 이는 비용이 하드웨어로 이동한 것일 뿐이다.

### 5.2 기능별 제약 (무료 구성에서 되는 것 / 안 되는 것)

| 기능 | 무료 구성에서 | 비고 |
|---|---|---|
| 대화 + 툴 콜링 파이프라인 | ⭕ (모델 역량 한도 내) | 프레임워크 동작 관찰·학습용으로는 충분 |
| 터미널/파일/코드 실행 | ⭕ | local 백엔드, 키 불필요 |
| 웹 검색 | △ **스니펫까지만** | ddgs는 search-only. 본문 추출(web_extract)은 Firecrawl/Tavily/Exa 등 필요 |
| 페이지 본문 추출 | ❌ → 무료 우회 있음 | Firecrawl **Self-Hosted**(Docker) 또는 Brave Search 무료 키(월 2천 쿼리)로 보강 가능 |
| 브라우저 자동화 | △ | Local Chromium은 무료지만 agent-browser 의존성 이슈 확인 필요 |
| TTS | ⭕ | Edge TTS 무료. 완전 로컬은 KittenTTS/Piper |
| 이미지 생성 | ❌ | 무료 프로바이더 없음 (FAL/OpenAI 키 필요) |
| 비디오 분석/생성, X 검색 | ❌ | 비디오 지원 모델·xAI 키 필요 |
| Skills Hub (스킬 공유) | ❌ → 무료 우회 있음 | GITHUB_TOKEN만 있으면 됨 (토큰 발급 자체는 무료) |
| Computer Use | △ | cua-driver 무료지만 Windows 설치 실패 사례 있음 |
| 메시징 게이트웨이 | ⭕ | 각 플랫폼 봇 토큰 발급은 무료 (Telegram 등) |

### 5.3 그럼에도 무료 PoC의 가치

프레임워크의 구조(설정 체계 config.yaml/.env 분리, 세션·스킬·메모리 저장 방식, 툴 파이프라인, 컨텍스트 압축 동작)를 비용 없이 해부할 수 있고, 트랜스포트와 툴 스키마가 어떻게 오가는지 로그로 관찰하는 학습용으로는 충분하다. "이 프레임워크에 유료 모델을 붙일 가치가 있는가"를 판단하는 데 필요한 정보는 무료 구성으로도 다 얻을 수 있었다.

### 5.4 개인적 결론 — 비용이 먼저, 통제는 그다음

배경(문서 서두)에서 밝힌 대로, 이 PoC의 원래 목표는 "비용 없이, 기밀이 새지 않게, 로컬에서 완결되는 DevOps 자동화 에이전트"였다. gemma4:e2b(4장)와 qwen3:8b(4.2절) 두 모델을 순서대로 검증한 결과, 이 목표는 **현재 컴퓨터 사양(RAM 16GB 노트북)으로는 무리**라는 결론에 도달했다. 사유는 4.2절 표에서 이미 드러났다 — 이 하드웨어 위에는 "Hermes의 최소 컨텍스트 요구를 만족하면서 동시에 에이전틱 추론이 가능한" 로컬 모델의 교집합이 존재하지 않는다.

여기서 얻은 개인적 판단은 두 가지다.

**첫째, Hermes Agent로 의도한 자동 DevOps를 구현하려면 결국 비싼(=성능이 좋은) 모델이 있어야 한다.** 이건 "돈을 더 쓰면 더 좋다" 수준의 뻔한 이야기가 아니라, 이번 PoC로 확인된 **문턱 조건**이다 — 4.2절에서 본 것처럼 에이전트 루프가 요구하는 최소 컨텍스트·추론력 자체가 로컬 소형 모델의 상한 밖에 있었다. 무료 구성으로는 "프레임워크를 써볼 수는 있지만 에이전트로 쓸 수는 없다"는 것이 이번 실험의 반복된 결론이다(gemma4:e2b는 4장, qwen3:8b는 4.2절 — 실패 지점은 서로 다르지만 결론은 같다).

**둘째, Claude API·ChatGPT 등으로 전환할 경우 비용이 사용량에 비례해 증가한다는 점을 선행 조건으로 반드시 고려해야 한다.** 구독형(월 정액)과 달리 API 과금은 에이전트가 대화를 몇 턴 돌렸는지, 툴을 몇 번 호출했는지, 컨텍스트를 얼마나 채웠는지에 그대로 연동된다. 1.3절에서 짚었듯 Hermes의 한 턴은 최대 150회의 루프를 돌 수 있는 구조이므로, 통제 없이 풀어두면 비용이 어디까지 늘어날지 예측하기 어렵다. **에이전트에게 어떤 범위(디렉터리, 툴, 권한)를 주고 어떻게 통제할 것인가는, 비용 문제를 먼저 받아들이고 난 다음에 풀어야 할 그다음 문제**라고 판단했다. 순서를 바꿔서 통제 설계부터 붙잡으면, 정작 그 통제를 적용할 만큼 똑똑한 모델이 없다는 걸 뒤늦게 깨닫게 된다 — 이번 PoC가 그 반대 순서로 흘렀다.

이 판단이 이 문서에 남기는 사유: 6장의 보완 체크리스트와 7장의 결론을 이 순서(① 비용 감당 여부 확정 → ② 그 다음 에이전트 범위·권한 설계)로 재정렬한다.

---

## 6. 현재 세팅의 문제점과 보완 체크리스트

우선순위 순.

**① 다음 방향 결정 (최우선, 갱신됨).** gemma4:e2b(4장)와 qwen3:8b(4.2절) 두 무료 로컬 모델이 순서대로 실패하면서, "이 하드웨어에서 무료로 되는 로컬 모델을 더 찾아본다"는 선택지는 5.4절 근거로 사실상 소진됐다고 판단한다. 남는 갈래는 둘이다. (a) **여기서 PoC를 마무리하고 결론(비용이 선행 조건)을 보고한다** — 무료 구성의 한계를 확인하는 것이 애초 이 PoC의 목적 중 하나였으므로 이 자체로 유효한 결론이다. (b) **비용을 감수하고 다음 단계로 간다** — OpenRouter 종량제(소액부터 시작 가능), Anthropic/OpenAI API 키, 또는 Nous Portal 구독 중 하나를 선택하되, 5.4절의 판단대로 **먼저 예산 상한을 정한 뒤** 에이전트 범위·권한 설계(⑥번 항목)로 넘어갈 것. 어느 쪽으로 가든 새 모델을 붙이기 전 4.1·4.2절의 검증 절차를 먼저 거칠 것 — 이번엔 그 절차 자체가 3단계에서 4단계로 늘었다는 걸 기억할 것.

**② AGENTS.md 잘림 해소.** 리포 루트가 아닌 별도 작업 디렉터리에서 실행. 또는 `context_file_max_chars` 상향(단, 소형 모델에는 역효과)이나 AGENTS.md 요약본 대체.

**③ web_extract 프로바이더 보강.** 검색 스니펫 이상이 필요하면 Firecrawl Self-Hosted(Docker, 무료) 또는 Brave Search 무료 키를 붙일 것. 현재는 검색만 되고 본문 추출이 안 되는 반쪽 상태.

**④ cua-driver 재설치 또는 비활성화.** 안내된 PowerShell 명령으로 재설치하거나, 쓸 계획이 없으면 `hermes setup tools`에서 꺼둘 것. 미설치 상태로 켜져 있으면 모델이 호출을 시도하다 실패하며 턴을 낭비한다.

**⑤ Browser Automation 실상 확인.** `hermes doctor`로 로컬 Chromium이 실제 사용 가능한지, 요약 화면의 `agent-browser missing`이 실제 차단 요인인지 검증.

**⑥ 보안 격리 (DevOps 시각) — 비용 다음 순서.** local 백엔드는 에이전트가 내 계정 권한으로 임의 셸을 실행한다. 소형 모델일수록 오동작 확률이 높으므로 본격 실험 전 Docker 백엔드로 격리 권장. 파일 변경은 체크포인트/`/rollback`으로 되돌릴 수 있지만 **셸 명령의 부수효과는 롤백되지 않는다.** 5.4절의 판단대로, 이 항목(에이전트에게 얼마나 넓은 권한을 줄지)은 ①에서 비용 지불 여부를 먼저 결정한 뒤에 설계할 문제다 — 아직 어떤 모델로 갈지도 못 정한 상태에서 권한 설계부터 정교화하는 것은 순서가 바뀐 작업이다.

**⑦ 컨텍스트 압축 설정 재검토.** 현재 threshold 50%인데, 압축 요약도 기본적으로 메인 모델(auxiliary auto=main)이 수행하므로 소형 모델에서는 품질 저하가 중첩된다. 프론티어 모델 교체 후에는 auxiliary(vision, compression 등)를 저가 모델로 분리하는 것이 문서상 권장 패턴.

---

## 7. 결론

이 PoC는 "비용 없이, 기밀이 새지 않게, 로컬에서 완결되는 DevOps 자동화 에이전트"라는 가설(배경 절)에서 출발했다. Hermes Agent는 설치 UX(자동 의존성 설치, 단계별 무료/유료 표기, config 자동 백업), 오류 리포팅, 프로바이더 추상화 등 프레임워크 완성도가 높고, 스킬 자가생성·세션 간 기억이라는 뚜렷한 차별점이 있다. 무료 구성만으로 설치부터 툴 파이프라인 관찰까지의 PoC는 충분히 가능하다.

그러나 그 차별점은 전부 프론티어급 모델의 추론 능력 위에서만 발현된다. 두 모델을 순서대로 무료로 테스트했고 둘 다 실패했다 — gemma4:e2b는 툴 콜링 형식은 통과했지만 에이전트 루프를 단 한 스텝도 완주하지 못했고(4장), qwen3:8b는 그보다도 이른 단계인 Hermes 자체의 최소 컨텍스트 요구(64K)에서 막혔다(4.2절). 이미지 생성·본문 추출 등 일부 기능은 무료 구성에 아예 존재하지 않는다. **"프레임워크 견학"은 무료로 가능하지만 "에이전트 사용"에는 유료 모델이 사실상 필수**라는 것이 결론이다.

여기에 이번 PoC로 얻은 개인적 결론(5.4절)을 더하면: 유료로 전환하는 경우 API 과금은 사용량에 비례해 늘어나므로, **비용을 먼저 선행 조건으로 받아들이고 예산 상한을 정한 뒤에야 "에이전트에게 얼마나 넓은 권한을 줄 것인가"라는 통제 설계로 넘어가는 것이 맞는 순서**라고 판단한다. 이번 PoC는 정확히 그 반대 순서(먼저 로컬·무료로 통제 걱정 없이 시도)로 진행했고, 그 결과 이 하드웨어의 한계에 먼저 부딪혔다.

다음 단계: ① 무료 로컬로 더 갈지, 비용을 감수하고 다음 단계로 갈지 결정(6장 ①) → (b를 선택할 경우) ② 예산 상한 확정 → ③ web_extract 보강 → ④ Docker 격리로 에이전트 권한 범위 설계 → 동일한 6개 검증 시나리오 재실행 후 비교.

---

### 참고 자료
- 공식 문서: https://hermes-agent.nousresearch.com/docs/ (LLM용: /llms.txt, /llms-full.txt)
- AI Providers 가이드: https://hermes-agent.nousresearch.com/docs/integrations/providers
- Configuration(터미널 백엔드, auxiliary 모델, context_file_max_chars): https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- Tools 가이드: https://hermes-agent.nousresearch.com/docs/user-guide/features/tools
- Features Overview: https://hermes-agent.nousresearch.com/docs/user-guide/features/overview
- GitHub: https://github.com/NousResearch/hermes-agent
