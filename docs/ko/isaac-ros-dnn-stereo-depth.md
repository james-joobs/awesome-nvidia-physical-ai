# Isaac ROS DNN Stereo Depth
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros-dnn-stereo-depth.md)

ROS 2 신경망 스테레오 깊이 추정.

**공식 자료:** [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth)  
**라이선스와 범위:** 코드 Apache-2.0; 모델 별도.

![Isaac ROS DNN Stereo Depth official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_stereo_depth/ess3.0_conf0_r2b_storage_576p.gif)
*이미지 출처: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**보정된 스테레오 영상 → 신경망 스테레오 추론 → 깊이 영상 → 지도·인식**

## 활용 사례

이동 로봇의 스테레오 카메라 영상에서 깊이를 추정합니다.

## 연결 기술

Isaac ROS DNN Inference, Nvblox, TensorRT.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
