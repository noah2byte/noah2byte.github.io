---
title: "CSR에서 SSR로, Istio까지 GitOps로 (5) — Istio를 App of Apps로, 그리고 mesh 편입"
author: 노아
date: 2026-10-06 09:40:00 +0900
categories: [문제 상황 개선 사례, 천재교육, ArgoCD]
pin: false
math: true
mermaid: true
---

{% raw %}

10월 6일부터 8일까지, PoC 환경에 Istio 를 ArgoCD 로 설치하고 4편에서 만든 앱을 mesh 에 넣은 과정이다. 9월 30일에
"차트에 mesh 분기는 넣고 꺼 둔다"고 미뤄 둔 것을 실제로 켠 셈이다.

---

## 1. 무엇을 계승하고 무엇을 바꿨나

mesh 를 켜려면 Istio 가 있어야 하는데 PoC 환경엔 없었다. 기존 방식(사람이 istioctl + 스크립트)을 쓰지 않은 이유는
1편에 적었다. 버전이 EOL 이라 어차피 설치 방식을 다시 정해야 하고, 앱이 GitOps 로 가는데 그 밑의 Istio 만 수동이며,
PoC 는 운영과 분리돼 실패해도 영향이 없다.

| 계승한 것 | 이유 |
|---|---|
| 과목(네임스페이스)마다 게이트웨이 하나 | Istio 기본은 공유인데 운영은 일부러 나눴다. 장애·트래픽 격리 의도로 보여 유지 |
| 이름 `ingressgateway-<과목>`, 라벨 `istio: ingressgateway-<과목>` | 앱 차트의 Gateway 가 이 라벨로 게이트웨이를 찾는다 |
| Service NodePort 80→8080 / 443→8443 | ALB 가 노드 포트를 타겟으로 잡는다 |
| 버전 1.23.2 | 운영과 맞춰 비교·이관을 쉽게 |

| 바꾼 것 | 이전 | 이후 |
|---|---|---|
| 설치 수단 | `istioctl install -f` | 공식 헬름 차트 (base / istiod / gateway) |
| 게이트웨이 목록 | 스크립트에 하드코딩 | `values.yaml` 의 `gateways` |
| 적용 주체 | 사람 | ArgoCD |
| 권한 | — | 별도 `infra` AppProject |

---

## 2. 래퍼 차트 — App of Apps

Application 파일을 직접 쓰면 과목이 늘 때마다 파일을 복사하고, 버전을 올릴 때 파일마다 고쳐야 한다. 하나라도
빠뜨리면 버전이 섞인다. 그래서 **래퍼 차트가 Application 을 찍어내게** 했다. 기존 스크립트가 목록을 돌며 yaml 블록을
이어 붙이던 것과 구조가 같고, 목록이 Git 에 남고 적용을 ArgoCD 가 한다는 점만 다르다.

![Istio App of Apps](/assets/img/ssr-istio/06-istio-app-of-apps.svg)
_부모 Application 하나가 base → istiod → 과목별 게이트웨이 순으로 자식을 만든다_

```
addon/
├── projects/appproject-infra.yaml      ① 권한 — 먼저 apply
├── applications/istio-addon.yaml       ② 부모 Application — 그다음 apply
└── istio/                              ③ 래퍼 차트 (ArgoCD 가 읽는다)
    ├── values.yaml                        ← 평소에 고치는 유일한 파일
    └── templates/
        ├── 00-base.yaml                   wave 0 · CRD
        ├── 01-istiod.yaml                 wave 1 · 컨트롤 플레인
        └── 02-gateways.yaml               wave 2 · 목록 수만큼
```

**sync-wave 가 필요한 이유** — CRD 가 없으면 istiod 가 못 뜨고, istiod 가 없으면 게이트웨이에 사이드카가 주입되지 않는다.

평소에 고치는 곳은 `values.yaml` 하나다.

```yaml
# base / istiod / gateway 세 차트가 모두 이 값을 쓴다.
# 세 곳에 흩어 두면 업그레이드 때 하나를 빠뜨리기 쉬워 한 곳으로 모았다.
version: 1.23.2

# 비우면 기본 설치. "1-24" 같은 값을 넣으면 istiod-1-24 가 기존 istiod 옆에 나란히 뜨는 카나리 업그레이드가 된다.
revision: ""

# 과목 목록. 예전 스크립트에 하드코딩돼 있던 목록이 여기로 왔다. 한 줄이 게이트웨이 하나다.
gateways:
  - name: test-lms
  # - name: math
  # - name: eng

# 과목마다 같은 값. 과목별로 다르면 그 항목에만 덮어쓴다.
gatewayDefaults:
  serviceType: NodePort
  ports:
    - { name: http,  port: 80,  targetPort: 8080 }
    - { name: https, port: 443, targetPort: 8443 }
```

게이트웨이 템플릿은 목록을 돌며 Application 을 하나씩 찍어 낸다.

```yaml
{{- range .Values.gateways }}               # . = 목록의 한 항목. 바깥 값은 $.Values 로 짚는다
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: istio-gateway-{{ .name }}{{ include "istio-addon.revSuffix" $ }}
  annotations:
    argocd.argoproj.io/sync-wave: "2"       # istiod 다음
spec:
  project: {{ $.Values.argocd.project }}
  source:
    repoURL: {{ $.Values.repoURL }}
    chart: gateway
    targetRevision: {{ $.Values.version }}
    helm:
      releaseName: ingressgateway-{{ .name }}
      values: |
        name: ingressgateway-{{ .name }}
        labels:
          istio: ingressgateway-{{ .name }}  # ← 앱 차트의 Gateway selector 가 이 라벨을 찾는다
        service:
          type: {{ default $.Values.gatewayDefaults.serviceType .serviceType }}
  destination:
    namespace: {{ default "istio-system" .namespace }}
{{- end }}
```

### 설치 중 막힌 것

| 증상 | 원인 | 조치와 이유 |
|---|---|---|
| 부모 `Unknown` | 앱용 프로젝트는 클러스터 범위 리소스를 거의 못 만든다 | **`infra` 프로젝트 신설.** 앱 프로젝트에 열면 그 프로젝트의 모든 앱이 클러스터 권한을 갖는다 |
| `istio-base` OutOfSync (sync 는 성공) | 웹훅 `caBundle` 을 istiod 가 런타임에 채운다 | `ignoreDifferences` |
| 게이트웨이 `Unknown` | helm 3.21 × 차트 1.23.2 에서 스키마 검증이 차트 자기 기본값까지 거부 | 로컬 `helm template` 로 재현해 ArgoCD 문제가 아님을 확정 후 `skipSchemaValidation` |
| `istiod` OutOfSync | istiod 는 웹훅을 두 종류 만드는데 하나만 뺐다 | Validating 도 추가 |

`infra` 프로젝트는 쓰는 것만 나열했다. `*` 로 열지 않은 이유는, 목록에 드러나 있어야 나중에 범위가 늘어난 걸
알아채기 때문이다.

```yaml
clusterResourceWhitelist:
  - { group: apiextensions.k8s.io,          kind: CustomResourceDefinition }        # Gateway·VS 같은 종류 등록
  - { group: admissionregistration.k8s.io,  kind: MutatingWebhookConfiguration }    # 사이드카 주입
  - { group: admissionregistration.k8s.io,  kind: ValidatingWebhookConfiguration }  # 설정 검증
  - { group: rbac.authorization.k8s.io,     kind: ClusterRole }
  - { group: rbac.authorization.k8s.io,     kind: ClusterRoleBinding }
  - { group: "", kind: Namespace, name: istio-system }
```

웹훅의 caBundle 은 이렇게 비교에서 뺐다. 고쳐도 istiod 가 다시 채우는 값이고, 채워졌다는 건 istiod 가 정상이라는 뜻이다.

```yaml
ignoreDifferences:
  - group: admissionregistration.k8s.io
    kind: ValidatingWebhookConfiguration
    jqPathExpressions:
      - '.webhooks[]?.clientConfig.caBundle'
      - '.webhooks[]?.failurePolicy'          # istiod 가 준비 상태에 따라 바꾼다
```

`skipSchemaValidation` 은 **빚으로 남는 설정**이다. 검증을 끈 상태라 values 오타를 못 거른다. 버전을 올릴 때 이 옵션
없이 통과하는지 확인하고 되돌릴 생각이다.

### 과목 추가와 업그레이드

```yaml
# 과목 추가 — 목록에 한 줄
gateways:
  - name: test-lms
  - name: math

# 카나리 업그레이드 — istiod-1-24 가 기존과 나란히 뜬다
version: 1.24.3
revision: "1-24"
```

카나리 때는 과목 네임스페이스 라벨을 `istio-injection=enabled` 에서 `istio.io/rev=1-24` 로 바꾸고 파드를 재시작하면 그
과목만 새 사이드카를 받는다. 문제가 생기면 그 과목 라벨만 되돌린다. 과목이 늘수록 이 방식이 이롭다.

---

## 3. mesh 편입 1단계 — 사이드카만

3편에서 말한 두 층 중 **사이드카만** 먼저 켰다. 라벨은 되돌리기 쉽고 ALB 를 건드리지 않는다.

```bash
kubectl label namespace test-lms istio-injection=enabled
kubectl rollout restart deployment front-end-next -n test-lms    # 사이드카는 파드 생성 시점에만 주입된다
```

파드가 2/2 → 3/3 이 됐다. **3/3 은 "컨테이너가 떠 있다"일 뿐이라** 여섯 가지로 확인했다.

| # | 확인 | 근거 |
|---|---|---|
| 1 | 사이드카 주입 | 차트에 없는 `istio-init`, `istio-proxy` 가 생겼다 |
| 2 | istiod 연결 | 사이드카 로그 `Envoy proxy is ready`, `state: LIVE` |
| 3 | 트래픽이 사이드카 경유 | 응답에 `server: istio-envoy` + nginx 보안 헤더 + Next 의 307 이 함께 |
| 4 | iptables | `istio-init` 로그에 15006/15001 리다이렉트 규칙 |
| 5 | 입구는 아직 mesh 밖 | Ingress 가 앱 네임스페이스에만 있다 |
| 6 | mTLS PERMISSIVE | PeerAuthentication 리소스가 없다 = 기본값 |

작업 서버에 `istioctl` 이 없어 사이드카 안에 원래 있는 `pilot-agent` 로 대신 확인했다. 외부 접속이 안 깨진 건,
ALB 가 보내는 평문을 PERMISSIVE 가 받아 줬고 nginx → Next 는 루프백이라 사이드카를 거치지 않기 때문이다.

---

## 4. mesh 편입 2단계 — 입구 전환

### 켜기 전에 렌더링부터

`mesh.enabled` 는 Ingress 를 다른 네임스페이스로 옮기고 ALB 를 재생성시킨다. 되돌리기 어려우니 **무엇이 만들어지는지
먼저 봤다.**

```bash
helm template front-end-next . -f values.yaml -f values-poc-image.yaml \
  --set mesh.enabled=true \
  --show-only templates/Ingress.yml --show-only templates/Gateway.yml --show-only templates/VirtualService.yml
```

처음 렌더링하니 Gateway·VirtualService 의 `name` 이 비고 목적지가 `..svc.cluster.local` 이었다. mesh 분기는 운영
차트에서 따라왔지만 **하위 값은 채운 적이 없었다.** 그대로 커밋했으면 sync 가 실패했다. 값을 채우고 다시 렌더링해
연결 고리를 하나씩 확인했다.

![연결 고리](/assets/img/ssr-istio/08-name-label-contract.svg)
_Ingress → 게이트웨이 → Gateway → VirtualService → Service → 파드. 이름과 라벨이 하나라도 어긋나면 끊긴다_

```yaml
# Gateway — 이미 있는 게이트웨이 파드에 "80 으로 오는 HTTP 를 받아라"고 문을 연다
spec:
  selector:
    istio: ingressgateway-test-lms         # 래퍼 차트가 붙인 라벨과 글자 하나까지 같아야 한다
  servers:
  - port: { number: 80, name: http, protocol: HTTP }
    hosts: ["*"]                           # ALB 헬스체크(Host 가 IP)도 받도록. TLS 는 ALB 에서 끝난다
---
# VirtualService — 문으로 들어온 요청을 앱 Service 로
spec:
  hosts: ["*"]
  gateways: [istio-system/front-end-next-gw]   # 다른 네임스페이스의 Gateway 는 "네임스페이스/이름"
  http:
  - match: [{ uri: { prefix: / } }]
    route:
    - destination:
        host: front-end-next.test-lms.svc.cluster.local
        port: { number: 80 }
```

세부 경로 규칙은 VirtualService 가 아니라 nginx 가 맡는다. VS 는 "앱으로 보낸다"까지만 한다.

### 권한

Ingress·Gateway 가 `istio-system` 에 생기므로 앱용 프로젝트에 그 네임스페이스를 destination 으로 열었다. 따로
프로젝트를 만들지 않은 이유는, 둘 다 네임스페이스 범위 리소스라 클러스터 권한이 필요 없고 앱의 입구 설정은 앱 차트가
관리하는 게 기존 운영 구조이기 때문이다. 대신 그 프로젝트가 `istio-system` 의 어떤 리소스든 만들 수 있게 된 점은
운영 전에 좁혀야 할 과제로 남겼다.

### 적용 — push 가 곧 배포였다

원래는 "자동 sync 끄기 → 기존 Ingress 수동 삭제 → ALB 정리 확인 → sync" 순서로 하려 했다. 그런데 **values 를
커밋하자 자동 sync 가 바로 돌았다.** 자동 sync 를 끈 건 1분 뒤였다.

```text
Warning  FailedReconcileLoadBalancer  ... 사용중인 타겟 그룹입니다.     ← 10/2 와 같은 에러
Normal   CreateLoadBalancer           ...                              ← 약 1분 뒤 컨트롤러 재시도로 성공
Normal   CreateTargetGroup            ... nodePort: 31492               ← 게이트웨이 Service 의 NodePort
```

ALB 는 새로 만들어졌지만 **공인 IP 는 그대로**였다. 약 1분 접속이 끊겼다. 10월 2일엔 같은 에러에 바로 설정을 바꿔
IP 를 잃었는데, 이번엔 지켜보니 저절로 풀렸다.

### 게이트웨이를 실제로 지나는지

curl 만으론 알 수 없다(사이드카만 있을 때도 같은 307). Istio 는 Envoy 기본 통계 대부분을 꺼 두므로 자체 지표
`istio_requests_total` 을 봐야 한다.

```bash
kubectl exec -n istio-system deploy/ingressgateway-test-lms -c istio-proxy -- \
  pilot-agent request GET stats/prometheus | grep '^istio_requests_total'
```

| 라벨 | 값 | 뜻 |
|---|---|---|
| source_workload | `ingressgateway-test-lms` | 게이트웨이가 |
| destination_service | `front-end-next.test-lms.svc.cluster.local` | 우리 앱으로 보냈다 |
| response_code | 200 × 33 / 307 × 2 / 304 × 3 | 헬스체크 / curl / 브라우저 재방문 |
| source·destination_principal | `spiffe://cluster.local/ns/.../sa/...` | 양쪽 다 Istio 신분증 → 자동 mTLS |

![요청 경로](/assets/img/ssr-istio/05-request-flow.svg)
_ALB → 게이트웨이 → 사이드카 → nginx → Next.js_

### OutOfSync 정리와 장애

입구 전환 뒤 Deployment 만 계속 OutOfSync 였고, 원인이 둘 겹쳐 있었다. `kubectl rollout restart` 가 붙인
`restartedAt`(ArgoCD 가 안 지우는 필드)과, 빈 사이드카 이미지 어노테이션이다. 두 번째를 고치다 `with` 줄을 빠뜨린 채
커밋해 **차트 전체가 사이드카 이미지 주소에 들어갔고**, 롤링 전략 때문에 기존 파드가 먼저 내려가 **약 3분 장애**가
났다. `kubectl rollout undo` 로 복구했다. 경위는 6편에서 자세히 다룬다.

---

## 5. 네임스페이스 라벨 코드화

1단계에서 `kubectl label` 로 손으로 붙인 라벨은 Git 어디에도 없었다. 네임스페이스를 다시 만들거나 같은 차트를 다른
환경에 올리면 사이드카 주입이 빠진다. 1편에서 말한 "스크립트·명령이 상태를 들고 있지 않다" 문제 그대로다. 앞선
시리즈([4편](/posts/argocd-migration-4/))에서 백엔드 차트에 쓰던 방식을 따라 차트에 넣었다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: {{ .Values.deploy.namespace }}
  labels:
    {{- if .Values.mesh.enabled }}
    istio-injection: enabled               # 사이드카 주입도 mesh 스위치 하나에 묶는다
    {{- end }}
  annotations:
    argocd.argoproj.io/sync-wave: "-1"     # 다른 리소스보다 먼저
    # Application 이 prune: true 라 템플릿을 빼면 네임스페이스도 지운다.
    # 네임스페이스가 지워지면 그 안의 모든 것이 사라지므로 이것만은 남긴다.
    argocd.argoproj.io/sync-options: Delete=false,Prune=false
```

넣기 전에 다른 Application 이 이미 이 네임스페이스를 관리하는지 먼저 확인했다(관리 표시 어노테이션이 비어 있었다).
두 Application 이 한 리소스를 관리하면 한쪽이 지울 때 다른 쪽까지 날아가기 때문이다. 적용 후 관리 표시가 생겼고,
파드는 재시작되지 않았다.

---

## 6. 젠킨스 경로 한 바퀴

오전까지는 전부 **사람이 차트를 고치고 사람이 sync** 한 경로였다. 원래 목적인 "코드를 바꾸면 젠킨스부터 배포까지
한 줄로 흐른다"는 9월 말 이후 한 번도 돌지 않았다. 돌려 보니 세 군데가 끊겨 있었다.

```
젠킨스 빌드 ─▶ 태그 patch ─▶ git push ─▶ ArgoCD sync ─▶ 이미지 pull ─▶ 파드
                  ①                          ②              ③
             옛 경로를 고침            자동 sync 꺼 둔 채    pull 시크릿 누락 → 403
```

| # | 원인 | 조치 |
|---|---|---|
| ① | 차트 개편으로 태그 위치가 `ssr.image.tag` 로 옮겨 갔는데 잡은 옛 경로를 고쳤다. yq 는 없는 경로를 조용히 만든다 | `yq -e` 로 경로 확인 후 수정 |
| ② | 작업용으로 끈 자동 sync 를 되돌리지 않았다 | 원복 |
| ③ | 차트 교체 때 pull 시크릿 값이 빠졌다. 이전 이미지는 노드에 이미 있어 pull 할 일이 없어 드러나지 않았다 | 복구 |

①과 ③은 뿌리가 같다. **차트 구조를 바꿀 때 기존 구성과 그 값을 쓰는 곳을 나란히 놓고 비교하지 않았다.**
세 군데를 고치고 나서야 커밋 한 번이 파드 교체까지 한 줄로 흘렀다.

---

이전: [(4) SSR 배포 틀 만들기](/posts/ssr-istio-gitops-4/) · 다음: [(6) 트러블슈팅 30건에서 배운 것](/posts/ssr-istio-gitops-6/)

*(회사·인프라 관련 실명, 클러스터 식별자, 내부 호스트 주소, 레포·시크릿 이름 등은 전부 임의로 재구성해 게시했다.)*

{% endraw %}
