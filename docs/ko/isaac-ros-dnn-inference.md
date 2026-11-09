# Isaac ROS DNN Inference
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-dnn-inference.md)

ROS 2용 TensorRT·Triton 추론 연동.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference)  
**라이선스와 범위:** 코드 Apache-2.0; 런타임·모델 별도.

![Isaac ROS DNN Inference official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_inference/isaac_ros_dnn_peoplenet.jpg)
*이미지 출처: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**ROS 2 입력 텐서 → TensorRT 또는 Triton 추론 → 출력 텐서 → 작업별 결과 해석**

## 활용 사례

ROS 2 애플리케이션에서 인식 신경망을 실행합니다.

## 연결 기술

TensorRT, Triton, Isaac ROS.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
