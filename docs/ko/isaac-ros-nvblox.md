# Isaac ROS Nvblox

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-nvblox.md)

Isaac ROS Nvblox는 GPU 복셀 매핑 라이브러리를 ROS 2에서 사용하고 Nav2에 비용 지도 계층을 제공하도록 연결합니다.

![깊이·자세에서 지도 및 Nav2로](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_nvblox/isaac_ros_nvblox_nodegraph.png)

*깊이와 자세가 재구성 노드로 들어간 뒤 경로 계획용 단면과 시각화 출력이 분리되는 부분을 보세요.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_nvblox/index.html)

![깊이·자세에서 지도 및 Nav2로 예시](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_nvblox/isaac_sim_nvblox_humans.gif)

*시뮬레이터의 지도에 사람이 등장하는 예입니다. 동적 장애물을 시험할 때 지도와 비용 지도를 함께 확인하세요.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_nvblox/index.html)

## 어떻게 동작하나

깊이와 카메라 내부 파라미터를 이용해 3D 측정값을 계산하고, 자세 또는 TF로 공통 지도 좌표계에 배치합니다. Nvblox는 측정값을 복셀에 통합하고 장애물까지의 거리를 계산합니다. Nav2는 2D 비용 지도 단면을 받습니다. 선택적으로 RGB를 시각화에 활용하며, 메시와 비용 지도는 별도의 출력입니다.

## 실전 워크플로

작은 가상 통로에서 깊이와 TF를 먼저 연결합니다. 로봇이 피해야 할 장애물 높이에 맞춰 단면 범위를 설정한 뒤, 낮은 상자와 위로 돌출된 선반을 놓고 메시와 경로 계획기가 보는 장애물을 비교합니다.

## 검증할 항목

깊이 스케일, 카메라 내부 파라미터, TF 지연, 복셀 해상도와 단면 높이를 확인합니다. 복셀을 작게 하면 세부 표현과 GPU 메모리 사용량이 늘어납니다. 움직이는 사람을 처리하는 방식은 선택한 파이프라인과 지원 입력에 따라 다릅니다.

## 공개 범위와 라이선스

Apache-2.0; 의존성 별도.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_nvblox/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox)
