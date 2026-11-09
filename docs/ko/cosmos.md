# Cosmos 및 Cosmos 3

[← 전체 목록](../../README.ko.md) · [English](../en/cosmos.md)

![Cosmos 주행 장면 생성 예시](https://raw.githubusercontent.com/NVIDIA/cosmos/main/assets/demos/transfer_worldscenario.gif)

이미지: 아래 공식 프로젝트 출처.

## 소개

월드 모델·도구 플랫폼 및 모델 계열.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["월드 모델 작업 선택"] --> n1
    n1["프롬프트 또는 영상 준비"] --> n2
    n2["생성·추론"] --> n3
    n3["결과 평가"]
```

## 활용 흐름과 사례

월드 모델 작업 선택 → 프롬프트 또는 영상 준비 → 생성·추론 → 결과 평가. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 물리 환경 시나리오의 합성. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Cosmos Predict, Transfer, Reason, Cosmos Curator.

## 구성과 구체적인 활용

Cosmos 3는 자기회귀 추론과 확산 생성을 결합한 mixture-of-transformers 구조를 사용한다. 더 넓은 플랫폼에는 데이터 선별과 평가 도구도 포함되며, 모델 버전마다 입출력이 다르다.

예를 들어 기존 주행 장면을 바탕으로 드문 상황의 후보 영상을 생성하고, 데이터셋에 넣기 전에 물리적 타당성을 검토한다.

[공식 기술 자료](https://github.com/NVIDIA/cosmos)

## 공개 및 이용 조건

[Cosmos 저장소](https://github.com/NVIDIA/cosmos)는 코드와 모델에 OpenMDW-1.1을 명시; OSI 승인 오픈소스라고 단정하지 않음. 개별 저장소는 별도 조건. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[공식 저장소](https://github.com/NVIDIA/cosmos)
