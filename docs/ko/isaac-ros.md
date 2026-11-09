# Isaac ROS
[← 목록으로](../../README.ko.md) · [English](../en/isaac-ros.md)

ROS 2 기반 GPU 가속 로봇 패키지 모음.

**공식 자료:** [공식 문서](https://nvidia-isaac-ros.github.io/) · [공통 코드](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common)  
**라이선스와 범위:** 패키지별 조건 상이; 공통 저장소와 배포물의 개별 라이선스 확인.

> 공식 이미지: 확인된 이미지를 찾지 못해 아래 개념 흐름을 제공합니다.

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**센서 토픽 → 가속 ROS 2 인식·추론 → 지도 작성 또는 계획 → 로봇 애플리케이션**

## 활용 사례

CUDA 지원 로봇 컴퓨터에서 인식·내비게이션 파이프라인을 구성합니다.

## 연결 기술

ROS 2, Jetson, Isaac ROS Visual SLAM, Nvblox.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
