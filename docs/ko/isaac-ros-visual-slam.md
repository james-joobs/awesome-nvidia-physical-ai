# Isaac ROS Visual SLAM

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-visual-slam.md)

Isaac ROS Visual SLAM은 카메라로 로봇의 움직임을 추정하는 cuVSLAM을 ROS 2 컴포넌트로 제공합니다.

![오도메트리와 Nav2 연결](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_visual_slam/vslam_odometry_nav2_diagram.png)

*추정 자세가 Nav2에 들어가는 위치를 확인하세요. 자세 추정과 경로 계획의 역할이 분리되어 있습니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_visual_slam/index.html)

![오도메트리와 Nav2 연결 예시](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_visual_slam/cuvslam_ros_3.gif)

*카메라 이동에 따라 추정 궤적이 갱신되는 모습을 보여줍니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_visual_slam/index.html)

## 어떻게 동작하나

**입력:** 보정하고 동기화한 카메라 스트림과 TF 카메라 프레임입니다. 지원 구성에서는 IMU 관측도 사용합니다. **추정:** cuVSLAM은 프레임 간 영상 특징을 추적하고 랜드마크를 삼각 측량해 움직임을 구합니다. SLAM 모드에서는 지도와 루프 클로저 보정이 추가됩니다. **출력:** 오도메트리와 자세를 내비게이션·매핑에서 사용합니다. 연속적인 로컬 오도메트리와 전역 보정이 적용되는 지도 좌표계를 구분합니다.

## 실전 워크플로

창고 통로를 한 바퀴 돌아 영상을 기록합니다. 같은 데이터를 오도메트리 모드와 매핑 모드로 각각 재생해 종료 자세를 시작 자세와 비교합니다. 자세와 스테레오 깊이를 [Isaac ROS Nvblox](isaac-ros-nvblox.md)에 전달할 수 있습니다.

## 검증할 항목

영상·IMU 시간 정렬, 보정, TF, 영상 특징 품질과 드리프트를 확인합니다. 반복되는 선반, 특징 부족, 급회전과 노출 불량은 추적 성능에 영향을 줍니다. 지도 좌표계 보정이 하위 노드에 미치는 영향도 확인합니다.

## 공개 범위와 라이선스

Apache-2.0; cuVSLAM은 별도 약관.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_visual_slam/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam)
