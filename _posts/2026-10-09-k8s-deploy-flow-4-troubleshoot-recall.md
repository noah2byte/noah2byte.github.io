---
title: "쿠버네티스 배포 흐름 한 번에 정리 (4) 장애 때 거꾸로 쓰기 + 5분 복기"
date: 2026-10-09 19:30:00 +0900
categories: [운영 이모저모, K8S]
pin: false
math: false
mermaid: false
---

## 이 편에서 얻을 것

1~3편의 7단계를 **거꾸로** 써서, 파드 상태만 보고 "어느 단계에서 끊겼나"를 바로 찾을 수 있게 된다. 그리고 이 시리즈를 잊었을 때 **5분 만에 복기**하는 루틴으로 마무리한다.

원리를 외우는 진짜 이유는 이것이다. 흐름을 알면 장애 때 볼 곳의 순서가 저절로 나온다.

---

## 1. 증상으로 단계 찾기

파드 상태는 사실 "7단계 중 어디까지 왔나"를 보여 주는 진행 표시줄이다.

| 보이는 증상 | 끊긴 단계 | 먼저 볼 곳 |
|---|---|---|
| 파드가 아예 안 생긴다 | ② 체인 또는 ③ 웹훅 | `kubectl describe rs <새-rs>` 이벤트 (`FailedCreate`, `failed calling webhook`) |
| `Pending` | ④ 스케줄링 | `describe pod` 이벤트 `FailedScheduling` (requests 부족, affinity, taint) |
| `Init:0/2`에서 멈춤 | ④ istio-init | `logs -c istio-init` |
| `Init:1/2`에서 멈춤 | ④ vault-agent-init | `logs -c vault-agent-init` (8200 우회 누락, Vault role·정책, ServiceAccount 이름) |
| `CrashLoopBackOff` | ④ 앱 기동 | `logs --previous` (설정 파일 경로, 시크릿 키 이름) |
| `Running`인데 READY `2/3` | ⑤ readiness | `describe pod`의 readiness 실패 메시지 |
| `3/3`인데 트래픽이 안 온다 | ⑤ 엔드포인트 / ⑦ 라우팅 | 아래 2장 |
| 배포 순간에만 5xx가 튄다 | ⑥ 종료 | preStop 유무, graceful shutdown, `terminationGracePeriodSeconds` |
| 503 | ⑦ Envoy | Envoy 접근 로그의 response flag |

> 위에서 아래로 내려갈수록 7단계의 뒤쪽이다. 즉 **증상표 = 7단계를 거꾸로 읽은 것**이다. 표를 외우지 말고 7단계를 떠올리면 표가 다시 만들어진다.
{: .prompt-tip }

---

## 2. "Running인데 트래픽을 안 받는다" — 보는 순서

가장 자주 만나고, 가장 많이 헤매는 상황이라 따로 뺐다.

![Running인데 트래픽을 안 받을 때 보는 순서](/assets/img/posts/k8s-deploy-flow/08-no-traffic-debug.svg){: w="960" h="720" }
_EndpointSlice에 "없을 때"와 "있는데도 안 될 때"로 갈라서 본다_

| 순서 | 질문 | 아니면 |
|---|---|---|
| ① | READY 칸이 다 찼나? | readiness 실패 이유 (`describe`) |
| ② | EndpointSlice에서 그 파드가 `ready: true`인가? | Service selector ↔ 파드 라벨, 포트 이름·번호 |
| ③ | Envoy가 그 엔드포인트를 아나? (`istioctl proxy-config endpoint`) | istiod 전파 (`istioctl proxy-status`) |
| ④ | 라우팅 규칙이 맞나? (VirtualService, Gateway host) | `istioctl analyze`, `proxy-config route` |
| ⑤ | 그래도 503이면 | response flag로 분류 |

**response flag 네 개만:**

| flag | 뜻 | 떠올릴 단계 |
|---|---|---|
| UH | 건강한(Ready) 엔드포인트가 없다 | ⑤ |
| UF | 대상 파드에 연결 실패 | ⑤·⑦ |
| UC | 연결이 중간에 끊겼다 | ⑥ (종료 중인 파드) |
| NR | 맞는 라우트가 없다 | ⑦ |

---

## 3. 처음에 틀렸던 것 — 다시 틀리지 않기 위해

내가 이 흐름을 처음 말로 설명했을 때의 실수다. 처음 공부하는 사람도 똑같이 틀리기 쉬운 지점이라 그대로 남긴다.

| 처음 한 말 | 바로잡은 말 | 왜 틀렸나 |
|---|---|---|
| "새 파드를 생성하도록 요청이 오는 상황인데…" | API 서버 → Deployment 컨트롤러 → RS 컨트롤러가 파드를 요청 | **주어가 없었다.** "누가?"를 스스로 묻지 않아서 사슬이 통째로 빠졌다 |
| "네임스페이스 라벨로 istio-init과 vault-agent-init을 넣는다" | Istio = 네임스페이스 라벨, Vault = 파드 어노테이션. 둘 다 init + 사이드카 | 웹훅마다 보는 대상이 다르다 |
| "istio-proxy를 통해 트래픽을 설정" | istio-init이 iptables로 **길만 깔아 둔다** | init 시점엔 프록시가 없다 |
| "8200은 트래픽 제한에서 제외" | 프록시 **우회** 대상에서 제외 | 막는 게 아니라 돌려보낸다 |
| "앱이 최종적으로 구동된다"에서 끝 | + readiness → EndpointSlice → Envoy 전파 → 트래픽 | Running ≠ 트래픽 수신 |
| (요청 흐름 없음) | Gateway → nginx → 메시 내부 → 백엔드 | 질문의 후반부를 잊었다 |
| 라벨 이름을 기억나는 대로 말함 | 확인한 이름만 말하고, 모르면 "Istio 주입 라벨"이라고 한다 | 틀린 이름 하나가 다른 설명의 신뢰도까지 깎는다 |

**공통 원인:** 나는 직접 만든 부분(CI, Helm 차트, Vault 주입 설정)은 정확하게 말하는데, **내가 만들지 않고 쿠버네티스가 알아서 해 주는 부분**에서 건너뛴다. 그래서 복기할 때는 "내가 설정한 것" 사이사이에 **"그 사이에 쿠버네티스의 누가?"**를 끼워 넣는 연습을 한다.

---

## 4. 5분 복기 루틴

읽고 끝내면 다음 주에 또 잊는다. 아래 세 개를 **안 보고** 한다. 읽기보다 꺼내기가 기억에 남기 때문이다.

### 4-1. 빈칸 채우기 (1분)

종이에 화살표만 그려 두고 채운다.

```
helm upgrade / ArgoCD
 → (________)에 저장
 → (________) 컨트롤러가 새 (____) 생성
 → (________) 컨트롤러가 Pod 요청
 → 저장 직전 (________) 웹훅: Istio는 (________), Vault는 (________)를 보고 주입
 → (________)가 (________) 기준으로 노드 배정
 → (________)이 init 실행: (________) → (________)   ※ 8200은 왜?
 → readiness: (____) 포트 경유
 → (________)에서 ready=true → (____)가 Envoy에 전파
 → maxSurge (_) / maxUnavailable (_)
 → 요청: LB → (________) → nginx → (________) → 백엔드
```

<details markdown="1">
<summary>정답</summary>

API 서버(etcd) → Deployment 컨트롤러 / ReplicaSet → ReplicaSet 컨트롤러 → mutating / 네임스페이스 라벨 / 파드 어노테이션 → 스케줄러 / requests → kubelet / istio-init → vault-agent-init (istio-init 시점엔 프록시가 없어서 Vault 요청이 막히므로 우회) → 15020 → EndpointSlice / istiod → 1 / 0 → Istio Ingress Gateway / 메시 내부(nginx 파드의 사이드카)

</details>

### 4-2. 소리 내어 말하기 (2분)

한 번 읽고, 덮고, 소리 내어 말한다. **막힌 곳이 다시 읽을 편이다.** (①~④에서 막히면 2편, ⑤~⑦에서 막히면 3편)

> 소스가 푸시되면 Jenkins가 빌드하고 Kaniko로 이미지를 만들어 레지스트리에 올립니다. 직접 배포는 Jenkins가 helm upgrade를 하고, GitOps 배포는 이미지 태그를 Git에 반영하면 ArgoCD가 동기화합니다.
>
> 여기서부터는 같습니다. API 서버가 변경을 받아 etcd에 저장하면, Deployment 컨트롤러가 새 ReplicaSet을 만들고, ReplicaSet 컨트롤러가 파드를 요청합니다. 저장 직전에 mutating 웹훅 두 개가 동작해서, 네임스페이스 라벨을 보고 Istio가 istio-init과 istio-proxy를, 파드 어노테이션을 보고 Vault가 vault-agent-init과 vault-agent를 넣습니다. 스케줄러가 requests 기준으로 노드를 고르면 kubelet이 init을 순서대로 실행합니다. istio-init이 iptables로 트래픽이 프록시로 가는 길을 깔아 두는데, 그 시점엔 프록시가 없어서 Vault 포트 8200은 우회 대상으로 뺐습니다. 이어서 vault-agent-init이 ServiceAccount 토큰으로 Vault에 로그인해 시크릿을 파일로 받아 오고, 그다음 앱이 뜹니다.
>
> readiness는 istio-proxy의 15020 포트를 거쳐 확인하고, 통과하면 EndpointSlice에서 ready가 되고 istiod가 Envoy들에 전파한 뒤에야 트래픽을 받습니다. maxSurge 1, maxUnavailable 0이라 새 파드가 준비된 뒤에야 옛 파드를 내립니다.
>
> 사용자 요청은 LB와 Ingress Gateway를 거쳐 nginx로 들어오고, API 요청은 nginx 파드의 사이드카가 메시 안에서 백엔드로 보냅니다. 백엔드는 외부에 직접 노출되지 않습니다.

### 4-3. 셀프 체크 (2분)

답을 먼저 말하고 펼친다.

<details markdown="1">
<summary>Q1. etcd에 직접 쓰는 컴포넌트는? (1편)</summary>

kube-apiserver뿐이다. 나머지는 모두 API 서버를 거친다. 인증·인가·검증을 한 곳에서 하기 위해서다.

</details>

<details markdown="1">
<summary>Q2. Deployment 컨트롤러는 ReplicaSet 컨트롤러에게 어떻게 일을 시키나? (1편)</summary>

시키지 않는다. API 서버에 ReplicaSet을 쓰면, ReplicaSet 컨트롤러가 watch로 보고 반응한다.

</details>

<details markdown="1">
<summary>Q3. replicas만 2→3으로 바꾸면 새 ReplicaSet이 생기나? (2편)</summary>

안 생긴다. 파드 템플릿이 바뀌어야(해시가 바뀌어야) 새 RS가 생긴다. replicas 변경은 기존 RS의 개수만 바꾼다.

</details>

<details markdown="1">
<summary>Q4. 웹훅 서버가 죽으면 증상은 어디에 보이나? (2편)</summary>

파드가 아니라 ReplicaSet 이벤트에 보인다(`FailedCreate`, `failed calling webhook`). 파드가 아예 저장되지 못하기 때문이다.

</details>

<details markdown="1">
<summary>Q5. 스케줄러는 requests와 limits 중 무엇을 보나? 왜? (2편)</summary>

requests. requests는 보장량이라 "이 노드에 들어갈 수 있나"의 기준이 되고, limits는 상한이라 배치와 관계없다.

</details>

<details markdown="1">
<summary>Q6. 8200을 우회시키지 않으면 파드는 어떤 상태로 멈추나? 왜? (2편)</summary>

`Init:1/2`. istio-init이 트래픽을 프록시로 가도록 바꿨는데, vault-agent-init이 도는 시점엔 프록시가 아직 없어서 Vault 요청이 실패하고 init이 끝나지 않는다.

</details>

<details markdown="1">
<summary>Q7. Running인데 트래픽을 못 받는 가장 흔한 이유와 첫 확인은? (3편)</summary>

readiness 미통과. `kubectl get pod`의 READY 칸(예: 2/3)을 먼저 보고, `describe`로 실패 이유를 본다.

</details>

<details markdown="1">
<summary>Q8. 배포할 때만 5xx가 잠깐 튄다. 어느 단계를 의심하나? (3편)</summary>

⑥ 종료. EndpointSlice 제거 전파와 SIGTERM이 동시에 일어나서, 전파가 끝나기 전에 앱이 먼저 죽는다. preStop 대기와 graceful shutdown을 본다.

</details>

<details markdown="1">
<summary>Q9. 사이드카가 있는 파드에서 나가는 요청의 대상 파드는 누가 고르나? (3편)</summary>

kube-proxy가 아니라 그 파드의 istio-proxy(Envoy)가, istiod에게 받은 엔드포인트 목록으로 고른다.

</details>

<details markdown="1">
<summary>Q10. 백엔드가 외부에 직접 노출되지 않는다는 걸 어떻게 확인하나? (3편)</summary>

백엔드 VirtualService에 `gateways` 필드가 없다(메시 내부 전용). 외부 진입은 Ingress Gateway에 연결된 웹서버 VirtualService뿐이다.

</details>

---

## 시리즈를 닫으며

| 편 | 한 줄 |
|---|---|
| (1) 큰 그림 | 모두 API 서버에 쓰고, 각자 지켜보다가, 자기 차례에 자기 일만 한다 |
| (2) 파드가 만들어지기까지 | 트리거 → 체인 → 웹훅 → 노드. istio-init은 길만 깔고, 8200은 우회 |
| (3) 트래픽을 받기까지 | Running ≠ Ready. 목록에 올라 전파돼야 요청이 온다. 백엔드는 메시 안에서만 |
| (4) 거꾸로 쓰기 | 증상표는 7단계를 거꾸로 읽은 것이다 |

잊었으면 1편의 그림 두 장(7단계, "누가?"의 사슬)부터 다시 본다. 그 두 장이 머리에 있으면 나머지는 다시 따라온다.

## 참고 문서

- [Kubernetes — Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Kubernetes — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes — Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Kubernetes — Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Kubernetes — EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
- [Istio — Sidecar Injection](https://istio.io/latest/docs/setup/additional-setup/sidecar-injection/)
- [Vault — Agent Sidecar Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector)
