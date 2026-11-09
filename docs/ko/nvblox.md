# nvblox

[← 전체 목록](../../README.ko.md) · [English](../en/nvblox.md)

![nvblox mapping and navigation](https://media.githubusercontent.com/media/nvidia-isaac/nvblox/public/docs/images/nvblox_navigation_trim.gif)

이미지: 아래 공식 프로젝트 출처.

## 소개

3D 공간 매핑·장애물 표현 라이브러리.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["깊이와 카메라 자세 수집"] --> n1
    n1["3D 맵 통합"] --> n2
    n2["장애물 추출"] --> n3
    n3["내비게이션에 활용"]
```

## 활용 흐름과 사례

깊이와 카메라 자세 수집 → 3D 맵 통합 → 장애물 추출 → 내비게이션에 활용. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 이동 로봇의 장애물 지도 생성. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac ROS Nvblox.

## 구성과 실제 활용

깊이 영상과 카메라 자세를 GPU 기반 3D 표현에 통합하며 TSDF·ESDF 계층으로 기하와 거리 질의를 지원합니다. 이동 로봇은 이 지도를 장애물 인식 내비게이션에 활용할 수 있고, 별도의 Isaac ROS 연동을 사용할 수 있습니다.

[공식 문서](https://github.com/nvidia-isaac/nvblox)

![nvblox system diagram](https://raw.githubusercontent.com/nvidia-isaac/nvblox/public/docs/images/system_diagram.png)

*이미지 출처: [Official repository](https://github.com/nvidia-isaac/nvblox)*

## 공개 및 이용 조건

코드 공개; 저장소의 혼합 라이선스 범위 미확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[저장소](https://github.com/nvidia-isaac/nvblox)
