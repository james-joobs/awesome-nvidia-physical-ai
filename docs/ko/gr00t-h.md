# GR00T-H 코드

[← 목록으로](../../README.ko.md) · [English](../en/gr00t-h.md)

GR00T-H는 의료 로봇 연구를 위해 GR00T VLA 스택을 적응시킨 모델입니다. 저장소는 GR00T-H-N1.7과 N1.6 기반의 이전 GR00T-H 체크포인트를 구분하며, 각 모델의 이용 조건이 다릅니다. 의료용 N1.7 모델은 Open-H 전체의 모든 센서와 로봇을 학습한 것이 아니라 수술 시연 하위 집합으로 후속 학습했습니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **입력과 로봇 형태** | 정책에는 RGB 관측, 작업 지시, 로봇 상태가 들어갑니다. 구체적인 입력은 로봇 형태 설정에 따라 달라집니다. N1.7 모델 카드에는 후속 학습에 사용한 카메라와 상대 말단 장치 규약이 나옵니다. |
| **공통 VLA 아키텍처** | Cosmos Reason2가 영상과 텍스트를 인코딩합니다. 로봇 형태별 투영이 상태와 행동을 처리하고, 흐름 정합 트랜스포머가 연속값 행동 묶음을 생성합니다. |
| **Open-H 후속 학습** | Open-H는 여러 로봇 플랫폼의 동기화된 영상·운동학 기록을 담습니다. GR00T-H-N1.7 모델 카드는 601시간의 수술 시연 하위 집합과 표준화된 상대 말단 장치 행동을 설명합니다. |

![저장소는 기반 N1.7의 구성도를 제공합니다. 모델 구조는 기반 모델에서 이어받고, 의료 분야 특화는 모델 카드에 설명된 Open-H 후속 학습에서 이루어집니다.](https://raw.githubusercontent.com/NVIDIA-Medtech/GR00T-H/main/media/model-architecture.png)

저장소는 기반 N1.7의 구성도를 제공합니다. 모델 구조는 기반 모델에서 이어받고, 의료 분야 특화는 모델 카드에 설명된 Open-H 후속 학습에서 이루어집니다. [공식 그림 출처](https://github.com/NVIDIA-Medtech/GR00T-H)

![Open-H 모음 사진에서 원본 데이터셋의 다양한 로봇과 시점을 볼 수 있습니다. 특정 체크포인트의 요구 필드는 로봇 형태별 자료에서 확인합니다.](https://raw.githubusercontent.com/NVIDIA-Medtech/GR00T-H/main/media/open-h-collage.jpg)

Open-H 모음 사진에서 원본 데이터셋의 다양한 로봇과 시점을 볼 수 있습니다. 특정 체크포인트의 요구 필드는 로봇 형태별 자료에서 확인합니다. [공식 그림 출처](https://github.com/NVIDIA-Medtech/GR00T-H)

## 적용 예시

1. 공식 CMR Versius 예시에서 기록한 궤적과 대응 로봇 형태 태그를 사용합니다. 독립 추론을 실행해 예측 행동 시퀀스를 평가용 운동학 기록과 비교합니다.
2. 지원되는 다른 연구 작업으로 미세조정할 때는 체크포인트를 비교하기 전에 기구 좌표계, 사용 가능한 시점, 주석 범위를 확인합니다.

## 검증할 항목

- 모델 카드에서 전체 자료의 범위와 학습에 사용한 범위를 구분합니다. 의료 로봇 연구에 대한 용도 및 적용 범위 제한을 확인합니다.
- 코드는 Apache-2.0입니다. N1.7 모델 카드는 NVIDIA Open Model License를, 초기 GR00T-H 가중치는 NVIDIA OneWay Noncommercial License를 명시합니다.

## 공식 자료와 이용 조건

코드는 Apache-2.0입니다. 두 모델 변형과 Open-H 데이터셋의 조건은 각각 별도입니다.

- [GR00T-H 코드·예제·버전별 조건](https://github.com/NVIDIA-Medtech/GR00T-H)
- [GR00T-H-N1.7 모델 카드](https://huggingface.co/nvidia/GR00T-H-N1.7)
- [Open-H 데이터셋 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment)

## 연관 상세 페이지

[GR00T N1.7](groot-model.md) · [LeRobot](lerobot.md)
