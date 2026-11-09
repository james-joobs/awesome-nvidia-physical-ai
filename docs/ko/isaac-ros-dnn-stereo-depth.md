# Isaac ROS DNN Stereo Depth

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-dnn-stereo-depth.md)

스테레오 깊이 패키지는 보정된 카메라 쌍으로 깊이를 추정합니다. 공식 문서에서는 처리 속도와 정확도를 기준으로 여러 모델을 비교합니다.

![ESS ROS 노드 그래프](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_stereo_depth/isaac_ros_ess_nodegraph.png)

*전처리, 신경망 시차 추정, 후속 깊이 변환의 경계를 확인하세요.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html)

![ESS ROS 노드 그래프 예시](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_stereo_depth/model_comparison.png)

*모델 비교 자료에서 실제 장비에서 재검증할 정확도와 처리량 항목을 찾을 수 있습니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html)

## 어떻게 동작하나

정류로 좌우 영상의 대응점을 같은 에피폴라 행에 맞춥니다. 추론 노드는 두 영상에서 시차를 예측합니다. 단위와 보정값이 일치하면 초점거리 × 카메라 간격 ÷ 시차로 깊이를 계산합니다. ESS와 FoundationStereo의 모델·연산 요구사항은 서로 다릅니다. 생성한 깊이 영상은 [Nvblox](isaac-ros-nvblox.md)에 전달할 수 있습니다.

## 실전 워크플로

스테레오 카메라로 거리를 알고 있는 상자를 여러 위치에서 촬영합니다. 상자 중앙과 가림 경계, 반사면의 깊이 값을 비교합니다. 동일 프레임을 후보 모델별로 재생해 지연과 유효 픽셀 비율을 확인합니다.

## 검증할 항목

카메라 간격과 단위, 정류 상태, 모델 입력 해상도, 무효·저신뢰도 픽셀 처리 방식을 확인합니다. 거리 구간별 오차를 확인한 뒤 모델과 신뢰도 기준을 선택합니다.

## 공개 범위와 라이선스

코드 Apache-2.0; 모델 별도.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth)
