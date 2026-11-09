# Isaac ROS Visual SLAM
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-visual-slam.md)

ROS 2 기반 시각 주행거리 추정·SLAM 연동.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam)  
**라이선스와 범위:** Apache-2.0; cuVSLAM은 별도 약관.

![Isaac ROS Visual SLAM official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_visual_slam/cuvslam_ros_3.gif)
*이미지 출처: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**카메라 관측·보정 → 시각 SLAM → 자세·주행거리 추정 → 내비게이션 또는 지도**

## 활용 사례

내비게이션을 위해 카메라로 이동 로봇의 자세를 추정합니다.

## 연결 기술

Isaac ROS, cuVSLAM, Nav2.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
