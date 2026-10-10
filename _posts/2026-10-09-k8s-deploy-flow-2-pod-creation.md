---
title: "쿠버네티스 배포 흐름 한 번에 정리 (2) 파드가 만들어지기까지 — 트리거·체인·웹훅·노드"
date: 2026-10-09 19:10:00 +0900
categories: [운영 이모저모, K8S]
pin: false
math: false
mermaid: false
---

## 이 편에서 얻을 것

helm upgrade 한 줄이 **컨테이너 다섯 개짜리 파드**로 바뀌는 과정을, 단계마다 "누가 무엇을 보고 무엇을 하는지"로 설명할 수 있게 된다.

**1편 복습 한 줄:** 모두 API 서버에 쓰고, 각자 API 서버를 지켜보다가, 자기 차례가 오면 자기 일만 한다.

![단계 7개 중 ①~④](/assets/img/posts/k8s-deploy-flow/01-overview.svg){: w="960" h="520" }
_이 편은 윗줄 ①~④다_

### 이 편의 용어

| 용어 | 한 줄 설명 |
|---|---|
| **어드미션 웹훅** | API 서버가 오브젝트를 저장하기 직전에 외부 서버에 "이거 고칠 거 있어?"라고 묻는 장치. 고치는 쪽이 mutating, 허용·거부만 하는 쪽이 validating이다 |
| **init 컨테이너** | 앱보다 먼저, **하나씩 순서대로** 실행되고 끝나야 하는 준비용 컨테이너. 하나라도 실패하면 다음으로 넘어가지 않는다 |
| **requests** | "이 컨테이너엔 최소 이만큼 보장해 달라"는 CPU·메모리 약속. 스케줄러가 노드를 고를 때 보는 값이다 |
| **iptables** | 리눅스 커널의 패킷 규칙. "이 포트로 가는 패킷은 저기로 돌려라" 같은 규칙을 건다 |

각 단계는 같은 틀로 정리했다. **한 줄 → 누가·무엇을 보고·무엇을 → 왜 → 확인 명령.** 어느 단계를 펴도 같은 순서로 읽혀서 비교가 쉽기 때문이다.

---

## ① 트리거 — 변경이 API 서버에 도착한다

**한 줄:** 배포 도구가 하는 일은 결국 "Deployment의 파드 템플릿을 바꿔 API 서버에 보내는 것"뿐이다.

| 경로 | 누가 | 무엇을 한다 |
|---|---|---|
| 직접 배포 | Jenkins → Helm | values의 이미지 태그를 바꿔 `helm upgrade` → 렌더링된 매니페스트를 API 서버에 적용 |
| GitOps 배포 | Jenkins → Git → ArgoCD | yq로 values의 이미지 태그만 바꿔 Git push → ArgoCD가 Git과 클러스터의 차이를 보고 적용 |

- **왜 이게 중요한가:** 두 경로는 **여기까지만** 다르다. API 서버에 도착한 뒤부터는 완전히 같다. 그래서 설명할 때 "여기서부터는 같습니다" 한 문장으로 갈라 주면 구조가 선다
- **포인트:** 이미지 태그가 바뀌면 파드 템플릿의 해시가 바뀌고, 그래서 새 ReplicaSet이 생긴다. replicas 숫자만 바꾸면 새 ReplicaSet은 생기지 않는다

```bash
kubectl rollout history deploy/api-backend -n app
helm history api-backend -n app
```

---

## ② 체인 — Deployment → ReplicaSet → Pod

**한 줄:** Deployment 컨트롤러는 ReplicaSet을, ReplicaSet 컨트롤러는 Pod를 "장부에 올릴" 뿐이다. 실제로 컨테이너를 띄우지 않는다.

| 누가 | 무엇을 보고 | 무엇을 한다 |
|---|---|---|
| API 서버 | 들어온 변경 | 인증·인가·검증 후 etcd에 저장 |
| Deployment 컨트롤러 | 템플릿 해시가 바뀐 Deployment | 새 ReplicaSet 생성, 옛 RS와 개수 조절 |
| ReplicaSet 컨트롤러 | 원하는 수보다 파드가 적은 RS | Pod 생성 요청 |

- **왜 두 단계로 나뉘나:** ReplicaSet은 "이 템플릿으로 N개"만 책임지고, Deployment는 "어떤 RS를 몇 개씩 둘지(롤링)"를 책임진다. 역할을 나눴기 때문에 **옛 RS가 남아 있고, 그래서 롤백이 된다**
- **롤링 중에는 RS가 두 개다.** 새것은 늘고 옛것은 준다

```bash
kubectl get rs -n app -l app=api-backend   # 새 RS와 옛 RS가 함께 보인다
kubectl describe rs <새-rs> -n app         # 파드 생성 실패는 여기 Events에 찍힌다
```

---

## ③ 웹훅 — 저장 직전에 컨테이너가 끼워진다

**한 줄:** 파드가 etcd에 저장되기 **직전**에 API 서버가 웹훅을 부르고, 웹훅이 init 컨테이너와 사이드카를 끼워 넣는다.

API 서버 안에서 요청이 처리되는 순서는 이렇다.

```
인증 → 인가 → mutating 웹훅(내용 변경) → 스키마 검증 → validating 웹훅(허용/거부) → etcd 저장
```

![웹훅 두 개는 보는 것이 다르다](/assets/img/posts/k8s-deploy-flow/03-webhook-injection.svg){: w="1000" h="560" }
_Helm 차트에는 앱 컨테이너 하나뿐인데, 실제 파드에는 init 2개 + 컨테이너 3개가 뜬다_

| 웹훅 | 무엇을 보고 | 무엇을 넣나 |
|---|---|---|
| Istio sidecar injector | **네임스페이스 라벨** (`istio-injection=enabled` 또는 `istio.io/rev`) | `istio-init`(init) + `istio-proxy`(사이드카) |
| Vault agent injector | **파드 어노테이션** `vault.hashicorp.com/agent-inject: "true"` | `vault-agent-init`(init) + `vault-agent`(사이드카) |

- **왜 이 방식인가:** 앱 Helm 차트를 건드리지 않고 공통 기능(서비스 메시, 시크릿 주입)을 모든 파드에 일괄로 넣을 수 있다
- **위험:** 웹훅 서버가 죽으면(실패 정책이 Fail이면) **파드 생성 자체가 실패한다.** 이때 증상은 파드가 아니라 **ReplicaSet 이벤트**에 찍힌다. 파드가 아예 저장되지 못했으니까

> **헷갈리기 쉬운 것:** "네임스페이스 라벨을 보고 웹훅이 istio-init과 vault-agent-init을 넣는다"고 말하기 쉽다. 틀렸다. **라벨은 Istio만 보고, Vault는 파드 어노테이션을 본다.** 그리고 둘 다 init만이 아니라 **사이드카까지** 넣는다.
{: .prompt-warning }

```bash
kubectl get mutatingwebhookconfigurations
kubectl get ns app --show-labels
kubectl get pod <pod> -n app -o jsonpath='{.spec.initContainers[*].name}{"\n"}{.spec.containers[*].name}{"\n"}'
```

---

## ④ 노드 — 스케줄러가 고르고 kubelet이 띄운다

**한 줄:** 스케줄러는 노드를 "고르기만" 하고, 그 노드의 kubelet이 init을 순서대로 돌린 뒤 컨테이너를 띄운다.

| 누가 | 무엇을 보고 | 무엇을 한다 |
|---|---|---|
| 스케줄러 | 아직 노드가 정해지지 않은 Pod | **requests 기준**으로 들어갈 노드를 골라 API 서버에 기록(binding) |
| kubelet | 자기 노드에 배정된 Pod | 파드 네트워크 준비(IP 할당) → init을 **하나씩 순서대로** → 모든 init 성공 후 컨테이너 동시 시작 |

- **스케줄러는 limits가 아니라 requests를 본다.** requests는 "최소 이만큼은 보장"이라는 약속이라 배치의 기준이 되고, limits는 "넘으면 제한"이라는 상한이라 배치와 관계없다
  - 그래서 앱 컨테이너의 requests가 비어 있으면, 스케줄러는 앱이 실제로 쓰는 양을 모른 채 배치한다
- **init은 순서대로 돌고, 하나라도 실패하면 다음으로 안 간다.** 이 성질 때문에 아래의 8200 문제가 생긴다

### 이 편의 핵심 — init 두 개의 순서와 8200 우회

![kubelet이 파드를 띄우는 순서](/assets/img/posts/k8s-deploy-flow/04-pod-startup-timeline.svg){: w="1000" h="620" }
_istio-init이 깔아 둔 길 위로 Vault 요청이 가면, 아직 없는 프록시에 막힌다. 그래서 8200만 우회시킨다_

순서대로 따라가면 이렇다.

1. **istio-init**이 iptables 규칙을 바꿔, 이후 파드에서 나가고 들어오는 트래픽이 **나중에 뜰** istio-proxy로 가도록 **길만 깔아 둔다**
2. 그런데 **이 시점엔 istio-proxy가 아직 없다.** 사이드카는 init이 다 끝나야 뜨기 때문이다
3. 다음 차례인 **vault-agent-init**이 Vault(8200 포트)로 요청을 보내면, 그 요청은 **아직 없는 프록시로 보내져 실패**한다 → init이 끝나지 않고 파드는 `Init:1/2`에서 멈춘다
4. 그래서 Vault 포트를 프록시 **우회** 대상에서 뺐다

```yaml
# 파드 어노테이션
traffic.sidecar.istio.io/excludeOutboundPorts: "8200"
traffic.sidecar.istio.io/excludeInboundPorts: "8200"
```

> **표현을 정확히:** "istio-proxy를 **통해** 트래픽을 설정한다"(X) → istio-init은 프록시를 통하지 않는다. 그 시점엔 프록시가 없다. "8200을 트래픽 **제한**에서 뺀다"(X) → 막는 게 아니라 **돌려보내는(우회)** 것이다. **"그 시점엔 프록시가 없어서"**까지 말할 수 있으면 이해한 것이다.
{: .prompt-danger }

- vault-agent-init은 파드의 **ServiceAccount 토큰**으로 Vault에 로그인한다. Vault는 그 토큰이 진짜인지 쿠버네티스(TokenReview API)에 물어 확인하고, 그 ServiceAccount에 묶인 정책만큼만 시크릿을 내준다
- 시크릿은 `/vault/secrets/` 아래 **파일**로 만들어지고, 앱은 그 파일을 설정으로 읽는다
- 컨테이너가 뜬 뒤 `vault-agent` 사이드카는 남아서 토큰을 갱신한다

```bash
kubectl get pod -n app -w                      # Init:0/2 → Init:1/2 → PodInitializing → Running
kubectl logs <pod> -n app -c vault-agent-init  # Vault 로그인 실패는 여기
kubectl get events -n app --field-selector involvedObject.name=<pod>
```

---

## 2편 한 장 요약

| 단계 | 누가 | 한 줄 |
|---|---|---|
| ① 트리거 | Helm / ArgoCD | Deployment 템플릿을 바꿔 API 서버에 보낸다. **여기까지만 경로가 다르다** |
| ② 체인 | API 서버 → Deployment 컨트롤러 → RS 컨트롤러 | 새 RS를 만들고 Pod를 장부에 올린다. 옛 RS가 남아 롤백이 된다 |
| ③ 웹훅 | Istio(라벨) · Vault(어노테이션) | 저장 직전에 init + 사이드카를 끼운다 |
| ④ 노드 | 스케줄러(requests) → kubelet | init 순서대로: istio-init(길만 깐다) → vault-agent-init(8200 우회 덕에 통과) → 컨테이너 3개 |

<details markdown="1">
<summary>읽고 나서 바로 확인 — 8200을 우회시키지 않으면 파드는 어떤 상태로 멈추나? 왜?</summary>

`Init:1/2`. istio-init이 트래픽을 프록시로 가도록 바꿨는데, vault-agent-init이 도는 시점엔 프록시가 아직 없어서 Vault 요청이 실패하고 init이 끝나지 않는다.

</details>

**다음 편:** (3) 트래픽을 받기까지 — 컨테이너가 떴는데 왜 아직 요청이 안 오는가, 그리고 사용자 요청은 어떤 길로 들어오는가
