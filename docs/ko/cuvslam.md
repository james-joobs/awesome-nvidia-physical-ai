# cuVSLAM

[← 전체 목록](../../README.ko.md) · [English](../en/cuvslam.md)

cuVSLAM은 별도 패키지인 Isaac ROS Visual SLAM이 사용하는 CUDA 가속 오도메트리·매핑 라이브러리입니다. 네이티브 및 Python 인터페이스도 제공합니다.

![cuVSLAM Python 워크플로](https://media.githubusercontent.com/media/nvidia-isaac/cuVSLAM/main/examples/assets/pycuvslam_overview.jpg)

*추적 호출에 필요한 보정 정보와 센서 구성을 보여주는 공식 예제입니다.* [공식 그림 출처](https://github.com/nvidia-isaac/cuVSLAM)

## 어떻게 동작하나

보정된 카메라 모델, 외부 파라미터와 추적 모드로 센서 구성을 초기화합니다. 타임스탬프가 있는 영상과 지원 모드의 선택 IMU·깊이가 자세를 갱신합니다. 스테레오는 카메라 간격으로 실제 스케일을 구하고, 단안에서는 스케일 모호성이 있습니다. 매핑 계층은 추적 경로를 전역 위치 추정과 루프 클로저에 활용할 수 있습니다.

## 실전 워크플로

기록 데이터로 공식 다중 카메라 예제를 실행합니다. 추정 경로를 측정 경로와 비교하고, 누락 프레임과 속도에 따른 모션 블러를 살펴봅니다. ROS 메시지와 TF 통합에는 [Isaac ROS Visual SLAM](isaac-ros-visual-slam.md)을 사용합니다.

## 검증할 항목

시간 동기화, 노출, 보정과 지원 센서 모드를 확인합니다. 드리프트, 추적 손실, 재위치 추정을 각각 평가합니다.

## 공개 범위와 라이선스

NVIDIA Community License; NVIDIA 플랫폼 제한이 있는 공개 코드, ROS 래퍼와 별도. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [모드, 보정과 예제](https://github.com/nvidia-isaac/cuVSLAM)
- [cuVSLAM 기술 보고서](https://arxiv.org/html/2506.04359v3)
