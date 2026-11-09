# Isaac ROS Image Segmentation
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-image-segmentation.md)

ROS 2 이미지 의미 분할.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation)  
**라이선스와 범위:** Apache-2.0; 모델 별도.

![Isaac ROS Image Segmentation official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_image_segmentation/isaac_ros_image_segmentation_example_seg.png)
*이미지 출처: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**카메라 영상 → 분할 모델 추론 → 픽셀 레이블 → 후속 인식**

## 활용 사례

로봇 인식에 사용할 영상 영역을 분류합니다.

## 연결 기술

Isaac ROS DNN Inference, TensorRT.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
