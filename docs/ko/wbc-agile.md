# WBC-AGILE

[← 목록으로](../../README.ko.md) · [English](../en/wbc-agile.md)

WBC-AGILE은 휴머노이드 제어를 위한 Isaac Lab 기반 학습·배포 스택입니다. 공식 예제는 속도·몸 높이 추적부터 쓰러진 자세에서 일어나기, 보행 중 상체 동작을 조율하는 작업까지 다룹니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **작업과 시뮬레이션 환경** | Isaac Lab에서 로봇 관절과 접촉을 시뮬레이션합니다. 선택한 작업이 정책의 관측, 명령, 보상, 종료 조건을 결정합니다. |
| **정책 간 조율** | AGILE 예제에는 상체와 하체 정책을 분리한 구성이 있습니다. 상체 목표가 바뀌는 동안에도 하체는 보행과 균형을 유지해야 하므로 정책 구성별로 관측과 명령 인터페이스가 달라집니다. |
| **내보내기와 평가** | 지원되는 체크포인트는 LEAPP로 내보낼 수 있습니다. 배포 워크플로는 Isaac ROS Deploy에서 번들을 사용해 시뮬레이터 간 이전과 실제 로봇 이전을 평가합니다. |

![상체·하체 정책 그림은 분리된 제어 경로가 한 로봇을 어떻게 함께 제어하는지 보여줍니다. 이 분리는 그림에 나온 정책 구성에 해당합니다.](https://media.githubusercontent.com/media/nvidia-isaac/WBC-AGILE/main/docs/figures/separate_upper_lower_body_policy_diagram.png)

상체·하체 정책 그림은 분리된 제어 경로가 한 로봇을 어떻게 함께 제어하는지 보여줍니다. 이 분리는 그림에 나온 정책 구성에 해당합니다. [공식 그림 출처](https://github.com/nvidia-isaac/WBC-AGILE)

![Unitree G1 예시는 실제 하드웨어에서 속도와 몸 높이를 추적하는 모습을 보여줍니다. 저장소에서 짝을 이루는 시뮬레이션 예시와 비교할 수 있습니다.](https://media.githubusercontent.com/media/nvidia-isaac/WBC-AGILE/main/docs/videos/unitree_g1_vel_height_sim2real.gif)

Unitree G1 예시는 실제 하드웨어에서 속도와 몸 높이를 추적하는 모습을 보여줍니다. 저장소에서 짝을 이루는 시뮬레이션 예시와 비교할 수 있습니다. [공식 그림 출처](https://github.com/nvidia-isaac/WBC-AGILE)

## 적용 예시

1. 작업과 체크포인트가 일치하는 Unitree G1 또는 Booster T1 공개 롤아웃을 재현합니다. 지원하는 체크포인트라면 공식 LEAPP 스크립트로 내보냅니다.
2. 하드웨어에 적용하기 전에 내보낸 정책을 시뮬레이터에서 실행합니다. 런타임별 명령 추적, 넘어짐 또는 회복 동작, 제어 루프 주기를 비교합니다.

## 검증할 항목

- 내보내기 폴더의 구성을 유지합니다. YAML은 상대 경로로 모델 파일과 필요한 상태 산출물을 참조합니다.
- 하드웨어의 관절 순서, 제어 모드, 행동 스케일링을 검증합니다. 시뮬레이터에서의 회복 동작은 접촉과 구동기 모델의 가정에 따라 달라집니다.

## 공식 자료와 이용 조건

프로젝트는 Apache-2.0을 사용하며 일부 RSL-RL 패치에는 BSD-3-Clause를 명시합니다. 체크포인트와 로봇 에셋의 이용 조건은 별도로 확인합니다.

- [저장소·정책 그림·시연](https://github.com/nvidia-isaac/WBC-AGILE)
- [AGILE 배포와 내보내기](https://nvidia-isaac.github.io/WBC-AGILE/deploy-policies.html)

## 연관 상세 페이지

[Isaac Lab](isaac-lab.md) · [LEAPP](leapp.md) · [Isaac ROS Deploy](isaac-ros-deploy.md)
