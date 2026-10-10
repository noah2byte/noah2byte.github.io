---
title: "쿠버네티스 배포 흐름 한 번에 정리 (3) 트래픽을 받기까지 — Ready·교체·요청 흐름"
date: 2026-10-09 19:20:00 +0900
categories: [운영 이모저모, K8S]
pin: false
math: false
mermaid: false
---

## 이 편에서 얻을 것

**컨테이너가 떴는데 왜 아직 요청이 안 오는지**, 옛 파드는 언제 내려가는지, 그리고 **사용자 요청이 어떤 길로 백엔드 파드에 닿는지**를 설명할 수 있게 된다.

**1편 복습 한 줄:** 모두 API 서버에 쓰고, 각자 지켜보다가, 자기 차례에 자기 일만 한다.
**2편 복습 한 줄:** 트리거 → 체인 → 웹훅 → 노드. 컨테이너 다섯 개짜리 파드가 노드에서 떴다.

![단계 7개 중 ⑤~⑦](/assets/img/posts/k8s-deploy-flow/01-overview.svg){: w="960" h="520" }
_이 편은 아랫줄 ⑤~⑦이다_

### 이 편의 용어

| 용어 | 한 줄 설명 |
|---|---|
| **readinessProbe** | "이 컨테이너가 요청을 받을 준비가 됐나"를 kubelet이 주기적으로 확인하는 설정 |
| **Running vs Ready** | Running = 컨테이너 프로세스가 떠 있다. Ready = readiness까지 통과했다. **트래픽은 Ready에만 간다** |
| **istiod / Envoy** | istiod는 Istio의 두뇌(설정 배포), Envoy는 각 사이드카(`istio-proxy`)와 Gateway 안에서 실제로 트래픽을 나르는 프록시 |
| **SIGTERM / preStop** | SIGTERM은 "이제 종료해라" 신호. preStop은 SIGTERM 직전에 실행되는 훅(보통 몇 초 대기) |

---

## ⑤ Ready — Running이라고 트래픽을 받는 게 아니다

**한 줄:** 컨테이너가 떠도(Running) readiness를 통과해야(Ready) 비로소 트래픽 대상 목록에 들어간다.

![Running ≠ 트래픽 수신, Ready가 되기까지](/assets/img/posts/k8s-deploy-flow/05-ready-chain.svg){: w="960" h="450" }
_보라색 글씨가 각 화살표를 움직이는 주체다. 여기서도 서로 부르지 않고 각자 watch한다 (1편 규칙 3)_

| 누가 | 무엇을 보고 | 무엇을 한다 |
|---|---|---|
| kubelet | readinessProbe 설정 | 주기적으로 확인 → Pod의 Ready 조건 갱신 |
| EndpointSlice 컨트롤러 | Pod의 Ready 조건 | Service의 EndpointSlice에 그 파드의 `ready` 값을 반영 |
| istiod | EndpointSlice 변화 | 모든 Envoy(Gateway, 각 사이드카)에 새 엔드포인트 목록 전파 |

- **readiness가 왜 15020 포트로 가나:** Istio가 앱의 HTTP probe를 자동으로 바꿔 쓴다. kubelet은 앱에 직접 묻지 않고 istio-proxy의 15020 포트(`/app-health/<컨테이너>/readyz`)에 묻고, 프록시가 앱에 대신 묻는다. mTLS가 걸린 메시에서는 kubelet이 앱 포트에 바로 닿기 어렵기 때문이다
- **정확히는:** 준비 안 된 파드도 EndpointSlice에 들어가 있을 수 있다. 다만 `ready: false`로 표시되고, 트래픽은 `ready: true`인 곳으로만 간다. 그래서 확인할 때는 "IP가 있나"가 아니라 **"ready가 true인가"**를 본다
- **사이드카가 있으면 kube-proxy가 아니라 Envoy가 파드를 고른다.** 호출하는 쪽 파드의 istio-proxy가, istiod에게 받은 엔드포인트 목록으로 대상 파드를 직접 정한다

```bash
kubectl get pod -n app     # READY 칸이 3/3 인가?
kubectl get endpointslice -n app -l kubernetes.io/service-name=api-backend -o yaml | grep -A3 conditions
```

---

## ⑥ 교체 — 새 파드가 준비된 뒤에 옛 파드를 내린다

**한 줄:** maxSurge / maxUnavailable은 "새 파드가 Ready가 된 뒤 옛 파드를 언제, 몇 개씩 내리느냐"의 규칙이다.

![롤링 업데이트 maxSurge 1 / maxUnavailable 0](/assets/img/posts/k8s-deploy-flow/06-rolling-update.svg){: w="1000" h="470" }
_EP(엔드포인트)에 들어 있는 파드가 2개 밑으로 떨어지는 순간이 없다_

| 설정 (파드 2개 기준) | 의미 | 트레이드오프 |
|---|---|---|
| maxSurge 1 | 원래 수보다 1개까지 더 띄운다 (잠시 3개) | 노드에 파드 1개분 여유가 필요하다 |
| maxUnavailable 0 | Ready 파드가 2개 밑으로 내려가지 않는다 | 용량은 안전하지만 교체가 느리다 |

- **누가 하나:** Deployment 컨트롤러다. 새 RS의 파드가 Ready가 된 걸 보고 옛 RS를 하나 줄인다. 2편의 "RS가 두 개"가 여기서 쓰인다

### 종료 순간의 함정

옛 파드를 지우면 두 가지 일이 **동시에** 시작된다.

| 동시에 일어나는 일 | 걸리는 시간 |
|---|---|
| ① EndpointSlice에서 빠짐 → istiod → 모든 Envoy에 전파 | 전파에 시간이 걸린다 |
| ② kubelet이 preStop 실행 → SIGTERM | 바로 시작된다 |

①의 전파가 끝나기 전에 앱이 먼저 죽으면, 아직 그 파드로 보낸 요청이 실패한다. 그래서 **preStop으로 몇 초 기다리고**, 앱은 SIGTERM을 받으면 받던 요청을 마저 처리하고 끝내야(graceful shutdown) 한다.

- **왜 "동시에"인가:** 1편 규칙 3 때문이다. kubelet과 EndpointSlice 컨트롤러는 서로를 기다리지 않는다. 각자 "파드 삭제"를 watch로 보고 각자 움직인다
- 즉 ⑤의 사슬이 **거꾸로** 도는 것이다. 들어올 때는 "Ready → 목록 추가 → 전파", 나갈 때는 "목록 제거 → 전파"와 "종료"가 경주한다

---

## ⑦ 요청 흐름 — 사용자 요청이 백엔드 파드에 닿기까지

**한 줄:** 외부 요청은 Gateway를 거쳐 웹서버(nginx)까지만 들어오고, 백엔드는 메시 안에서만 호출된다.

![사용자 요청이 백엔드 파드에 닿기까지](/assets/img/posts/k8s-deploy-flow/07-request-flow.svg){: w="1000" h="520" }
_빨간 점선: 외부에서 백엔드로 직접 오는 길은 없다_

| 단계 | 누가 | 하는 일 |
|---|---|---|
| 1 | 클라우드 LB | 외부 진입점 |
| 2 | Istio Ingress Gateway (Envoy) | Gateway + VirtualService 규칙으로 웹서버로 보낸다 |
| 3 | 웹서버 파드의 istio-proxy → nginx | 화면 요청은 정적 파일로 응답, API 요청은 conf 분기로 `api-backend.app.svc`로 넘긴다 |
| 4 | nginx 파드의 istio-proxy | 나가는 요청을 가로채 메시 내부 VirtualService를 적용하고, ⑤에서 받은 목록 중 Ready인 백엔드 파드를 고른다 |
| 5 | 백엔드 파드의 istio-proxy → 앱 | 요청 처리 |

- **⑤와 연결:** 4단계에서 "Ready인 파드를 고른다"가 바로 ⑤에서 istiod가 전파한 목록이다. 배포 흐름과 요청 흐름은 여기서 만난다
- **보안 포인트:** 백엔드 VirtualService에는 Gateway가 연결돼 있지 않다. 외부에서 백엔드로 바로 오는 길이 없고 nginx를 통해서만 호출된다 → **공격 표면이 줄어든다.** 같은 흐름도 이 한 문장이 있으면 보안 관점의 설명이 된다

---

## 3편 한 장 요약

| 단계 | 누가 | 한 줄 |
|---|---|---|
| ⑤ Ready | kubelet → EndpointSlice 컨트롤러 → istiod | readiness(15020) 통과 → `ready: true` → 모든 Envoy에 전파. **Running ≠ 트래픽** |
| ⑥ 교체 | Deployment 컨트롤러 | maxSurge 1 / maxUnavailable 0. 종료 때는 목록 제거와 SIGTERM이 동시 → preStop |
| ⑦ 요청 | LB → Gateway → nginx → 사이드카 → 백엔드 | 백엔드는 메시 안에서만 호출된다. 외부 미노출 |

**시리즈 1~3편을 한 문장으로:**

> 배포 도구가 API 서버에 변경을 쓰면, 컨트롤러들이 차례로 그걸 보고 새 파드를 장부에 올리고, 웹훅이 사이드카를 끼우고, 스케줄러와 kubelet이 실제로 띄운다. readiness를 통과하면 목록에 올라 Envoy들에 전파되고, 그때부터 Gateway → nginx → 메시 안을 거쳐 온 요청을 받는다.

<details markdown="1">
<summary>읽고 나서 바로 확인 — 배포할 때만 5xx가 잠깐 튄다. 어느 단계를 의심하나?</summary>

⑥ 종료. EndpointSlice 제거 전파와 SIGTERM이 동시에 일어나서, 전파가 끝나기 전에 앱이 먼저 죽는다. preStop 대기와 graceful shutdown을 확인한다.

</details>

**다음 편:** (4) 장애 때 거꾸로 쓰기 + 복기 루틴 — 7단계를 거꾸로 따라가 원인을 찾는 법과, 5분 복기
