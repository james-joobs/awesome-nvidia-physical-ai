# Isaac ROS Pose Estimation

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-pose-estimation.md)

자세 추정 패키지는 강체의 위치와 방향을 계산합니다. 어떤 입력을 요구하는지는 선택한 모델에 따라 다릅니다.

![자세 추정 노드 그래프](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_pose_estimation/isaac_ros_pose_estimation_nodegraph.png)

*백엔드별 입력을 따라가며 어떤 관측값을 준비해야 하는지 확인하세요.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_pose_estimation/index.html)

## 어떻게 동작하나

FoundationPose 경로에서는 보정된 RGB-D, 목표 마스크, 물체 형상을 사용합니다. 자세 후보를 보정하고 점수를 매긴 뒤 추적 단계에서 이전 자세를 따라갑니다. DOPE 등 다른 백엔드는 RGB 특징과 학습된 물체 모델을 사용합니다. 추정 자세는 카메라 또는 설정한 좌표계로 나오며, TF로 로봇 베이스에 변환합니다.

## 실전 워크플로

테이블 위 형상을 아는 부품의 자세를 초기 추정한 뒤 거리를 아는 두 번째 위치로 옮깁니다. 고정구나 마커로 측정한 변환과 결과를 비교합니다. 베이스 좌표계로 변환한 뒤 로봇을 움직이기 전에 파지 계획을 시각화합니다.

## 검증할 항목

깊이 단위, 메시 크기와 원점, 좌표계 규약, 물체 대칭성, 마스크 품질과 가림을 확인합니다. 초기 추정과 추적을 따로 검증하고 추적을 잃으면 초기화합니다.

## 공개 범위와 라이선스

코드 Apache-2.0; 모델 별도.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_pose_estimation/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation)
