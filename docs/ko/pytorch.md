# PyTorch

[← 전체 목록](../../README.ko.md) · [English](../en/pytorch.md)

PyTorch는 이 목록의 여러 모델에서 사용하는 텐서 연산, 자동 미분, 신경망 구성 요소를 제공합니다.

![PyTorch 자동 미분 연산 그래프](https://docs.pytorch.org/tutorials/_images/comp-graph.png)

*순방향 연산의 의존 관계를 역전파에서 기울기 전파에 사용합니다.* [공식 그림 출처](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)

## 어떻게 동작하나

데이터셋과 로더가 텐서 배치를 공급합니다. 모듈이 예측을, 손실 함수가 예측 점수를 계산하며, 자동 미분이 미분 가능한 연산을 추적해 기울기를 구합니다. 옵티마이저는 기울기로 파라미터를 갱신합니다. 배포 시 체크포인트를 저장하거나 지원 연산을 별도 런타임으로 내보낼 수 있습니다.

## 실전 워크플로

로봇 카메라 라벨 영상으로 탐지기를 파인튜닝합니다. 먼저 아주 작은 배치에 과적합시켜 라벨과 기울기 흐름을 점검합니다. 모델과 전처리 설정을 함께 저장하고 배포 내보내기 전후 예측을 비교합니다.

## 검증할 항목

장치, 데이터 타입, 텐서 레이아웃과 학습·평가 모드를 확인합니다. 데이터 로더와 별도로 기울기를 시험하고 내보내기 지원 연산과 수치 일치도를 검증합니다.

## 공개 범위와 라이선스

PyTorch는 BSD 계열 라이선스이며 모델·패키지·CUDA 런타임 등 의존성의 조건은 별도입니다.

## 공식 자료

- [공식 기술 자료](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)
- [관련 공식 자료 · github.com](https://github.com/pytorch/pytorch)
- [관련 공식 자료 · docs.pytorch.org](https://docs.pytorch.org/docs/stable/index.html)
