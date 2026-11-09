# Isaac ROS Image Segmentation

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-image-segmentation.md)

영상 분할 패키지는 카메라 영상을 픽셀 단위 마스크로 변환합니다. 의미 분할은 픽셀의 클래스에, 인스턴스 분할 방식은 개별 물체 영역의 구분에 활용됩니다.

![영상 분할 노드 그래프](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_image_segmentation/isaac_ros_image_segmentation_nodegraph.png)

*모델 텐서를 픽셀 마스크로 바꾸는 디코더를 보세요.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_image_segmentation/index.html)

![영상 분할 노드 그래프 예시](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_image_segmentation/isaac_ros_image_segmentation_example_seg.png)

*마스크 오버레이는 박스보다 세밀한 픽셀 영역을 보여줍니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_image_segmentation/index.html)

## 어떻게 동작하나

인코더가 영상을 텐서로 바꿉니다. 추론 런타임에서 모델을 실행하고, 디코딩으로 영상 좌표에 정렬된 마스크를 얻습니다. 이후 노드는 레이블을 장면 이해에 사용하거나 단일 물체의 마스크를 자세 추정기로 전달할 수 있습니다. 메시지와 클래스 매핑은 패키지와 모델에 따라 다릅니다.

## 실전 워크플로

목표 물체가 담긴 상자에서 사람이 표시한 RGB 프레임과 마스크를 비교합니다. 물체 경계와 마스크 구멍을 살펴보고, 깊이 프레임과 선택한 마스크를 정렬한 뒤 [자세 추정](isaac-ros-pose-estimation.md)에 전달합니다.

## 검증할 항목

클래스 ID, 마스크 크기 변경 시 보간 방식, 깊이 프레임 정렬과 동기화를 확인합니다. 마스크가 불완전하거나 목표물이 반사되거나 가려졌을 때의 자세 안정성을 측정합니다.

## 공개 범위와 라이선스

Apache-2.0; 모델 별도.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_image_segmentation/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation)
