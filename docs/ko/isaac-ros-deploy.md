# Isaac ROS Deploy

[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-deploy.md)

Isaac ROS Deploy는 학습된 정책을 ROS 2 노드나 ros2_control 루프 안에서 실행합니다. LEAPP 번들을 읽어 정책 인터페이스를 시뮬레이터 또는 실제 로봇의 관측·명령 채널에 연결합니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **번들과 텐서 의미** | LEAPP YAML에 그래프 입출력과 텐서 의미를 정의합니다. 변환기가 ROS 메시지나 제어 인터페이스 데이터를 이름 있는 텐서로 바꾸고 출력은 로봇 명령으로 되돌립니다. |
| **추론 그래프** | 런타임은 ONNX 모델 파일을 읽고 NVIDIA Triton으로 추론할 수 있습니다. 토픽 연결에는 ROS 2 노드 런타임을, 컨트롤러 루프 연동에는 ros2_control 런타임을 선택합니다. |
| **명령 실행** | 선택적인 SafetyController가 하드웨어로 명령을 보내기 전에 정책 명령을 혼합하거나 설정한 관절 속도 임계치를 검사할 수 있습니다. 적용 범위와 한계는 NVIDIA 문서에서 확인합니다. |

```mermaid
flowchart LR
    S["로봇 센서와 목표"] --> C["입력 변환기"]
    C --> N["LEAPP 그래프와 ONNX 추론"]
    N --> O["출력 변환기"]
    O --> R["ROS 2 토픽 또는 ros2_control"]
    R --> H["시뮬레이터 또는 하드웨어"]
    H --> S
```

![UR10e policy rollout](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.5/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/ur10e_rl_reach.gif)

공식 UR10e 목표 도달 예시는 제어 루프를 실행했을 때의 동작을 보여줍니다. 위 도식은 패키지 문서에 나온 런타임 인터페이스를 바탕으로 정리했습니다. [공식 예제](https://nvidia-isaac-ros.github.io/v/release-4.5/reference_workflows/isaac_for_manipulation/tutorials/sim_to_real/tutorial_sim_to_real.html)

## 적용 예시

1. Isaac Lab의 공식 목표 도달 정책 튜토리얼을 따릅니다. 지원 정책을 내보낸 뒤 목표와 로봇 상태 채널을 올바르게 설정하고, 지원되는 시뮬레이터에서 시험합니다.
2. 알려진 관측의 그래프 출력과 Python 추론 결과를 비교합니다. 실제 하드웨어 시험 전에 출력 단위와 타임아웃을 확인하고, 센서 연결 상태에서 전체 루프 지연을 측정합니다.

## 검증할 항목

- 텐서 순서, 자료형, 관측 시점, 기준 좌표계를 하드웨어 설정과 맞춥니다. 텐서 형상이 맞는 것만으로 올바른 로봇 동작을 보장할 수 없습니다.
- NVIDIA는 SafetyController를 기능 안전 인증을 받지 않은 선택적 런타임 구성 요소로 설명합니다. 하드웨어 플랫폼의 독립적인 안전 절차를 적용합니다.

## 공식 자료와 이용 조건

저장소 코드는 Apache-2.0입니다. 선택한 추론 런타임과 정책 가중치의 이용 조건은 별도로 확인합니다.

- [Isaac ROS Deploy 문서와 런타임 선택](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_deploy/)
- [SafetyController와 제어 루프 연결](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_deploy/concepts/safety.html)
- [Isaac Lab에서 로봇으로 목표 도달 정책을 배포하는 튜토리얼](https://nvidia-isaac-ros.github.io/v/release-4.5/reference_workflows/isaac_for_manipulation/tutorials/sim_to_real/tutorial_sim_to_real.html)
- [소스 저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_deploy)

## 연관 상세 페이지

[LEAPP](leapp.md) · [Isaac Lab](isaac-lab.md) · [Isaac GR00T](isaac-gr00t.md)
