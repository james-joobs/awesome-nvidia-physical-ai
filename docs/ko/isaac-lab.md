# Isaac Lab
[← 목록으로](../../README.ko.md) · [English](../en/isaac-lab.md)

강화·모방학습 및 로봇 학습 환경.

**공식 자료:** [저장소](https://github.com/isaac-sim/IsaacLab)  
**라이선스와 범위:** BSD-3-Clause; 선택한 백엔드와 의존성은 별도 조건.

![Isaac Lab robot learning simulation](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/isaaclab.jpg)
*이미지 출처: [Repository](https://github.com/isaac-sim/IsaacLab)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**로봇·작업 정의 → 관측·보상 설정 → 병렬 시뮬레이션 → 정책 학습·평가**

## 주요 구성과 공식 아키텍처

![Isaac Lab 백엔드 아키텍처](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/concepts/backend-architecture-light.svg)

*이미지 출처: [Official repository](https://github.com/isaac-sim/IsaacLab)*

작업 API는 로봇·환경·관측·행동 및 학습을 정의합니다. 백엔드 확장은 이 인터페이스를 서로 다른 물리·렌더링 구현에 연결합니다. Isaac Sim 백엔드를 사용하는 경우 호환 버전이 필요하며 Newton 기반 워크플로는 Isaac Sim 없이 실행할 수 있습니다. 사용하는 버전에서 지원하는 백엔드와 학습 프레임워크를 선택하세요.

## 활용 사례

조작 또는 이동 정책을 강화학습이나 모방학습으로 학습합니다.

## 연결 기술

Isaac Sim, Newton, Isaac Lab-Arena.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
