# LeRobot

[← 목록으로](../../README.ko.md) · [English](../en/lerobot.md)

LeRobot은 로봇·조작기 인터페이스, 에피소드 저장, 정책 학습과 평가를 연결합니다. 데이터셋은 수집과 학습의 접점입니다. 정책은 데이터셋과 학습 설정에 선언한 특징 이름과 시간 오프셋을 바탕으로 관측과 행동을 선택합니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **기록** | 지원 로봇과 조작기가 상태·행동 벡터를 제공합니다. 카메라 관측에는 이름이 붙습니다. 에피소드는 이들을 작업·시간 정보와 함께 저장해 재생과 학습에 사용합니다. |
| **LeRobotDataset v3** | 표 형식 시계열은 Parquet, 영상은 MP4에 저장합니다. 여러 에피소드가 파일을 공유할 수 있고, 메타데이터가 에피소드 경계와 카메라 스트림 위치를 기록합니다. |
| **데이터 로더와 정책** | 데이터셋 API는 정책에 샘플과 시계열 구간을 제공합니다. 학습 환경은 데이터를 로컬에서 읽거나, 지원되는 v3 구성에서 허브로부터 스트리밍합니다. |

![공식 형식 그림에는 v3 데이터셋을 이루는 데이터, 영상, 메타데이터가 표시됩니다. 에피소드마다 별도 파일이 있다고 가정하지 말고 메타데이터로 위치를 찾습니다.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/lerobotdataset-v3/asset1datasetv3.png)

공식 형식 그림에는 v3 데이터셋을 이루는 데이터, 영상, 메타데이터가 표시됩니다. 에피소드마다 별도 파일이 있다고 가정하지 말고 메타데이터로 위치를 찾습니다. [공식 그림 출처](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

![스트리밍 그림은 전체 데이터를 미리 내려받지 않고 학습에 필요한 샤드를 읽는 방식을 설명합니다.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/lerobotdataset-v3/streaming-lerobot.png)

스트리밍 그림은 전체 데이터를 미리 내려받지 않고 학습에 필요한 샤드를 읽는 방식을 설명합니다. [공식 그림 출처](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

## 적용 예시

1. 관측 카메라의 이름을 정하고 SO-101 시연을 짧게 기록합니다. 에피소드를 시각화해 카메라 프레임, 관절 관측, 행동이 맞물리는지 확인합니다.
2. 동일한 카메라·행동 스키마로 지원되는 정책을 학습합니다. 수집 규모를 늘리기 전에 평가용 에피소드와 정책이 제어하는 롤아웃을 비교합니다.

## 검증할 항목

- 카메라 특징 이름, 프레임률, 단위, 행동 순서를 점검합니다. 카메라 채널이나 관절 순서가 바뀌어도 스키마를 읽는 데 성공할 수 있습니다.
- 대상 학습 도구가 지원하는 데이터 형식을 확인합니다. 예를 들어 GR00T N1.7 저장소는 v3에서 자체 v2 기반 형식으로 변환하는 도구를 제공합니다.

## 공식 자료와 이용 조건

Hugging Face는 저장소 코드를 Apache-2.0으로 공개합니다. 허브의 데이터셋과 모델에는 각각의 조건이 적용됩니다.

- [LeRobot 소스와 지원 정책](https://github.com/huggingface/lerobot)
- [LeRobotDataset v3 설계](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)
- [학습 중 스트리밍](https://huggingface.co/docs/lerobot/main/training_dataset_streaming)

## 연관 상세 페이지

[Isaac Capture](isaac-capture.md) · [Isaac GR00T](isaac-gr00t.md)
