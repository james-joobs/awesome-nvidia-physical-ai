# Jetson / JetPack

[← 전체 목록](../../README.ko.md) · [English](../en/jetson-jetpack.md)

Jetson은 엣지 컴퓨팅 모듈이고 JetPack은 지원 모듈에서 실행되는 시스템 이미지와 SDK 구성 요소를 제공합니다.

![JetPack 로봇 소프트웨어 스택](https://developer.download.nvidia.com/images/jetson/robotics-diagram-update-jetpack7.2-cptx26.png)

*공식 JetPack 릴리스의 구성 계층을 보여줍니다. 대상 모듈에서 사용하는 릴리스와 대조하세요.* [공식 그림 출처](https://developer.nvidia.com/embedded/jetpack)

## 어떻게 동작하나

시스템 계층의 Jetson Linux는 보드 지원 패키지, 드라이버, 센서·가속기 인터페이스를 제공합니다. 상위의 CUDA와 TensorRT는 계산과 추론에 사용하며, 호환 릴리스에 Isaac ROS나 DeepStream을 올릴 수 있습니다. 모듈, 캐리어 보드, OS 릴리스와 런타임 라이브러리가 컨테이너·드라이버 호환 범위를 결정합니다.

## 실전 워크플로

이동 로봇에서는 대상 캐리어 보드와 Jetson Linux 릴리스를 정합니다. 카메라 인식과 타임스탬프를 확인한 뒤 작은 TensorRT 인식 파이프라인을 배포합니다. 지속 구동 상태의 전체 지연과 전력 사용을 기록해 전력 모드를 선택합니다.

## 검증할 항목

모듈과 캐리어 지원 표, 컨테이너 아키텍처, 카메라 드라이버와 엔진 파일 호환성, 실제 열부하에서의 워밍업 이후 성능을 확인합니다.

## 공개 범위와 라이선스

제품·배포판; 개별 구성 요소의 조건 상이. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://developer.nvidia.com/embedded/jetpack)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/embedded/jetpack/downloads)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/embedded/jetson-modules)
