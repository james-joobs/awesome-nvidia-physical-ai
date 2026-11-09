# Isaac ROS Object Detection
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-object-detection.md)

ROS 2 물체 탐지 패키지.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection)  
**라이선스와 범위:** Apache-2.0; 모델 별도.

![Isaac ROS Object Detection official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_object_detection/isaac_ros_object_detection_example_bbox.png)
*이미지 출처: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**카메라 영상 → 탐지 모델 추론 → 경계 상자·레이블 → 후속 애플리케이션**

## 활용 사례

ROS 2 로봇 인식 그래프에서 물체를 탐지합니다.

## 연결 기술

Isaac ROS DNN Inference, TensorRT.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
