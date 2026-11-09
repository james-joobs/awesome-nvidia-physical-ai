# Isaac ROS Nvblox
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-nvblox.md)

ROS 2 3D 지도 및 Nav2 장애물 비용 지도.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox)  
**라이선스와 범위:** Apache-2.0; 의존성 별도.

![Nvblox performance setup](https://raw.githubusercontent.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox/main/resources/nvblox_performance_setup.png)

*이미지 출처: [Official repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**깊이 관측 + 카메라 자세 → 3D 복원 → 거리장·비용 지도 → 내비게이션**

## 활용 사례

깊이 영상으로 이동 로봇의 주변 장애물 지도를 만듭니다.

## 연결 기술

Isaac ROS, Nav2, visual SLAM.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
