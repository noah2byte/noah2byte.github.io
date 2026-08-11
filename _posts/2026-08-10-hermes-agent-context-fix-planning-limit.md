---
title: "Hermes Agent 후속 — 컨텍스트 벽을 넘자 나타난 새로운 벽"
date: 2026-08-10 23:00:00 +0900
categories: [운영 이모저모, LLM]
pin: false
math: false
mermaid: false
---

# Hermes Agent 후속 — 컨텍스트 벽을 넘자 나타난 새로운 벽

> 전편: [Hermes Agent 무료(Zero-Cost) PoC 가이드](/posts/hermes-agent-local-guide/)
> 이 글은 전편의 4.3절에서 이어진다. 남겨뒀던 숙제 하나를 실제로 풀어본 기록이다.

---

## 왜 이 글을 따로 쓰는가

전편 4.3절 결론은 "qwen3:8b는 에이전틱 추론 능력 자체는 있지만, Hermes가 요구하는 최소 컨텍스트(64K)를 현재 설정(40960)이 못 채워서 실행 자체가 거부된다"였다. 그리고 남은 선택지로 YaRN이라는 RoPE 스케일링 방식을 다음 과제로 남겨뒀다.

이 글을 별도로 쓰는 사유는, 실제로 그 벽을 넘어보니 **예상과 다른 경로로 풀렸고, 그 직후 예상하지 못한 새로운 벽이 나타났기** 때문이다. 전편에 끼워 넣기엔 전편이 이미 충분히 길었고, 무엇보다 이번 발견은 "컨텍스트 문제 해결"이라는 하나의 사건이 아니라 "관문을 하나 넘으면 다음 관문이 보인다"는 패턴 자체를 보여주는 사례라, 독립된 글로 다룰 가치가 있다고 판단했다.

---

## 1. YaRN 대신 먼저 시도한 것 — 에러 메시지가 알려준 지름길

전편에서는 다음 시도로 YaRN을 예고했다. 하지만 실제로 `hermes chat`을 재실행했을 때, Hermes 자신이 내놓은 에러 메시지가 YaRN보다 훨씬 직접적인 해법을 담고 있었다:

```
❌ Ollama runtime context is too small for Hermes tool use
   Ollama loaded qwen3:8b with only 40,960 tokens of runtime context, but Hermes
   needs at least 64,000 tokens for reliable tool use. Increase the Ollama context
   for this model and restart/reload the model before trying again. A known-good
   starting point is 65,536 tokens. In Hermes config, set model.ollama_num_ctx: 65536
   (and model.context_length: 65536 if you also override the displayed model context).
```

YaRN을 먼저 시도하지 않은 이유를 밝혀둔다. YaRN은 모델의 네이티브 학습 길이(Qwen3-8B의 경우 32K)를 RoPE 스케일링으로 늘리는 방식이라 원리적으로는 더 정교하지만, Ollama의 GGUF 배포판이 `rope_scaling` 설정을 얼마나 매끄럽게 받아들이는지 전편 시점엔 검증되지 않은 상태였다. 반면 에러 메시지가 직접 제시한 `ollama_num_ctx` 설정은 Hermes가 공식적으로 지원을 명시한 경로이므로, 검증 안 된 방법보다 검증된 방법을 먼저 시도하는 게 순서상 맞다고 판단했다.

### 시도 1 — `model.context_length`만 바꾸면 왜 안 되는가

```powershell
hermes config set model.context_length 65536
```

이 명령으로 config.yaml에는 값이 반영됐지만, `hermes chat`을 다시 실행하니 동일한 초기화 거부 에러가 그대로 재현됐다. 처음엔 설정이 안 먹힌 줄 알았는데, 원인은 따로 있었다.

Hermes는 컨텍스트를 두 갈래로 나눠 관리한다. `context_length`는 Hermes 자신이 "이 모델의 컨텍스트가 이 정도"라고 판단·표시하는 값이고, `ollama_num_ctx`는 Ollama 런타임에게 "이 모델을 이 크기로 메모리에 올려라"라고 지시하는 값이다. 전자만 고쳐서는 후자, 즉 실제로 모델을 서빙하는 Ollama 프로세스는 여전히 기본값(40960)으로 모델을 로드하고 있었던 것이다. 이 둘을 하나로 착각한 것이 첫 시도가 실패한 이유다.

### 시도 2 — `ollama_num_ctx`를 별도로 지정

```powershell
hermes config set model.ollama_num_ctx 65536
```

```
✓ Set model.ollama_num_ctx = 65536 in C:\Users\<user>\AppData\Local\hermes\config.yaml
```

이 명령 이후 `hermes chat`이 컨텍스트 에러 없이 정상 초기화됐다. 전편(4.2절)에서 검토했던 두 대안 — config 강제 상향, 또는 Ollama Modelfile에 `PARAMETER num_ctx 65536`을 넣고 `ollama create`로 커스텀 모델을 재빌드하는 방식 — 중 후자를 실제로 시도하려다가, Hermes가 이미 제공하는 `ollama_num_ctx` 키가 있다는 걸 에러 메시지에서 발견하고 그쪽으로 전환했다. Modelfile 재빌드는 새 모델 이름을 만들고 Hermes 설정에서 그 이름으로 다시 연결해야 하는 두 단계 작업인데, 이 방법은 한 줄로 끝난다 — 지름길이 있는데 돌아갈 이유가 없었다.

---

## 2. 관문④를 넘으니 나타난 관문⑤ — "소화 능력"과 "범위 판단력"은 다른 근육이다

컨텍스트 문제가 풀렸으니 이제 전편 4.3절에서 격리 테스트로 확인했던 "결과를 소화하는 능력"이 실제 Hermes 프레임워크 위에서도 재현되는지 확인할 차례였다. 다음 요청을 던졌다:

```
search_files 도구로 현재 디렉토리에 어떤 파일들이 있는지 찾아줘
```

이 요청은 `search_files` 툴 하나만 있으면 완결되는, 난이도로 치면 전편 3.8절 시나리오의 2단계(터미널 실행) 수준이다. 그런데 실제 로그는 이랬다:

```
🔎 preparing search_files…
🔎 grep        25.1s
🔍 preparing web_search…
🔍 search    how to find and extract text from files in a directory using python  2.3s
📄 preparing web_extract…
📄 fetch     [www.computerhope.com] +4  0.2s
(◔_◔) ruminating...
⚕ qwen3:8b │ 2.05K/65.5K │ 10m+
```

`search_files`(내부적으로 grep 실행)까지는 요청과 정확히 맞아떨어졌다. 문제는 그다음이다. 모델은 여기서 멈추지 않고 "디렉토리에서 텍스트를 찾고 추출하는 방법"을 스스로 웹에서 검색하기 시작했고, 검색 결과 페이지 5개를 fetch까지 했다. 10분이 넘도록 응답이 나오지 않아 결국 지켜보다 만 상태로 기록을 남겼다.

여기서 짚어야 할 것은, 이게 전편 4.1절에서 gemma4:e2b가 보였던 실패와 **다른 종류**라는 점이다. gemma4:e2b는 tool 결과를 손에 쥐고도 그걸 인지하지 못했다 — 결과를 소화하는 단계 자체가 무너진 경우다. 반면 이번 qwen3:8b는 각 tool 호출 결과를 정상적으로 소화하며 다음 행동을 판단했다. 다만 그 판단이 "이 작업엔 이거 하나면 충분하다"가 아니라 "혹시 더 필요할지도 모르니 검색도 해보자"는 방향으로 계속 뻗어나갔다. 결과를 읽어내는 것과, 언제 멈춰야 하는지 아는 것은 서로 다른 역량이라는 뜻이다. 전자를 "이해력"이라 부른다면 후자는 "판단력" 내지 "범위 감각(scoping)"에 가깝다.

이 구분을 이 글에 남기는 사유는, 실무에서 "이 모델이 tool calling이 되나요?"라는 질문 하나로는 에이전트 도입 여부를 판단할 수 없다는 걸 직접 겪었기 때문이다. tool calling 지원, 결과 소화, 작업 범위 통제는 각각 별개로 무너질 수 있는 지점이고, 하나를 통과했다고 나머지가 따라오지 않는다.

---

## 3. 관문을 다섯 개로 다시 그리다

전편은 4단계 관문(① tools capability → ② Hermes 최소 컨텍스트 → ③ 격리 테스트 → ④ 프레임워크 연결)으로 검증 절차를 정리했다. 이번 결과를 반영해 다섯 번째 관문을 추가한다.

| 관문 | qwen3:8b | 확인 방법 |
|---|---|---|
| ① tools capability | 통과 | `ollama show <모델>` |
| ② Hermes 최소 컨텍스트(64K) | **통과** (`ollama_num_ctx: 65536` 설정) | `hermes chat` 초기화 여부 |
| ③ 격리 테스트(툴 결과 소화) | 통과 | Ollama API에 tool role 직접 주입 |
| ④ 프레임워크 연결(초기화) | 통과 | `hermes chat` 정상 기동 |
| ⑤ 작업 범위 통제(planning/scoping) — 신설 | **미흡** | 단순 요청 → 필요 최소 tool 수로 완료되는지 관찰 |

관문을 이렇게 계속 쪼개는 이유는, "에이전트가 동작하는가"라는 질문이 사실 하나의 질문이 아니기 때문이다. 이번에 다섯 번째 관문이 나온 것처럼, 앞으로 실제 업무에 투입하는 단계로 가면 또 다른 관문(예: 150회 루프를 안정적으로 유지하는가, 스킬 자가생성이 실제로 유용한 품질로 나오는가)이 나올 가능성이 높다고 본다.

---

## 4. 다음에 확인할 것 — 그리고 이번 시리즈에서 유보하는 것

관문⑤가 모델 크기의 근본 한계인지, 아니면 지시 방식의 문제인지는 아직 구분하지 못했다. 다음으로 시도해볼 것은 시스템 프롬프트나 AGENTS.md에 "이 작업에 필요한 최소한의 tool만 사용하라"는 제약을 명시적으로 넣고, 같은 요청을 다시 던져보는 것이다. 이 제약만으로 개선된다면 지시 방식의 문제였다는 뜻이고, 그래도 비슷한 양상이 반복된다면 8B급 모델의 planning 역량 자체가 부족하다는 뜻으로 받아들일 생각이다.

이번 글에서 다루지 않은 것도 밝혀둔다. 컨텍스트를 65536으로 강제 확장한 것이 응답 품질에 어떤 영향을 주는지는 정량적으로 측정하지 않았다. Qwen3-8B의 네이티브 학습 길이(32K)를 넘어선 확장이므로, 이번에 관찰한 planning 저하가 이 확장 자체의 부작용인지, 모델 크기의 근본 한계인지는 이 글만으로는 분리해서 말할 수 없다. 이 부분은 다음 글에서 마저 다룬다.

---

### 참고 자료
- 전편: [Hermes Agent 무료(Zero-Cost) PoC 가이드 — 설치·세팅 전 과정과 제약 사항](/posts/hermes-agent-local-guide/)
- Configuration(model.ollama_num_ctx, model.context_length): https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- GitHub: https://github.com/NousResearch/hermes-agent
