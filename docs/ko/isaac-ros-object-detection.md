# Isaac ROS Object Detection

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-object-detection.md)

객체 탐지 패키지는 ROS 카메라 영상에서 모델별 2D 탐지 결과를 발행합니다. 후속 추적과 로봇 조작에서 이 결과를 인식 입력으로 사용합니다.

![객체 탐지 노드 그래프](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_object_detection/isaac_ros_object_detection_nodegraph.png)

*출력 경계는 2D 탐지 결과입니다. 이후 노드에서 목적에 맞게 사용합니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_object_detection/index.html)

![객체 탐지 노드 그래프 예시](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_object_detection/isaac_ros_object_detection_example_bbox.png)

*탐지한 클래스별 박스를 입력 영상 위에 배치한 예입니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_object_detection/index.html)

## 어떻게 동작하나

공식 그래프는 영상 인코더와 신경망 런타임으로 시작합니다. 탐지기별 디코더가 2D 박스, 신뢰도와 클래스 레이블을 계산합니다. 고정 클래스 탐지기는 학습 시의 레이블 집합을 사용합니다. 탐지 박스를 프롬프트 분할 노드에 전달하거나 관심 물체의 영역을 선택하는 데 사용할 수 있습니다.

## 실전 워크플로

작업대 카메라로 토트를 탐지합니다. 오버레이를 확인하고, 탐지 시간과 RGB 프레임을 맞춰 비슷한 포장재에서 오탐이 발생하는지 기록합니다. 파지 좌표가 필요하면 깊이와 자세 추정 단계를 연결합니다.

## 검증할 항목

레이블 ID, 신뢰도 및 중복 제거 설정, 박스 좌표 규약, 모델 라이선스를 확인합니다. 실제 촬영 거리와 가림, 조명에서 탐지 성능을 평가합니다.

## 공개 범위와 라이선스

Apache-2.0; 모델 별도.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_object_detection/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection)
