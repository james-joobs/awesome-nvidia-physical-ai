# EgoHand / EgoPost

[← 전체 목록](../../README.ko.md) · [English](../en/egohand-egopost.md)

## 소개

Capture의 1인칭 손·카메라 동작 관련 구성 요소.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["1인칭 관측 수집"] --> n1
    n1["손과 카메라 움직임 추정"] --> n2
    n2["후속 리타기팅을 위한 처리"]
```

## 활용 흐름과 사례

1인칭 관측 수집 → 손과 카메라 움직임 추정 → 후속 리타기팅을 위한 처리. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 로봇 시연을 위한 손동작 기록. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac Capture.

## 구성과 실제 활용

Ego Pipeline은 1인칭 관측을 수집하고 후처리하여 손과 카메라 자세를 복원합니다. 로봇 없이 사람이 물체를 다루는 영상을 수집한 후, 로봇용 리타기팅에 사용하기 전에 복원 동작을 검토하는 사례가 있습니다. 수집 장치와 복원 구성 요소 및 각 라이선스를 별도로 확인하세요.

[공식 문서](https://github.com/NVIDIA/IsaacCapture)

![EgoHand pipeline](https://raw.githubusercontent.com/NVIDIA/IsaacCapture/main/docs/source/_static/egohand-pipeline.svg)

*이미지 출처: [Official repository](https://github.com/NVIDIA/IsaacCapture)*

## 공개 및 이용 조건

EgoPost는 OpenMDW-1.1; EgoHand의 독립 라이선스 미확인. 상위 패키지 기본 라이선스를 일괄 적용하지 않음. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[Isaac Capture](https://github.com/NVIDIA/IsaacCapture)
