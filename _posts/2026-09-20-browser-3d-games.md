---
title: three.js로 브라우저 3D 게임 두 개 만들기
date: 2026-09-20 20:00:00 +0900
categories: [운영 이모저모, 기타]
---

three.js로 간단한 브라우저 3D 게임 두 개를 만들었다. 게임은 [게임 탭](/game/)에 모아 두었고, 아래 링크로 바로 플레이할 수 있다.

## 도심 질주

밤의 서울 도로에서 차량 사이를 빠져나가는 레이싱 게임이다. 도심 업무지구, 한강 다리, 터널, 항만, 한옥 마을 등 8개 구역이 무작위로 이어지고 구간에 따라 비가 온다. 차량 모델과 환경맵은 오픈 라이선스 자산을 쓰고, 도시는 전부 코드로 생성했다.

- [▶ 플레이하기](/game/#city-rush)
- 소스: [noah2byte/city-rush](https://github.com/noah2byte/city-rush)

## 종이배

해 질 녘 강을 따라 떠내려가는 종이배를 조종해 바위를 피하고 등불을 모으는 게임이다. 모델 파일 없이 기본 도형만으로 만들었다.

- [▶ 플레이하기](/game/#paper-boat)
- 소스: [noah2byte/paper-boat](https://github.com/noah2byte/paper-boat)

<!-- TODO: 만든 과정, 성능 최적화(드로콜 97→병합), 조향 관성 모델, 청크 스트리밍·곡선 셰이더, 자산 파이프라인 등 본문 작성 -->

## 사용한 자산

- 차량 모델: [Car Concept](https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CarConcept) by Eric Chadwick, Darmstadt Graphics Group GmbH, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 폴리곤 단순화·텍스처 압축·도색 변경을 거쳤다.
- 환경맵: [Moonless Golf](https://polyhaven.com/a/moonless_golf) by Greg Zaal, Poly Haven, CC0
- 폰트: Gowun Dodum, Black Han Sans, Do Hyeon (SIL Open Font License)
