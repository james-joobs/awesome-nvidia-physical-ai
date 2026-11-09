# Isaac Manipulator

[← 목록으로](../../README.ko.md) · [English](../en/isaac-manipulator.md)

Isaac for Manipulation은 ROS 2에서 로봇팔의 인식·계획·실행을 연동하는 참조 아키텍처입니다. 각 패키지가 깊이, 물체 자세, 장애물 맵, 궤적을 생성하고 워크플로가 이를 연결해 집기·놓기 등의 작업을 수행합니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **시각 입력과 물체 자세** | 참조 워크플로는 카메라 관측에서 작업 물체의 자세를 추정합니다. 구성에 따라 검출 또는 분할로 관심 영역을 찾고, FoundationPose가 조작 스택에 물체 자세를 제공합니다. |
| **장면 충돌 모델** | 스테레오 깊이나 다른 깊이 센서가 맵핑의 입력을 제공합니다. nvblox가 주변 장면 기하를 유지하고 충돌 검사에 필요한 정보를 계획 단계에 전달합니다. |
| **동작 계획과 실행** | MoveIt과 cuMotion은 현재 로봇 상태, 파지 목표, 장애물을 사용해 궤적을 계산할 수 있습니다. 컨트롤러가 궤적을 실행하며 워크플로는 작업 진행을 관리합니다. |

![공식 참조 구성도는 인식 결과를 로봇 계획·실행에 연결합니다. 물체 자세와 장애물 지도는 플래너의 서로 다른 입력이므로 두 경로를 구분해 따라갑니다.](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.2/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_main.png)

공식 참조 구성도는 인식 결과를 로봇 계획·실행에 연결합니다. 물체 자세와 장애물 지도는 플래너의 서로 다른 입력이므로 두 경로를 구분해 따라갑니다. [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)

![RViz 예시에서는 워크플로에 사용되는 장면과 로봇 기하를 볼 수 있습니다. 로봇팔에 명령을 보내기 전에 좌표 변환을 점검하는 데 활용할 수 있습니다.](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.2/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_rviz.png)

RViz 예시에서는 워크플로에 사용되는 장면과 로봇 기하를 볼 수 있습니다. 로봇팔에 명령을 보내기 전에 좌표 변환을 점검하는 데 활용할 수 있습니다. [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)

## 적용 예시

1. 지원되는 집기·놓기 참조 워크플로를 구성합니다. RViz에서 계획 좌표계로 변환된 물체 자세와 장애물 기하를 확인합니다.
2. 순서를 실행하기 전에 접근·파지·후퇴 동작을 계획합니다. 인식, 계획, 제어 단계에서 발생한 실패를 나누어 기록합니다.

## 검증할 항목

- 카메라에서 베이스까지의 변환, 자세 추정 시각, 잡고 있는 물체, 그리퍼 도구 좌표계를 확인합니다. 카메라 좌표계의 자세가 맞더라도 계획 좌표계에서 목표가 잘못될 수 있습니다.
- 릴리스별 하드웨어·구성 요소의 사전 요구사항을 확인합니다. 패키지와 가중치는 따로 배포되며 이용 조건도 다를 수 있습니다.

## 공식 자료와 이용 조건

Isaac ROS 패키지와 모델 에셋은 각자의 조건에 따라 별도로 배포됩니다.

- [공식 참조 아키텍처와 그림](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)
- [Isaac ROS Manipulator 저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_manipulator)

## 연관 상세 페이지

[FoundationPose](foundationpose.md) · [Isaac ROS Nvblox](isaac-ros-nvblox.md) · [cuRobo](curobo.md)
