# SkillGen / SkillMimicGen

[← 목록으로](../../README.ko.md) · [English](../en/skillgen.md)

SkillGen은 재사용 가능한 국소 스킬과 그 사이의 이동 계획을 결합해 시연을 만듭니다. 연구는 SkillMimicGen이라는 이름으로 발표됐습니다. Isaac Lab 튜토리얼은 큐브 쌓기 등의 작업에서 Isaac Lab Mimic과 cuRobo를 연동해 생성 워크플로를 구현합니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **국소 스킬 구간** | 기록 시연을 물체 기준의 접촉 중심 스킬과 이동 동작으로 나눠 주석을 달아야 합니다. 스킬 경계가 재사용할 구간과 새로 계획을 시작할 위치를 결정합니다. |
| **이동 구간 계획** | 새 장면에서는 물체 자세에 맞춰 국소 스킬을 변환하고 플래너로 새 시작점까지 이동 경로를 구합니다. 이동을 계획할 때 경로상의 충돌 기하를 고려합니다. |
| **롤아웃과 정책** | 시뮬레이터에서 계획한 이동과 국소 스킬 궤적을 실행하고 성공 시연을 기록합니다. 논문은 계획 기반 실행을 위한 스킬 시작·제어·종료 학습도 다루며, Isaac Lab 튜토리얼에는 행동 복제 절차가 있습니다. |

![공식 연구 그림은 재사용하는 국소 스킬과 다시 계획할 수 있는 이동 동작을 구분합니다. 시연을 새 장면에 적용할 때 이 구분이 핵심입니다.](https://skillgen.github.io/resources/overview.png)

공식 연구 그림은 재사용하는 국소 스킬과 다시 계획할 수 있는 이동 동작을 구분합니다. 시연을 새 장면에 적용할 때 이 구분이 핵심입니다. [공식 그림 출처](https://skillgen.github.io/)

![Isaac Lab 장애물 회피 예시는 이동 구간에서 동작 플래너가 맡는 역할을 보여줍니다.](https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/obstacle_avoidance_curobo.gif)

Isaac Lab 장애물 회피 예시는 이동 구간에서 동작 플래너가 맡는 역할을 보여줍니다. [공식 그림 출처](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/features/imitation-learning/skillgen.html)

## 적용 예시

1. 공식 Franka 큐브 쌓기 예제에서 파지·배치 경계를 표시합니다. 데이터셋 규모를 늘리기 전에 시각화를 켜고 소규모 생성을 실행합니다.
2. 상자 안 큐브 쌓기 변형에서는 장애물 회피와 스킬 시작 자세 도달 여부를 살펴봅니다. 생성 성공률과 후속 행동 복제 정책 성공률을 비교합니다.

## 검증할 항목

- 주석과 충돌 모델이 생성 결과에 큰 영향을 줍니다. 오래 걸리는 실행 전에 소규모 결과를 점검하고 하위 작업별 실패 원인을 기록합니다.
- 버전에 맞는 Isaac Lab과 cuRobo 설정을 따릅니다. 작업 ID, 원본 데이터셋, 플래너 설정이 같은 공식 워크플로에 해당하는지 확인합니다.

## 공식 자료와 이용 조건

Isaac Lab 구현과 의존성의 조건을 개별 확인합니다. 연구 페이지와 Isaac Lab 튜토리얼은 워크플로의 서로 다른 부분을 설명합니다.

- [SkillMimicGen 프로젝트와 연구 그림](https://skillgen.github.io/)
- [Isaac Lab SkillGen 튜토리얼](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/features/imitation-learning/skillgen.html)
- [논문과 발표 정보](https://proceedings.mlr.press/v270/garrett25a.html)

## 연관 상세 페이지

[MimicGen](mimicgen.md) · [cuRobo](curobo.md) · [Isaac Lab](isaac-lab.md)
