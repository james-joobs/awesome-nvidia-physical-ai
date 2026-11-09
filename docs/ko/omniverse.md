# NVIDIA Omniverse

[← 전체 목록](../../README.ko.md) · [English](../en/omniverse.md)

## 소개

OpenUSD 기반 3D 개발 플랫폼.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["OpenUSD 에셋과 장면 구성"] --> n1
    n1["시뮬레이션 애플리케이션 연결"] --> n2
    n2["디지털 트윈 구축 및 반복 개선"]
```

## 활용 흐름과 사례

OpenUSD 에셋과 장면 구성 → 시뮬레이션 애플리케이션 연결 → 디지털 트윈 구축 및 반복 개선. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 공장 디지털 트윈. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** OpenUSD, Isaac Sim, SimReady.

## 구성과 구체적인 활용

Omniverse Kit은 확장 기능을 조합해 앱을 만드는 프레임워크를 제공하며, OpenUSD는 호환되는 앱 간 장면 데이터를 구성하고 교환하는 데 사용된다.

공장 지형과 설비를 공유 장면으로 구성하고 시뮬레이터에 연결해 로봇 작업을 평가한다.

[공식 기술 자료](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/kit_architecture.html)

## 공개 및 이용 조건

제품·SDK와 공개 구성 요소의 조건이 각각 다름. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[공식 페이지](https://developer.nvidia.com/omniverse)
