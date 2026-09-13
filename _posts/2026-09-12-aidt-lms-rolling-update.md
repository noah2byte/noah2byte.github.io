---
title: "백엔드/웹서버 실제 설정으로 보는 롤링 업데이트"
date: 2026-09-12 23:00:00 +0900
categories: [운영 이모저모, K8S]
pin: false
math: false
mermaid: false
---

## 왜 이 글을 쓰는가

롤링 업데이트는 어디서나 "구버전 파드를 순차적으로 신버전으로 교체하는 것"이라고 설명한다. 그런데 이 한 줄짜리 설명은 실제 운영에서 별 도움이 안 된다. 진짜 궁금한 건 "우리 시스템의 `maxSurge`, `maxUnavailable`, Probe 설정값으로 실제 배포 순간에 무슨 일이 벌어지는가"다. 이 글은 백엔드(`aidt-api-lm`)와 웹서버(nginx) 두 차트의 **실측 설정값**을 기준으로 그 과정을 그대로 재구성한다. 현재 직장에 구성된 내용을 다시 한번 이 포스팅으로 정리함으로써, 나중에 복기하고 보다 나은 구성으로 고도화 가능할 수 있는 기반이 되도록 한다.

## 두 차트의 실측 설정 대비

| 항목 | 백엔드 (prod) | nginx |
|---|---|---|
| strategy | RollingUpdate | RollingUpdate |
| maxSurge | 1 | 0 |
| maxUnavailable | 0 | 1 |
| minReadySeconds | 5 | 5 |
| replicas 관리 주체 | HPA (min=max=1) | HPA (min=3, max=5) |
| readinessProbe | httpGet `/healthcheck:8080`, period 5s, timeout 1s, failureThreshold 5 | 없음 |
| livenessProbe | 동일 엔드포인트, initialDelaySeconds=60s | 없음 |

두 값이 완전히 반대로 설정된 이유부터 짚고 가야 한다. 백엔드는 `maxSurge=1, maxUnavailable=0`을 써서 "잠깐 리소스를 더 쓰더라도 절대 트래픽을 못 받는 파드가 있으면 안 된다"는 쪽을 선택했다. 반면 nginx는 `maxSurge=0, maxUnavailable=1`이라 "새 파드를 추가로 띄우지 않고, 기존 파드 중 하나를 먼저 내리고 그 자리에 새 파드를 채운다"는 방식이다. 이런 선택을 한 사유는 nginx가 HPA로 3~5개 replica를 이미 넉넉히 굴리고 있어서, 순간적으로 하나 빠져도 나머지가 트래픽을 받아낼 수 있다고 판단했기 때문으로 보인다. 반대로 백엔드는 replica가 사실상 1개(HPA min=max=1)라 하나라도 빠지면 바로 서비스 중단이 되므로, 리소스를 더 쓰더라도 무중단 쪽을 택할 수밖에 없는 구조다.

<svg width="100%" viewBox="0 0 680 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="백엔드와 nginx의 롤링 업데이트 전략 비교">
  <rect x="40" y="30" width="280" height="150" rx="10" fill="#EAF3DE" stroke="#639922" stroke-width="1"/>
  <text x="180" y="55" text-anchor="middle" font-size="14" font-weight="600" fill="#27500A">백엔드 (prod)</text>
  <text x="180" y="80" text-anchor="middle" font-size="13" fill="#3B6D11">maxSurge: 1</text>
  <text x="180" y="100" text-anchor="middle" font-size="13" fill="#3B6D11">maxUnavailable: 0</text>
  <text x="180" y="130" text-anchor="middle" font-size="12" fill="#3B6D11">먼저 새로 띄우고</text>
  <text x="180" y="148" text-anchor="middle" font-size="12" fill="#3B6D11">준비되면 구버전 종료</text>
  <text x="180" y="168" text-anchor="middle" font-size="11" fill="#5F5E5A">(replica 1개 · 무중단 최우선)</text>

  <rect x="360" y="30" width="280" height="150" rx="10" fill="#E1F5EE" stroke="#1D9E75" stroke-width="1"/>
  <text x="500" y="55" text-anchor="middle" font-size="14" font-weight="600" fill="#04342C">nginx</text>
  <text x="500" y="80" text-anchor="middle" font-size="13" fill="#0F6E56">maxSurge: 0</text>
  <text x="500" y="100" text-anchor="middle" font-size="13" fill="#0F6E56">maxUnavailable: 1</text>
  <text x="500" y="130" text-anchor="middle" font-size="12" fill="#0F6E56">구버전 하나 먼저 종료 후</text>
  <text x="500" y="148" text-anchor="middle" font-size="12" fill="#0F6E56">그 자리에 신버전 채움</text>
  <text x="500" y="168" text-anchor="middle" font-size="11" fill="#5F5E5A">(replica 3~5개 · 리소스 절약 우선)</text>
</svg>

## 1. 백엔드 시뮬레이션 — 실제로 벌어지는 일

HPA가 `minReplicas: maxReplicas: 1`로 고정돼 있어서 사실상 단일 Pod로 운영한다. 그런데 `maxUnavailable=0`이 무중단을 강제하니, 이 조합이 실제로 어떻게 굴러가는지 단계 하나하나를 쪼개서 본다.

### 1단계 — 배포 요청이 API 서버에 접수된다

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="1단계 배포 요청 접수">
  <rect x="30" y="45" width="140" height="50" rx="8" fill="#444441"/>
  <text x="100" y="75" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">Jenkins</text>
  <line x1="170" y1="70" x2="240" y2="70" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#a1)"/>
  <text x="205" y="60" text-anchor="middle" font-size="10" fill="#5F5E5A">helm upgrade</text>
  <rect x="240" y="45" width="160" height="50" rx="8" fill="#0C447C"/>
  <text x="320" y="70" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">API 서버</text>
  <text x="320" y="86" text-anchor="middle" font-size="10" fill="#B5D4F4">Deployment PATCH</text>
  <line x1="400" y1="70" x2="470" y2="70" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#a1)"/>
  <rect x="470" y="45" width="180" height="50" rx="8" fill="#085041"/>
  <text x="560" y="68" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">Deployment Controller</text>
  <text x="560" y="86" text-anchor="middle" font-size="10" fill="#9FE1CB">새 ReplicaSet(v2) 생성</text>
  <defs><marker id="a1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5"/></marker></defs>
  <text x="340" y="130" text-anchor="middle" font-size="12" fill="#444441">이 시점 v1은 그대로 Ready 상태로 트래픽을 받고 있다</text>
</svg>

Jenkins가 커밋 해시 기반 새 태그로 values를 override해서 `helm upgrade --install`을 실행하면, 실제로 바뀌는 건 클러스터 안의 파일이 아니라 **Deployment 오브젝트의 Pod Template 필드**다. API 서버가 이 변경을 받아들이는 순간 Deployment Controller가 "템플릿 해시가 달라졌다"는 걸 감지하고, 새 해시를 가진 ReplicaSet(v2)을 하나 만든다. 이 시점엔 아직 v2 파드는 존재하지 않고 ReplicaSet 오브젝트만 생긴 상태다 — v1은 아무 영향 없이 계속 트래픽을 받는다.

### 2단계 — surge 자리로 v2 파드가 스케줄링된다

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="2단계 surge 파드 스케줄링">
  <rect x="40" y="45" width="140" height="50" rx="8" fill="#0C447C"/>
  <text x="110" y="75" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="270" y="45" width="140" height="50" rx="8" fill="#854F0B"/>
  <text x="340" y="70" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v2 [Pending]</text>
  <text x="340" y="86" text-anchor="middle" font-size="10" fill="#FAC775">스케줄러 노드 배정 중</text>
  <line x1="410" y1="70" x2="480" y2="70" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#a2)"/>
  <rect x="480" y="45" width="160" height="50" rx="8" fill="#854F0B"/>
  <text x="560" y="70" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">kubelet</text>
  <text x="560" y="86" text-anchor="middle" font-size="10" fill="#FAC775">이미지 pull 시작</text>
  <defs><marker id="a2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5"/></marker></defs>
  <text x="340" y="130" text-anchor="middle" font-size="12" fill="#444441">desired(1) + maxSurge(1) = 최대 2개까지 허용되는 순간</text>
</svg>

`maxUnavailable=0`이라 v1을 먼저 내릴 수 없다. 대신 `maxSurge=1`이 있어서 desired(1) + 1 = 최대 2개까지 허용되므로, v2 파드를 기존 v1을 그대로 둔 채로 "추가로" 하나 더 만든다. kube-scheduler가 이 파드를 어느 노드에 배치할지 결정하고(노드 리소스 여유 확인), 결정되면 그 노드의 kubelet이 이미지를 레지스트리에서 pull하기 시작한다. 이 순간부터 클러스터는 순간적으로 리소스를 평소의 2배 쓴다 — nginx 대비 넉넉하게 리소스를 잡아둔 이유이기도 하다.

### 3단계 — init 컨테이너가 순차 실행되고, probe는 아직 시작 전이다

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="3단계 init 컨테이너 실행">
  <rect x="40" y="45" width="140" height="50" rx="8" fill="#0C447C"/>
  <text x="110" y="75" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="270" y="30" width="380" height="80" rx="8" fill="none" stroke="#854F0B" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="290" y="50" font-size="11" fill="#854F0B">v2 Pod (Running, NotReady)</text>
  <rect x="290" y="58" width="100" height="30" rx="5" fill="#854F0B"/>
  <text x="340" y="78" text-anchor="middle" font-size="10" fill="#FFFFFF">init: vault-agent</text>
  <line x1="390" y1="73" x2="420" y2="73" stroke="#854F0B" stroke-width="1.5" marker-end="url(#a3)"/>
  <rect x="420" y="58" width="100" height="30" rx="5" fill="#B4B2A9"/>
  <text x="470" y="78" text-anchor="middle" font-size="10" fill="#2C2C2A">메인 컨테이너</text>
  <line x1="520" y1="73" x2="545" y2="73" stroke="#854F0B" stroke-width="1.5" marker-end="url(#a3)"/>
  <text x="600" y="78" text-anchor="middle" font-size="10" fill="#791F1F">probe 대기중</text>
  <defs><marker id="a3" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#854F0B" stroke-width="1.5"/></marker></defs>
  <text x="340" y="130" text-anchor="middle" font-size="12" fill="#444441">initialDelaySeconds=50s가 지나야 첫 readinessProbe 호출</text>
</svg>

파드가 뜬다고 컨테이너들이 동시에 시작하는 게 아니다. init 컨테이너(vault-agent-init 등)가 **순서대로 하나씩** 완료돼야 메인 컨테이너가 시작된다. 메인 컨테이너가 시작해도 `initialDelaySeconds=50s`가 지나기 전까지는 kubelet이 readinessProbe 자체를 호출하지 않는다 — 이 구간에서 파드 상태는 `Running`이지만 `Ready`는 아니다. 대기 시간을 이렇게 넉넉히 잡은 사유는, 사이드카/init 컨테이너가 완전히 준비되기 전에 트래픽을 받아버리는 걸 막기 위해서다.

### 4단계 — probe 성공, EndpointSlice에 등록된다

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="4단계 readiness probe 성공">
  <rect x="40" y="45" width="140" height="50" rx="8" fill="#0C447C"/>
  <text x="110" y="75" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="270" y="45" width="140" height="50" rx="8" fill="#085041"/>
  <text x="340" y="70" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <text x="340" y="86" text-anchor="middle" font-size="10" fill="#9FE1CB">probe 성공</text>
  <line x1="410" y1="70" x2="480" y2="70" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#a4)"/>
  <rect x="480" y="45" width="160" height="50" rx="8" fill="#085041"/>
  <text x="560" y="70" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">EndpointSlice</text>
  <text x="560" y="86" text-anchor="middle" font-size="10" fill="#9FE1CB">v2 IP 등록됨</text>
  <defs><marker id="a4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5"/></marker></defs>
  <text x="340" y="130" text-anchor="middle" font-size="12" fill="#444441">minReadySeconds=5초 경과 후 v1 · v2 둘 다 동시에 트래픽 수신</text>
</svg>

50초 뒤 첫 readinessProbe가 성공하면 kubelet이 파드를 Ready로 표시하고, 이 정보가 API 서버를 거쳐 EndpointSlice 컨트롤러에 전달돼 v2의 IP가 Service의 EndpointSlice에 추가된다. 다만 바로 "Available"로 카운트되는 건 아니고 `minReadySeconds=5초`가 더 지나야 한다 — 이 짧은 유예 시간은 probe가 우연히 한 번만 성공하고 곧바로 불안정해지는 걸 걸러내기 위한 안전판이다. 이 순간부터 v1과 v2가 **동시에** 실제 트래픽을 나눠 받는다.

### 5단계 — 조건이 충족되어 구버전이 종료된다

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="5단계 구버전 종료">
  <rect x="40" y="45" width="140" height="50" rx="8" fill="#791F1F"/>
  <text x="110" y="70" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Terminating]</text>
  <text x="110" y="86" text-anchor="middle" font-size="10" fill="#F7C1C1">SIGTERM 전송됨</text>
  <rect x="270" y="45" width="140" height="50" rx="8" fill="#085041"/>
  <text x="340" y="75" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <line x1="410" y1="70" x2="480" y2="70" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#a5)"/>
  <rect x="480" y="45" width="160" height="50" rx="8" fill="#791F1F"/>
  <text x="560" y="70" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF">terminationGrace</text>
  <text x="560" y="86" text-anchor="middle" font-size="10" fill="#F7C1C1">최대 30초 대기</text>
  <defs><marker id="a5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5"/></marker></defs>
  <text x="340" y="130" text-anchor="middle" font-size="12" fill="#444441">EndpointSlice에서는 즉시 제거 — 새 요청은 v1로 안 감</text>
</svg>

v2가 Ready가 됨으로써 이제 "정상 replica 수(1개)가 항상 유지된다"는 `maxUnavailable=0` 조건이 만족된 상태다. 그러면 Deployment Controller가 v1에 SIGTERM을 보낸다. 이때 v1은 **두 가지가 동시에 일어난다** — ① EndpointSlice에서 즉시 제거되어 새로운 요청은 더 이상 v1로 라우팅되지 않고, ② 프로세스 자체는 `terminationGracePeriodSeconds=30초` 동안 살아남아 이미 받은 요청을 마저 처리한다. 이 둘을 분리해두는 사유는 "새 요청 차단"과 "기존 요청 완료"가 동시에 되도록 해서 커넥션이 중간에 끊기지 않게 하기 위해서다.

### 6단계 — 최종 상태

<svg width="100%" viewBox="0 0 680 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="6단계 최종 상태">
  <rect x="270" y="35" width="140" height="50" rx="8" fill="#085041"/>
  <text x="340" y="65" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <text x="340" y="105" text-anchor="middle" font-size="12" fill="#444441">v1 완전히 사라지고 v2만 남는다 — 이 사이 트래픽 끊김 없음</text>
</svg>

v1의 grace period가 끝나면 컨테이너가 완전히 종료되고 ReplicaSet에서도 제거된다. replica가 1개인 상태로 배포 시작 전과 배포 후가 동일하게 유지되면서, 그 사이 트래픽은 한 번도 끊기지 않았다 — 대신 짧은 구간 동안 리소스를 2배 쓰는 걸 감수한 결과다.

**readinessProbe가 계속 실패하면 어떻게 되는가.** `failureThreshold=5, periodSeconds=5`라 약 25초 연속 실패하면 v2는 계속 NotReady 상태로 남는다. 이러면 4단계가 영원히 안 일어나고, `maxUnavailable=0`이라 v1도 못 내리고 `maxSurge=1`을 이미 다 썼으니 v2를 더 늘리지도 못한다. 결과적으로 **서비스 자체는 v1이 계속 받아내서 정상이지만, 배포는 그 자리에서 멈춘다** — Deployment가 `Progressing` 상태에 갇혀서 안 끝나는 상황이 바로 이거다.



## 2. nginx — 두 가지 서로 다른 배포 경로가 있다는 게 핵심

nginx는 한 가지가 아니라 **두 가지 완전히 다른 배포 경로**를 갖고 있다는 걸 먼저 짚어야 한다. 이 구분을 모르면 "nginx도 롤링 업데이트 되겠지"라고 오해하기 쉽다.

<svg width="100%" viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="nginx의 두 가지 배포 경로 비교">
  <rect x="40" y="30" width="280" height="200" rx="10" fill="#E1F5EE" stroke="#1D9E75"/>
  <text x="180" y="55" text-anchor="middle" font-size="13" font-weight="600" fill="#04342C">nginx 서버 자체 변경</text>
  <text x="180" y="72" text-anchor="middle" font-size="11" fill="#5F5E5A">(설정, 베이스 이미지)</text>
  <text x="180" y="100" text-anchor="middle" font-size="12" fill="#0F6E56">Kaniko 이미지 빌드</text>
  <text x="180" y="120" text-anchor="middle" font-size="12" fill="#0F6E56">→ helm upgrade</text>
  <text x="180" y="140" text-anchor="middle" font-size="12" fill="#0F6E56">→ Deployment spec 변경</text>
  <text x="180" y="160" text-anchor="middle" font-size="12" fill="#0F6E56">→ 표준 RollingUpdate 발동</text>
  <text x="180" y="195" text-anchor="middle" font-size="11" fill="#5F5E5A">maxSurge:0 / maxUnavailable:1</text>
  <text x="180" y="212" text-anchor="middle" font-size="11" fill="#5F5E5A">경로를 그대로 탐</text>

  <rect x="360" y="30" width="280" height="200" rx="10" fill="#FAEEDA" stroke="#BA7517"/>
  <text x="500" y="55" text-anchor="middle" font-size="13" font-weight="600" fill="#412402">정적 파일(dist) 변경</text>
  <text x="500" y="72" text-anchor="middle" font-size="11" fill="#5F5E5A">(프론트엔드 배포)</text>
  <text x="500" y="100" text-anchor="middle" font-size="12" fill="#854F0B">npm build</text>
  <text x="500" y="120" text-anchor="middle" font-size="12" fill="#854F0B">→ kubectl cp로</text>
  <text x="500" y="140" text-anchor="middle" font-size="12" fill="#854F0B">떠 있는 파드에 직접 복사</text>
  <text x="500" y="160" text-anchor="middle" font-size="12" fill="#854F0B">→ Pod Spec 변경 없음</text>
  <text x="500" y="195" text-anchor="middle" font-size="11" fill="#791F1F">RollingUpdate 개념 자체가</text>
  <text x="500" y="212" text-anchor="middle" font-size="11" fill="#791F1F">적용되지 않음</text>
</svg>

**왜 이렇게 나뉘어 있는가.** "무엇이 바뀌었는가"에 따라 배포의 무게를 다르게 가져가려는 설계다. 코드나 실행 환경이 바뀌면 이미지 자체가 바뀌어야 하니 Kaniko + Helm + RollingUpdate라는 표준 경로를 그대로 태우고, 반대로 빌드 결과물(정적 파일)만 바뀌는 경우엔 이미지를 새로 굽는 무거운 과정을 생략하고 `kubectl cp`로 파일만 갈아 끼운다. 가벼운 대신 표준 롤백 수단(`kubectl rollout undo`)을 못 쓴다는 트레이드오프를 함께 가져가는 선택이다.

### 2-1. nginx 서버 자체가 바뀔 때 — 실제 RollingUpdate 동작

`maxSurge=0, maxUnavailable=1`이라 백엔드와 정반대 순서로 진행된다. replica는 HPA min=3 기준으로 본다.

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="nginx 1단계 초기 상태">
  <rect x="80" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="140" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="220" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="280" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="360" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="420" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <text x="280" y="130" text-anchor="middle" font-size="12" fill="#444441">1단계 — 배포 전, v1 파드 3개가 정상적으로 트래픽을 받는 상태</text>
</svg>

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="nginx 2단계 구버전 먼저 종료">
  <rect x="80" y="45" width="120" height="50" rx="8" fill="#791F1F"/>
  <text x="140" y="70" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF">v1 [Terminating]</text>
  <rect x="220" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="280" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="360" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="420" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <text x="280" y="130" text-anchor="middle" font-size="12" fill="#444441">2단계 — maxUnavailable=1 한도까지 v1 하나를 먼저 종료 (정상 replica 2개로 감소)</text>
</svg>

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="nginx 3단계 신버전 즉시 Ready">
  <rect x="80" y="45" width="120" height="50" rx="8" fill="#085041"/>
  <text x="140" y="70" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <text x="140" y="86" text-anchor="middle" font-size="9" fill="#9FE1CB">probe 없이 즉시</text>
  <rect x="220" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="280" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <rect x="360" y="45" width="120" height="50" rx="8" fill="#0C447C"/>
  <text x="420" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v1 [Ready]</text>
  <text x="280" y="130" text-anchor="middle" font-size="12" fill="#791F1F">3단계 — readinessProbe가 없어 컨테이너 시작과 동시에 Ready 판정, 트래픽 즉시 수신</text>
</svg>

<svg width="100%" viewBox="0 0 680 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="nginx 4단계 최종 상태">
  <rect x="80" y="45" width="120" height="50" rx="8" fill="#085041"/>
  <text x="140" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <rect x="220" y="45" width="120" height="50" rx="8" fill="#085041"/>
  <text x="280" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <rect x="360" y="45" width="120" height="50" rx="8" fill="#085041"/>
  <text x="420" y="75" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">v2 [Ready]</text>
  <text x="280" y="130" text-anchor="middle" font-size="12" fill="#444441">4단계 — 이 과정이 replica 수만큼 하나씩 반복되어 전체가 v2로 교체된다</text>
</svg>

각 단계를 사유와 함께 풀면 이렇다.

1. **새 ReplicaSet(v2)이 생성되지만, `maxSurge=0`이라 먼저 추가로 띄우는 일은 없다.** 백엔드와 달리 여유 리소스를 쓰지 않는 쪽을 선택한 것이다.
2. **`maxUnavailable=1`이 허용하는 한도까지 구버전(v1) 파드 하나를 먼저 Terminating 상태로 만든다.** HPA가 min=3이므로 이 순간 정상 replica는 2개로 줄어든다 — 백엔드였다면 절대 허용 안 되는 상태지만, nginx는 replica가 여유 있어 감수 가능하다고 판단한 것으로 보인다.
3. **v1 파드가 완전히 빠진 자리에 v2 파드가 새로 뜬다.** 여기서 결정적인 차이가 나온다 — **nginx Deployment에는 readinessProbe가 없다.** 즉 v2 컨테이너가 시작되자마자(프로세스가 뜨는 순간) 바로 Ready로 간주돼 트래픽을 받기 시작한다. 컨테이너 시작과 "실제로 요청을 처리할 준비가 됐는가" 사이에 별도 확인 절차가 없는 셈이다.
4. **이 과정이 replica 수만큼 반복되며 전체가 v2로 교체된다.**

**probe가 없다는 게 왜 문제가 될 수 있는가.** 백엔드처럼 init 컨테이너(vault-agent 등)를 기다릴 필요가 nginx엔 상대적으로 적어서 지금까지는 큰 문제 없이 운영돼왔을 가능성이 높다. 다만 nginx 설정 리로드나 초기화에 아주 짧은 시간이라도 걸린다면, 그 찰나의 요청이 실패로 이어질 여지가 이론상 남아있다. Probe를 추가하는 게 왜 필요한지 판단할 때 참고할 지점이다.

### 2-2. 정적 파일(dist)만 바뀔 때 — RollingUpdate가 아예 발동하지 않음

`kubectl cp`는 이미 떠 있는 컨테이너의 파일시스템에 파일을 밀어넣는 동작이라, Deployment의 Pod Template 자체를 건드리지 않는다. 그래서 이 경로는 롤링 업데이트라는 개념이 아예 적용되지 않는다 — 파드 재시작도, ReplicaSet 교체도 일어나지 않고 그냥 실행 중인 파드 안의 파일 하나가 바뀔 뿐이다.

여기서 짚고 넘어가야 할 리스크가 있다. `kubectl cp`로 넣은 파일은 컨테이너의 **ephemeral layer**에만 존재한다. 만약 다른 이유로(리소스 제한 변경, 노드 재스케줄링 등) 파드가 재시작되면, 새로 뜬 파드에는 이 파일이 없다 — 이 부분이 이 배포 방식의 가장 큰 구조적 약점으로, `kubectl cp` 방식을 쓸 때는 반드시 인지하고 있어야 하는 지점이다.

## 부록 — 개념 자체 복기

실측값 시뮬레이션만 보면 나중에 "그래서 maxSurge랑 maxUnavailable이 정확히 뭐였지"가 다시 헷갈릴 수 있어서, 개념 자체를 처음부터 다시 정리해둔다.

### maxSurge / maxUnavailable가 정확히 뭘 통제하는가

Deployment의 `strategy.rollingUpdate` 아래에 두 값이 들어간다.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

- **maxSurge**: 원하는 replica 수보다 순간적으로 **최대 몇 개까지 더** 띄울 수 있는가. replica가 3이고 maxSurge=1이면, 롤링 업데이트 도중 최대 4개까지 동시에 떠 있을 수 있다는 뜻이다. 신규 파드를 먼저 띄우고 그다음 구버전을 내리는 순서로 진행된다.
- **maxUnavailable**: 롤링 업데이트 도중 동시에 몇 개까지 "서비스 불가" 상태여도 되는가. 0으로 두면 "항상 정상 replica 수를 유지한 채로" 교체하라는 뜻이라 무중단에 가까워진다.

![롤링 업데이트 5단계 진행 과정](/assets/img/posts/rolling-update-flow.png)
_maxSurge=1, maxUnavailable=0 조합에서 새 파드가 추가로 뜨고, Ready가 확인된 뒤에야 구 파드가 내려가는 흐름_

이 둘의 조합에 따라 진행 순서 자체가 달라진다.

- **maxSurge > 0, maxUnavailable = 0** (백엔드): 새 파드를 먼저 추가로 띄우고, Ready가 확인되면 그제서야 구 파드를 내린다. 순간적으로 리소스를 더 쓰지만 트래픽 끊김이 없다.
- **maxSurge = 0, maxUnavailable > 0** (nginx): 추가로 띄우지 않고, 구 파드를 먼저 내린 다음 그 자리에 새 파드를 채운다. 리소스는 그대로 쓰지만 그 순간만큼은 정상 replica 수가 줄어든다.

### Readiness Probe가 왜 "게이트" 역할을 하는가

새 파드가 뜬다고 바로 트래픽을 받는 게 아니다. Deployment 컨트롤러는 **Readiness Probe가 성공할 때까지 다음 단계로 넘어가지 않는다** — 이게 롤링 업데이트에서 가장 중요한 지점이다. 파드 상태가 `Running`이어도 `Ready`가 아니면 Service의 EndpointSlice에 등록되지 않아서 트래픽을 못 받는다.

그래서 init 컨테이너(vault-agent-init 등)나 사이드카(istio-proxy 등)가 붙는 파드는, 그것들이 전부 초기화될 때까지 메인 컨테이너의 Readiness가 통과되지 않도록 `initialDelaySeconds`를 여유 있게 잡아두는 게 안전하다. 이 값이 너무 짧으면, 사이드카가 준비되기 전에 트래픽을 받아버리는 상황이 생길 수 있다.

**Probe가 계속 실패하면 롤링 업데이트 자체가 멈춘다.** `maxUnavailable=0`인 상태에서 새 파드가 계속 NotReady면, 구 파드를 못 내리고(무중단 조건 위반이라서) 새 파드를 더 늘리지도 못한다(`maxSurge`를 이미 다 썼으므로). 서비스는 구 버전이 계속 받아내서 정상이지만, 배포 자체는 `Progressing` 상태에 갇혀서 끝나지 않는다.

### Topology Spread Constraint (maxSkew) — 롤링 업데이트와는 별개의 개념

maxSurge/maxUnavailable이 "언제 몇 개씩 뜨고 내리는가"를 정하는 규칙이라면, maxSkew는 **"그 파드들을 어느 노드에 배치할 것인가"**를 정하는 완전히 다른 레이어의 규칙이다. 롤링 업데이트 중 새 파드가 스케줄링될 때 이 제약도 함께 참조된다.

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: aidt-api-lm
```

**비유로 이해하면 쉽다.** 학생 10명을 조 A, B, C 세 개에 나눠 앉힐 때 "한 조에 몰빵하지 말고 최대한 비슷하게 나눠라"는 규칙과 같다. maxSkew는 그 "몰림을 얼마나 봐줄 것인가"의 허용치다.

- skew 계산법: `(한 그룹의 파드 개수) - (전체 그룹 중 가장 적은 그룹의 개수)`
- 모든 그룹의 skew 중 **가장 큰 값이 maxSkew를 넘으면 안 된다**

예를 들어 노드 3대에 파드가 4, 2, 2개로 떠 있다면 skew = 4 - 2 = 2다. `maxSkew: 1`로 설정돼 있으면 이 상태는 위반이라, 다음 파드는 무조건 파드가 적은 노드(B나 C) 쪽으로 스케줄링된다.

![maxSkew 계산 예시](/assets/img/posts/maxskew-example.png)
_노드 A(4개)가 이미 초과 상태라 새 파드는 B나 C로만 스케줄링된다_ `maxSkew: 1`은 사실상 "완전 균등"에 가깝지만 정확히는 "제일 많은 곳과 제일 적은 곳의 차이가 1개를 넘지 않는 선까지"를 허용하는 것이다. 그래서 파드 5개를 노드 3대에 나눌 때 2·2·1 분포는 통과하지만 3·1·1 분포는 위반이 된다.

**왜 필요한가.** 이 제약이 없으면 스케줄러는 그냥 여유 있는 노드부터 채우기 때문에, 극단적으로는 파드 대부분이 노드 하나에 몰릴 수 있다. 그 상태에서 그 노드가 죽으면 서비스 replica 대부분이 한 번에 사라진다. maxSkew는 "노드(혹은 존) 하나가 죽어도 서비스 전체가 죽지 않도록" 미리 파드를 흩어두는 안전장치다. `topologyKey`를 `zone`으로 잡으면 가용 영역 단위 장애까지 방어 범위에 들어오고, `hostname`으로 잡으면 노드 단위 장애를 방어한다.

`whenUnsatisfiable: DoNotSchedule`로 엄격하게 걸려 있으면, 롤링 업데이트 도중 surge로 파드가 순간적으로 늘어나서 배치할 자리가 애매해질 때 새 파드가 Pending에 걸려 배포가 멈추는 경우도 생길 수 있다 — maxSurge/maxUnavailable과 maxSkew를 같이 튜닝할 때 염두에 둬야 하는 상호작용이다.

## 정리

같은 "롤링 업데이트"라는 말을 쓰지만, 실제로는 세 가지 서로 다른 상황이 존재한다.

| 상황 | 발동 여부 | 핵심 설정 |
|---|---|---|
| 백엔드 이미지 배포 | O (무중단 우선) | maxSurge=1, maxUnavailable=0, probe 있음 |
| nginx 서버 자체 배포 | O (리소스 절약 우선) | maxSurge=0, maxUnavailable=1, probe 없음 |
| nginx 정적 파일 배포 | X (개념 자체 미적용) | kubectl cp, Pod Spec 불변 |

같은 클러스터, 심지어 같은 nginx Deployment라도 "무엇을 배포하느냐"에 따라 전혀 다른 메커니즘이 동작한다는 게 이 정리의 핵심이다.