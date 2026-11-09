# DeepStream

[← 전체 목록](../../README.ko.md) · [English](../en/deepstream.md)

## 소개

실시간 영상 분석 SDK.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["영상 스트림 입력"] --> n1
    n1["디코딩·전처리"] --> n2
    n2["추론"] --> n3
    n3["추적 또는 결과 출력"]
```

## 활용 흐름과 사례

영상 스트림 입력 → 디코딩·전처리 → 추론 → 추적 또는 결과 출력. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 다중 카메라 스트림 분석. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** TensorRT, Metropolis, Jetson.

## 구성과 구체적인 활용

DeepStream은 GStreamer 플러그인으로 영상 분석 그래프를 구성한다. 스트림을 디코딩·배치하고 TensorRT 또는 Triton 추론 플러그인과 후속 처리 플러그인을 연결한다.

여러 카메라 입력을 배치 처리하고 탐지·추적을 수행해 시설 내 움직임을 분석한다.

[공식 기술 자료](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Overview.html)

## 공개 및 이용 조건

제품 SDK; 공개 샘플과 바이너리의 조건 별도. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[공식 페이지](https://developer.nvidia.com/deepstream-sdk)
