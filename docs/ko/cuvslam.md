# cuVSLAM

[← 전체 목록](../../README.ko.md) · [English](../en/cuvslam.md)

![cuVSLAM official example](https://media.githubusercontent.com/media/nvidia-isaac/cuVSLAM/main/examples/assets/pycuvslam_overview.jpg)

이미지: 아래 공식 프로젝트 출처.

## 소개

CUDA 가속 시각 위치 추정·SLAM 라이브러리.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["스테레오 또는 다중 카메라 영상"] --> n1
    n1["시각 주행거리 추정·매핑"] --> n2
    n2["내비게이션에 활용할 카메라 자세"]
```

## 활용 흐름과 사례

스테레오 또는 다중 카메라 영상 → 시각 주행거리 추정·매핑 → 내비게이션에 활용할 카메라 자세. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 창고 로봇의 위치 추정. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac ROS Visual SLAM.

## 구성과 실제 활용

보정된 카메라와 동기화된 시각 관측을 사용해 시각 주행거리와 지도를 계산하고, 추정 자세를 내비게이션에 전달할 수 있습니다. 창고 이동 로봇에 적용할 때 움직임·표면 무늬·조명 변화에 따른 추적 품질을 검증하세요. Isaac ROS Visual SLAM은 별도 ROS 연동이며 cuVSLAM 자체 약관이 적용됩니다.

[공식 문서](https://github.com/nvidia-isaac/cuVSLAM)

## 공개 및 이용 조건

NVIDIA Community License; NVIDIA 플랫폼 제한이 있는 공개 코드, ROS 래퍼와 별도. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[저장소](https://github.com/nvidia-isaac/cuVSLAM)
