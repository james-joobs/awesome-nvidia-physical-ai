# NVIDIA PhysX

[← 전체 목록](../../README.ko.md) · [English](../en/nvidia-physx.md) · [공식 소스](https://github.com/NVIDIA-Omniverse/PhysX) · [공식 문서](https://nvidia-omniverse.github.io/PhysX/physx/5.4.0/docs/RigidBodyDynamics.html)

강체, 충돌, 제약 및 관절 시스템을 시뮬레이션하는 물리 SDK입니다.

**라이선스:** PhysX SDK는 BSD-3-Clause; 추가 구성 요소는 별도 확인. 사용 전에 해당 버전과 에셋·모델·의존성의 조건을 확인하세요.



## 구성과 아키텍처

장면에 시뮬레이션 객체를 넣고 시간 단위로 진행합니다. 지원되는 구성에서는 GPU 강체 시뮬레이션 기능도 제공합니다.

```mermaid
flowchart LR
    A["강체와 형상"] --> B["충돌·제약 처리"] --> C["물리 계산"] --> D["갱신된 상태"]
```

*이 안내서에서 만든 개념적 흐름도입니다. 실제 구현은 공식 문서를 확인하세요.*

## 활용 흐름

형상·강체·관절·재질 속성으로 장면을 구성하고 시간을 진행한 뒤 상태와 접촉 결과를 애플리케이션에 활용합니다.

## 활용 사례

로봇 팔과 물체 상호작용, 충돌 동작, 상호작용형 3D 환경을 시뮬레이션할 수 있습니다.

## 연계 기술

Isaac Sim은 OpenUSD 기반 환경에서 물리 시뮬레이션을 사용합니다. PhysX는 물리 계산 SDK이고 OpenUSD는 장면을 기술합니다.

## 공식 자료

- [프로젝트 저장소](https://github.com/NVIDIA-Omniverse/PhysX)
- [공식 문서](https://nvidia-omniverse.github.io/PhysX/physx/5.4.0/docs/RigidBodyDynamics.html)
