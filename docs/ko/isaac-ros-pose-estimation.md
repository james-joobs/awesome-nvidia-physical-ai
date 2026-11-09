# Isaac ROS Pose Estimation
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-pose-estimation.md)

GPU 가속 물체 자세 추정 패키지.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation)  
**라이선스와 범위:** 코드 Apache-2.0; 모델 별도.

![Isaac ROS Pose Estimation official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_pose_estimation/dope_objects.png)
*이미지 출처: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**카메라 영상 + 모델 입력 → 자세 추정 → 물체 자세 → 후속 조작**

## 활용 사례

로봇이 물체를 집기 위한 판단에 활용하도록 물체 자세를 추정합니다.

## 연결 기술

Isaac ROS, FoundationPose, manipulation.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
