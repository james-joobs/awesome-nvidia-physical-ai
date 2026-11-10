# Isaac Lab

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-lab.md)

<p align="center">
  <img src="../../assets/project-marks/isaac-lab.jpg" width="384" alt="Isaac Lab의 가상 지형에서 이동하는 로봇"><br>
  <sub><a href="https://github.com/isaac-sim/IsaacLab">Isaac Lab 공식 저장소 대표 이미지</a></sub>
</p>

Isaac Lab은 배치 시뮬레이션을 로봇 학습 환경으로 묶는다. 관측, 행동, 보상, 리셋 인터페이스를 제공하고 물리 스텝, 관절체 상태, 센서 계산은 선택한 백엔드에서 수행한다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| `InteractiveScene`과 백엔드 | 장면 설정으로 에셋과 센서를 선언하고 환경별 사본을 구성한다. 백엔드 프리셋으로 작업에 사용할 물리·렌더링·장면 도구를 선택한다. |
| `ManagerBasedRLEnv` | 매니저는 작업 설정으로 행동을 구동 목표로 바꾸고 관측, 보상, 종료, 이벤트를 만든다. 전체 환경을 다시 작성하지 않고 항목을 재사용하거나 센서를 교체할 수 있다. |
| `DirectRLEnv` | 작업 코드에서 행동 적용, 관측·보상 생성, 환경 리셋 루틴을 직접 구현해 실행 루프를 세밀하게 제어한다. |
| 정책 러너 | 학습 스택은 배치 환경 인터페이스를 사용해 정책 체크포인트를 만든다. 시뮬레이터 하위 스텝과 정책 스텝의 주기는 다를 수 있다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    task["작업 항목과 장면 설정"]
    env["Isaac Lab 환경과 장면"]
    sim["선택한 시뮬레이션 백엔드"]
    policy["정책 또는 학습 러너"]
    ckpt["정책 체크포인트와 지표"]
    task --> env
    env --> sim
    sim --> env
    env --> policy
    policy --> env
    policy --> ckpt
```

### 공식 그림과 예시

![Isaac Lab 공식 백엔드 구성도는 환경이 사용하는 인터페이스와 백엔드별 구현의 연결을 보여 준다.](https://raw.githubusercontent.com/isaac-sim/IsaacLab/main/docs/source/_static/concepts/backend-architecture-light.svg)

Isaac Lab 공식 백엔드 구성도는 환경이 사용하는 인터페이스와 백엔드별 구현의 연결을 보여 준다. [그림 출처와 원문 설명](https://isaac-sim.github.io/IsaacLab/develop/source/concepts/backends_and_presets.html)

## 워크플로 예시

1. 매니저 기반 카트폴 예제에서 상태 관측과 구동기 행동의 연결을 확인한다. 환경을 하나만 실행해 리셋 동작과 관절 단위를 점검한다.
2. 로봇팔 도달 작업에서는 장면을 바꾸고 목표 자세 관측, 관절 행동, 거리 보상을 정의한다. 환경 수를 늘리기 전에 종료 조건과 리셋 분포를 설정한다.
3. 고정 시드로 체크포인트를 재생하고 목표 자세와 물리 매개변수를 바꿔 본다. 실제 로봇에 적용하기 전에 미사용 조건에서 성공률과 행동의 부드러움을 평가한다.

## 검증 포인트

- PhysX, Newton 등의 프리셋을 바꾸기 전에 백엔드 지원 표를 확인한다. 센서, 구동기, 제약 지원은 백엔드와 릴리스에 따라 다르다.
- 새 시뮬레이션이나 하드웨어 러너로 정책을 옮길 때 관측 순서, 정규화, 관절 규약과 제어 주기를 맞춘다.

## 라이선스와 범위

Isaac Lab 코드는 BSD-3-Clause다. 백엔드, 정책 가중치, 에셋 조건은 별도다.

## 관련 가이드

[Isaac Sim](isaac-sim.md) · [Newton](newton.md) · [Isaac Lab-Arena](isaac-lab-arena.md) · [Isaac RLPT](isaac-rlpt.md) · [Microduck](microduck.md)

## 공식 자료

- [Isaac Lab 저장소](https://github.com/isaac-sim/IsaacLab)
- [백엔드 선택과 프리셋](https://isaac-sim.github.io/IsaacLab/develop/source/concepts/backends_and_presets.html)
- [매니저 기반 환경 튜토리얼](https://isaac-sim.github.io/IsaacLab/main/source/tutorials/03_envs/create_manager_rl_env.html)
- [Newton 백엔드 인터페이스](https://docs.nvidia.com/isaaclab/concepts/newton)
