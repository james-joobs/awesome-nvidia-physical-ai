# Cosmos Predict / Transfer / Reason

[← 전체 목록](../../README.ko.md) · [English](../en/cosmos-models.md)

## 소개

각각 세계·영상 생성, 시각 조건 변환, 장면 추론 모델 계열.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["생성에는 Predict, 제어된 변환에는 Transfer, 이해에는 Reason 선택"] --> n1
    n1["입력 준비"] --> n2
    n2["출력 평가"]
```

## 활용 흐름과 사례

생성에는 Predict, 제어된 변환에는 Transfer, 이해에는 Reason 선택 → 입력 준비 → 출력 평가. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 다양한 주행 영상 생성. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Cosmos Data Factory, Cosmos Evaluator.

## 구성과 구체적인 활용

Predict는 월드·영상 이어 생성을, Transfer는 제어 조건에 따른 시각 변환을, Reason은 장면 이해를 지원한다. 지원되는 제어 및 입력 형태는 버전마다 다르다.

주행 영상의 날씨 변형을 Transfer로 생성한 뒤 장면 일관성을 검사할 수 있다.

[공식 기술 자료](https://github.com/NVIDIA/cosmos)

## 공개 및 이용 조건

모델 버전과 가중치별 약관 확인; 전체를 일괄 오픈소스로 취급하지 않음. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[Cosmos 공식 저장소](https://github.com/NVIDIA/cosmos)
