# Isaac Lab-Arena
[← 목록으로](../../README.ko.md) · [English](../en/isaac-lab-arena.md)

조합 가능한 로봇 작업 환경과 정책 평가.

**공식 자료:** [저장소](https://github.com/isaac-sim/IsaacLab-Arena)  
**라이선스와 범위:** Apache-2.0; Isaac Sim 등 의존성 별도.


## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**로봇 + 장면 + 작업 → 환경 조합 → 정책 실행 → 평가 결과 비교**

## 주요 구성과 공식 아키텍처

![Isaac Lab-Arena 아키텍처](https://raw.githubusercontent.com/isaac-sim/IsaacLab-Arena/main/docs/images/isaac_lab_arena_arch_overview.png)

*이미지 출처: [Official repository](https://github.com/isaac-sim/IsaacLab-Arena)*

Arena는 로봇 구성, 장면, 작업을 분리해 평가 환경으로 조합합니다. 선택한 구성에서 정책을 실행하고 작업과 장면 변화에 따른 지표를 비교할 수 있습니다. 사용 가능한 환경과 실험적 에이전트 기반 생성 기능은 공식 저장소를 참고하세요.

## 활용 사례

로봇 형태와 장면 조건을 바꿔 조작 정책을 비교합니다.

## 연결 기술

Isaac Lab, Isaac Sim, SimReady.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
