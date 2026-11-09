# Isaac Capture (이전 Isaac Teleop 포함)
[← 목록으로](../../README.ko.md) · [English](../en/isaac-capture.md)

원격 조작 및 1인칭 데이터 수집·기록·리타기팅.

**공식 자료:** [저장소](https://github.com/NVIDIA/IsaacCapture)  
**라이선스와 범위:** 기본 Apache-2.0; EgoPost는 OpenMDW-1.1, CloudXR과 일부 선택 패키지는 별도 독점 조건.

![Isaac Capture architecture diagram](https://media.githubusercontent.com/media/NVIDIA/IsaacCapture/main/docs/source/_static/isaac-capture-architecture.png)
*이미지 출처: [Repository](https://github.com/NVIDIA/IsaacCapture)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**입력 장치 → 리타기팅 → 시뮬레이션 또는 실제 로봇 → 시연 기록·재생**

## 주요 구성과 공식 아키텍처

![Isaac Teleop 아키텍처](https://raw.githubusercontent.com/NVIDIA/IsaacCapture/main/docs/source/_static/isaac-teleop-architecture.svg)

*이미지 출처: [Official repository](https://github.com/NVIDIA/IsaacCapture)*

공유 코어는 장치 플러그인, 리타기터와 기록 유틸리티를 제공합니다. Isaac Teleop은 로봇을 조작하며 데이터를 수집하고, 별도의 Ego Pipeline은 1인칭 관측을 수집해 손과 카메라 자세를 복원합니다. 리타기팅은 사람의 입력을 로봇 제어 표현으로 변환하며 장치와 로봇별 지원 범위를 확인해야 합니다.

## 활용 사례

원격 조작으로 로봇 시연을 기록합니다. Ego Pipeline은 로봇 없이 1인칭 인간 데이터도 수집합니다.

## 연결 기술

Isaac Lab, LeRobot, Isaac GR00T.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
