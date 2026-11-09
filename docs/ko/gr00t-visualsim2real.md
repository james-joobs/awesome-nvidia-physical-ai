# GR00T-VisualSim2Real

[← 목록으로](../../README.ko.md) · [English](../en/gr00t-visualsim2real.md)

GR00T-VisualSim2Real 저장소에는 VIRAL과 DoorMan 연구 구현이 들어 있습니다. 두 프로젝트 모두 시뮬레이션에서 휴머노이드를 학습한 후 탑재 센서 관측으로 실제 로봇에 배포합니다. VIRAL은 교사 정책에서 시각 정책을 학습하는 과정에, DoorMan은 전신으로 문을 조작하는 작업에 초점을 둡니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **시뮬레이션 교사 정책** | VIRAL의 학습 단계는 시뮬레이터에서 제공하는 특권 정보를 PPO에 사용합니다. 학습할 때 작업 물체의 자세와 같은 시뮬레이터 상태를 참조할 수 있습니다. |
| **시각 학생 정책** | 학생 정책은 RGB와 자기 상태 등 실제 로봇에서도 얻을 수 있는 관측으로 교사 정책을 학습합니다. 연구에서는 렌더링과 실제 관측의 차이를 줄이기 위한 데이터 규모 확장과 시각적 무작위화를 설명합니다. |
| **하드웨어 인터페이스** | 배포 단계는 탑재 카메라와 로봇 상태를 시각 정책에 입력하고 예측 명령을 실행합니다. 공식 연구는 카메라 시야각 정렬과 하드웨어 특성 파악을 별도 항목으로 다룹니다. |

![VIRAL 공식 구성도에서 시뮬레이터 전용 교사 정보가 어느 단계에서 실제 로봇이 제공할 수 있는 관측으로 바뀌는지 확인할 수 있습니다.](https://viral-humanoid.github.io/static/images/VIRAL-Pipeline.png)

VIRAL 공식 구성도에서 시뮬레이터 전용 교사 정보가 어느 단계에서 실제 로봇이 제공할 수 있는 관측으로 바뀌는지 확인할 수 있습니다. [공식 그림 출처](https://viral-humanoid.github.io/)

![DoorMan 시연에서는 보행, 문과의 접촉, 열린 문 통과가 하나의 작업으로 이어집니다.](https://media.githubusercontent.com/media/NVlabs/GR00T-VisualSim2Real/main/media/doorman-teaser.gif)

DoorMan 시연에서는 보행, 문과의 접촉, 열린 문 통과가 하나의 작업으로 이어집니다. [공식 그림 출처](https://github.com/NVlabs/GR00T-VisualSim2Real)

## 적용 예시

1. Unitree G1 연구라면 지원 작업의 공개 시뮬레이션 롤아웃을 재현하고 교사·학생 성공률을 별도로 기록합니다.
2. 하드웨어에서 시각 정책을 실행하기 전에 카메라 자세와 시야각을 확인합니다. 통제된 환경에서 작업 전체를 평가하고 접촉 실패나 대상이 보이지 않는 사례를 기록합니다.

## 검증할 항목

- 공식 예제와 프로젝트 브랜치 및 로봇 모델을 일치시킵니다. VIRAL과 DoorMan의 코드 경로와 작업 정의는 서로 다릅니다.
- 배포 실패의 원인을 학습 정책으로 판단하기 전에 시야각, 관측 타이밍, 실제 접촉 조건을 비교합니다.

## 공식 자료와 이용 조건

저장소 코드는 Apache-2.0입니다. 모델 체크포인트, 시뮬레이터 에셋, 로봇 모델의 이용 조건은 별도로 확인합니다.

- [소스와 브랜치 안내](https://github.com/NVlabs/GR00T-VisualSim2Real)
- [VIRAL 아키텍처와 실험](https://viral-humanoid.github.io/)
- [DoorMan 프로젝트와 논문](https://doorman-humanoid.github.io/)

## 연관 상세 페이지

[Isaac Lab](isaac-lab.md) · [WBC-AGILE](wbc-agile.md)
