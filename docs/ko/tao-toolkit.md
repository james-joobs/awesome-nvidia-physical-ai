# TAO Toolkit

[← 전체 목록](../../README.ko.md) · [English](../en/tao-toolkit.md)

TAO Toolkit은 비전 모델을 작업별 데이터에 맞춰 학습하고 배포용으로 내보내는 워크플로를 제공합니다.

![TAO Toolkit 개요](https://docs.nvidia.com/tao/tao-toolkit/latest/_images/tao_overview_image.png)

*공식 개요에서 학습과 내보내기가 배포 흐름의 어디에 위치하는지 확인할 수 있습니다.* [공식 그림 출처](https://docs.nvidia.com/tao/tao-toolkit/latest/text/overview.html)

![TAO 소프트웨어 스택](https://docs.nvidia.com/tao/tao-toolkit/latest/_images/tao_stack.png)

*TAO 워크플로가 하위 가속 소프트웨어 위에서 동작하는 구조를 보여줍니다.* [공식 그림 출처](https://docs.nvidia.com/tao/tao-toolkit/latest/text/overview.html)

## 어떻게 동작하나

학습 명세에서 모델, 데이터셋과 최적화 설정을 선택합니다. 지원 사전학습 체크포인트로 초기화한 뒤 정답이 있는 검증 데이터에서 평가합니다. 작업별 형식으로 내보내고, 호환 산출물은 공식 배포 절차에 따라 TensorRT와 DeepStream에서 활용할 수 있습니다.

## 실전 워크플로

[Replicator](replicator.md)로 라벨이 있는 영상을 생성하고 컨베이어 부품 탐지기를 학습합니다. 실제 카메라 검증 세트를 따로 확보해 사전학습 모델과 비교하고, 내보낸 후 일부 예측을 배포 환경에서 재현합니다.

## 검증할 항목

클래스 정의, 데이터 형식, 학습·검증 장면 중복과 실제 카메라 조건을 확인합니다. 학습과 배포의 전후처리를 일치시키고 선택한 워크플로의 호환성과 모델 약관을 확인합니다.

## 공개 범위와 라이선스

제품·SDK; 모델과 구성 요소별 조건 확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://docs.nvidia.com/tao/tao-toolkit/latest/text/overview.html)
- [관련 공식 자료 · docs.nvidia.com](https://docs.nvidia.com/tao/tao-toolkit/latest/text/reference_workflows/index.html)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/tao-toolkit)
