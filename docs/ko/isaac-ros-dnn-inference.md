# Isaac ROS DNN Inference

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros-dnn-inference.md)

Isaac ROS DNN Inference는 ROS 2 데이터를 신경망 추론 런타임에 연결합니다. 배포 방식에 따라 TensorRT 노드 또는 Triton 노드를 사용할 수 있습니다.

![DNN 추론 노드 그래프](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_inference/isaac_ros_dnn_inference_nodegraph.png)

*영상 인코더부터 추론, 디코더까지 순서대로 따라가면 텐서가 의미 있는 결과로 바뀌는 위치를 확인할 수 있습니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_inference/index.html)

![DNN 추론 노드 그래프 예시](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_inference/isaac_ros_dnn_peoplenet.jpg)

*PeopleNet 박스는 디코딩된 출력의 예입니다. 영상 좌표와 신뢰도 기준을 검토하는 데 활용할 수 있습니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_inference/index.html)

## 어떻게 동작하나

인코더는 영상을 정해진 레이아웃, 정규화, 입력 이름을 갖는 텐서로 바꿉니다. 추론 노드는 신경망을 실행해 출력 텐서를 생성합니다. 모델별 디코더가 이를 탐지 결과 등의 ROS 메시지로 변환합니다. 호환 가속 버퍼를 사용하는 노드 사이에서는 NITROS 메시지 협상으로 전송을 효율화할 수 있습니다.

## 실전 워크플로

카메라 사람 탐지기를 배포할 때 인코딩 입력과 원시 출력을 기준 추론과 대조합니다. 이후 디코더를 연결해 크기 변경 또는 패딩을 적용했던 박스가 원본 영상 좌표에 맞는지 확인합니다.

## 검증할 항목

텐서 이름, 형상 프로파일, 색 채널 순서, 엔진 호환성과 영상 크기 변환을 확인합니다. 전후처리를 포함한 전체 지연을 측정합니다. Triton 모델 설정과 TensorRT 엔진 파일은 ROS 그래프와 별도입니다.

## 공개 범위와 라이선스

코드 Apache-2.0; 런타임·모델 별도.

## 공식 자료

- [패키지 개요와 노드 그래프](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_inference/index.html)
- [ROS 패키지 소스](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference)
