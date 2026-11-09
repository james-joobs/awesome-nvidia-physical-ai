# GR00T-Mimic / GR00T-Dreams

[← 목록으로](../../README.ko.md) · [English](../en/groot-mimic-dreams.md)

GR00T-Mimic과 GR00T-Dreams는 서로 다른 입력으로 로봇 학습 데이터를 확장합니다. 공개 Mimic 블루프린트는 기록된 시연을 시뮬레이션에서 증강합니다. Dreams의 DreamGen 구현은 Cosmos 월드 모델로 로봇 영상을 만들고 그에 대응하는 행동 라벨을 추정합니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **Mimic 블루프린트** | 원격 조작에서 원본 행동과 장면을 얻습니다. Isaac Lab과 Isaac Sim이 변형 궤적과 시각 관측을 생성합니다. 공개 블루프린트에서는 정책 학습 전에 Cosmos 기반 시각 증강도 수행합니다. |
| **DreamGen 영상 생성 단계** | 로봇 장면 이미지와 언어 지시를 조건으로 영상 월드 모델이 동영상을 생성합니다. 저장소에는 Cosmos Predict2 후속 학습 및 합성 MP4 클립 생성 절차가 나옵니다. |
| **DreamGen 행동 추정 단계** | 역동역학 모델(IDM)이 영상에서 로봇 행동을 추정합니다. 공식 스크립트는 특정 로봇 형태를 지원하며, 결과를 정책 미세조정용 LeRobot 형식으로 변환합니다. |

![Mimic 블루프린트는 원격 조작에서 얻은 시연을 시뮬레이션 궤적과 영상 생성에 넣고, 증강과 학습으로 이어가는 흐름을 보여줍니다.](https://developer-blogs.nvidia.com/wp-content/uploads/2025/01/nvidia-isaac-groot-blueprint-architecture-1024x446.png)

Mimic 블루프린트는 원격 조작에서 얻은 시연을 시뮬레이션 궤적과 영상 생성에 넣고, 증강과 학습으로 이어가는 흐름을 보여줍니다. [공식 그림 출처](https://developer.nvidia.com/blog/building-a-synthetic-motion-generation-pipeline-for-humanoid-robot-learning/)

![Dreams 참조 아키텍처는 생성 영상과 추정 행동을 분리해 보여줍니다. 대상 정책이 로봇 행동 라벨을 요구하는 경우 후자의 단계가 필요합니다.](https://raw.githubusercontent.com/NVIDIA/GR00T-Dreams/main/reference_architecture/reference_architecture_diagram.png)

Dreams 참조 아키텍처는 생성 영상과 추정 행동을 분리해 보여줍니다. 대상 정책이 로봇 행동 라벨을 요구하는 경우 후자의 단계가 필요합니다. [공식 그림 출처](https://github.com/NVIDIA/GR00T-Dreams/blob/main/reference_architecture/reference_architecture.md)

## 적용 예시

1. 기존 시연과 수정 가능한 장면이 있는 집기·놓기 작업이라면 Mimic 방식으로 물체 자세 변화에 맞춰 원본 궤적을 변형합니다.
2. 시작 이미지로 새 환경을 탐색할 때는 지원 로봇 형태로 DreamGen 경로를 사용합니다. 학습 전에 생성 영상을 선별하고 추정 행동을 점검합니다.

## 검증할 항목

- 작업 지시 준수와 물리적 타당성을 따로 살펴봅니다. 영상은 자연스러워도 추정한 로봇 동작이 실행 불가능할 수 있습니다.
- DreamGen 절차는 해당 저장소에 명시된 모델 버전을 대상으로 합니다. 다른 GR00T 릴리스에서 결과를 재사용하기 전에 행동 스키마와 체크포인트 호환성을 확인합니다.

## 공식 자료와 이용 조건

GR00T-Dreams 저장소의 DreamGen 구현은 Apache-2.0을 적용합니다. 기반 모델과 데이터셋의 조건은 별도로 확인합니다. Mimic 블루프린트에서 연결하는 도구의 조건은 구성 요소마다 다릅니다.

- [NVIDIA GR00T-Mimic 블루프린트와 실제 예제](https://developer.nvidia.com/blog/building-a-synthetic-motion-generation-pipeline-for-humanoid-robot-learning/)
- [GR00T-Dreams 구현과 지원 로봇 형태](https://github.com/NVIDIA/GR00T-Dreams)
- [DreamGen 연구와 벤치마크](https://research.nvidia.com/labs/gear/dreamgen/)

## 연관 상세 페이지

[MimicGen](mimicgen.md) · [Cosmos Predict2](cosmos-predict2.md) · [Isaac GR00T](isaac-gr00t.md)
