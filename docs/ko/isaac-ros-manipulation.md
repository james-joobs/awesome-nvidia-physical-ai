# Isaac ROS Manipulation

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-manipulation.md)

Isaac ROS 조작 워크플로는 로봇 팔에 필요한 인식, 장면 재구성, 동작 계획을 연결합니다.

![Isaac 조작 참조 아키텍처](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.6/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_main.png)

*목표와 장애물 경로가 계획기와 제어기에 연결되는 부분을 확인하세요. 4.6 참조 워크플로입니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)

![RViz의 계획 장면](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.6/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_rviz.png)

*실행 전에 로봇 모델, 인식 장면과 계획을 대조할 수 있는 화면입니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)

## 어떻게 동작하나

참조 아키텍처에는 인식 경로가 두 개 있습니다. 한쪽은 RGB-D와 Nvblox로 장애물 형상을 만들고, 다른 쪽은 탐지기 또는 분할 모델과 자세 추정기로 목표 물체 자세를 구합니다. MoveIt 또는 cuMotion 통합이 로봇 상태, 충돌 형상, 목표를 이용해 제어기로 보낼 궤적을 생성합니다.

## 실전 워크플로

Isaac Sim에서 Franka 팔과 보정된 카메라를 실행합니다. RViz에서 장애물 형상, 목표 자세, 계획 궤적을 확인합니다. 통로를 막는 물체를 옮긴 뒤 다시 계획해 성공 여부와 최소 간격을 비교합니다.

## 검증할 항목

카메라와 베이스 사이 보정, 시간 정렬, 계획 장면의 갱신을 확인합니다. 메시 스케일과 좌표계도 확인합니다. 계획 결과, 궤적 추종, 하드웨어 한계는 별도로 검증합니다.

## 공개 범위와 라이선스

코드 Apache-2.0; 모델·의존성 별도.

## 공식 자료

- [Isaac Perceptor 데이터 흐름](https://nvidia-isaac-ros.github.io/v/release-3.1/reference_workflows/isaac_perceptor/technical_details.html)
- [Isaac for Manipulation 참조 아키텍처](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)
- [관련 공식 자료 · github.com](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_manipulation)
