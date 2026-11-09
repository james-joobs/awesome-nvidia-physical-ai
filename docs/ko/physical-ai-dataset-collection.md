# NVIDIA Physical AI dataset collection

[전체 목록](../../README.ko.md) · [English](../en/physical-ai-dataset-collection.md)

NVIDIA Physical AI 컬렉션은 로봇, 자율주행, 시뮬레이션 등에서 사용할 데이터셋을 찾는 시작점이다. 실제 파일 구성과 접근 조건, 권장 사용 목적은 각 데이터셋 카드에서 확인한다.

## 필요한 데이터 종류로 고르기

| 질문 | 시작 페이지 | 작은 표본으로 확인할 것 |
|---|---|---|
| 시뮬레이터에 물체를 배치할 수 있는가? | [3D 자산과 환경](datasets-3d-assets.md) | USD·MJCF 표현, 상대 경로, 크기, 충돌체와 관절 |
| 이 기록으로 로봇 정책을 학습할 수 있는가? | [로봇 시연과 동작](datasets-robot-demonstrations.md) | 로봇 형태, 관측과 행동 배열, 언어 지시, 시간과 카메라 |
| 장면을 재생하거나 영상 모델을 평가할 수 있는가? | [자율주행·월드 모델](datasets-driving-world-model.md) | 재생 시 보정과 센서 정렬, 평가 시 과제별 분할과 지표 |
| 특정 레시피를 재현할 수 있는가? | [V2D 및 Cosmos 데이터](datasets-v2d-cosmos.md) | 모델 조건, 학습 목표, 벤치마크 입력 중 무엇을 담았는지 |

## 활용 예시 — 재현 가능한 로봇 데이터 표본 만들기

데이터셋 하나를 고르고 카드 URL, 버전, 파일 목록, 접근 조건과 사용 목적을 기록한다. 데이터 로더로 에피소드 하나를 읽고 관측을 재생해 행동 차원과 단위를 확인한 뒤 배치를 늘린다. 작업이나 세션별로 분리할 때 생성 변형은 원본 에피소드와 같이 둔다. 예를 들어 G1 원격 조작은 HDF5와 MP4를 쓰고, Human-1M은 Parquet와 영상을 담은 LeRobot v3 샤드를 사용한다. [G1 데이터 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1) · [Human-1M 데이터 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)

접근 및 이용 조건은 항목별로 확인한다. [NVIDIA 컬렉션](https://huggingface.co/collections/nvidia/physical-ai) · [NVIDIA 데이터셋 목록](https://huggingface.co/nvidia/datasets)
