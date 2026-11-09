# Isaac ROS Teleop

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-teleop.md)

Isaac ROS Teleop은 조작자의 XR 입력을 지원되는 로봇 원격조작 실행 구성에 연결합니다.

![Unitree G1 원격조작 시연](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_physical_ai/isaac_ros_unitree_g1_teleop_bringup/unitree-g1-teleop-hero.gif)

*조작자의 팔 동작과 휴머노이드의 동작을 비교할 수 있습니다. 명령 인터페이스는 실행 구성 문서에서 확인하세요.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_teleop/index.html)

## 어떻게 동작하나

Unitree G1 예에서는 XR 입력을 애플리케이션으로 스트리밍하고 움직임 의도로 해석해 로봇 명령으로 변환합니다. 로봇의 제어기가 명령을 받아 실행합니다. 카메라 영상이 조작자에게 돌아와 동작을 수정할 수 있습니다. 로봇별 매핑과 제어는 실행 구성에서 설정합니다.

## 실전 워크플로

지원되는 가상 로봇에서 시작합니다. 중립 자세를 비교하고 한 손을 천천히 움직입니다. 실제 장비에 적용하기 전에 손이 추적 범위를 벗어나거나 네트워크가 끊겼을 때 제어기 반응을 확인합니다.

## 검증할 항목

버전, 매핑, 보정, 네트워크 지연, 정지·초기화 동작을 확인합니다. 명령 한계와 통신 끊김 처리를 조작자 영상과 별도로 시험합니다.

## 공개 범위와 라이선스

Apache-2.0; 장치 소프트웨어 별도.

## 공식 자료

- [Isaac ROS Teleop 패키지 문서](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_teleop/index.html)
- [관련 공식 자료 · github.com](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_teleop)
