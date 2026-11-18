# 로봇 파운데이션 모델 선택과 평가

[← 모델 목록](../../CATALOG.ko.md#로봇-파운데이션-모델과-vla) · [English](../en/robot-foundation-models.md)

먼저 어떤 로봇으로 어떤 작업을 시험할지 정하세요. 카메라 구성과 그리퍼가 맞는 체크포인트나 벤치마크용 체크포인트로 공식 예제를 재현합니다. 처음 얻은 결과를 기준으로 삼으면 새 시연을 모으거나 파인튜닝한 뒤 얼마나 나아졌는지 비교할 수 있습니다.

| 가지고 있는 것 | 시작점 | 처음 확인할 결과 |
|---|---|---|
| SO-100 또는 SO-101 시연 | [LeRobot의 SmolVLA](https://huggingface.co/docs/lerobot/smolvla) 또는 로봇에 맞는 [MolmoAct 2](https://huggingface.co/allenai/MolmoAct2) 체크포인트 | 관절 순서와 그리퍼 규약이 일치하는 행동 시퀀스 |
| LIBERO 시뮬레이션 벤치마크 | [π₀.₅-LIBERO](physical-intelligence-pi.md) 또는 [Cosmos Policy LIBERO](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B) | 체크포인트가 지원하는 벤치마크 작업의 실행 결과 |
| DROID 관측 샘플 | [GR00T N1.7](groot-model.md), [π₀.₅-DROID](physical-intelligence-pi.md) 또는 [Cosmos 3 Edge Policy DROID](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) | 샘플의 관측 스키마와 일치하는 궤적 |
| Isaac Lab 조작 환경 | 정책 인터페이스가 맞는 [Isaac Lab-Arena](isaac-lab-arena.md) | 고정된 장면 변형과 재현 가능한 초기화 조건에서 측정한 성공률 |

## 관측값을 행동으로 바꾸고 평가하기

1. **입력을 맞춥니다.** 체크포인트와 공식 예제에서 카메라 이름과 순서, 이미지 전처리, 지시문, 로봇 상태 필드와 정규화 방식을 확인합니다.
2. **폐루프 실행 전에 행동 출력을 해석합니다.** 단위, 좌표계, 절대·상대 목표, 관절 순서, 그리퍼 규약을 확인합니다. 추론 한 번에 몇 스텝을 예측하는지, 다음 관측을 받기 전 그중 몇 스텝을 실행하는지 기록합니다.
3. **공식 예제를 재현해 기준 결과를 남깁니다.** 체크포인트 버전, 대상 로봇, 행동 주기, 추론 지연, 성공 기준과 초기화 조건을 저장합니다. 이후 물체 위치나 조명처럼 작업 조건을 하나씩 바꿔 같은 절차로 평가합니다.
4. **접근 방법과 이용 조건을 확인합니다.** 코드 라이선스와 사용할 체크포인트의 모델 카드를 각각 읽고, 해당할 경우 백본과 데이터 조건도 확인합니다. 공개 연구 페이지, 호스팅 API, 다운로드 가능한 가중치는 재현 방법이 각각 다릅니다.

### 같은 지시를 받은 다른 로봇도 바로 움직일 수 있을까요?

VLA는 보통 카메라 영상, 작업 지시, 체크포인트가 요구하는 로봇 상태를 받아 행동을 예측합니다. 여러 시점의 행동을 묶어 예측하면 **액션 청크**라고 부릅니다. 설명용 배열 `[8, 7]`은 여덟 시점마다 일곱 값이 있다는 뜻입니다. 어느 열이 어떤 축이나 관절인지, 절대 목표인지 변화량인지, 실제 단위인지 정규화된 값인지는 모델과 로봇의 설정으로 확인합니다.

GR00T N1.6-DROID는 DROID에 맞춘 제어 규약을 쓰고, π 계열도 과제에 맞는 체크포인트와 관측 어댑터를 씁니다. 같은 모양의 배열도 제어 규약이 다르면 다른 동작을 만들 수 있습니다. 저장된 관측 하나로 입력 키와 배열 모양을 확인한 뒤 시뮬레이션에서 작업 성공 조건을 검사합니다. [GR00T 데이터 설정](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_config.md) · [Physical Intelligence openpi](https://github.com/Physical-Intelligence/openpi)

### GR00T N1.7 시뮬레이션 예제 따라가기

Apache-2.0으로 공개된 참조 워크플로는 Isaac Lab에서 시연을 기록하고 LeRobot 데이터로 변환한 뒤 정책을 파인튜닝하는 과정을 보여줍니다. G1은 사과까지 걸어가 집은 뒤 접시에 놓고, H2 Plus는 사과를 한 손에서 다른 손으로 건넨 뒤 접시에 놓습니다. G1의 모델과 데이터셋을 받으려면 Hugging Face에서 이용 조건에 동의해야 합니다. H2 Plus 자료는 바로 다운로드할 수 있으며, 공식 저장소에서는 학습된 H2 Plus 정책의 평가가 아직 검증되지 않았다고 안내합니다. [공식 워크플로](https://nvidia-isaac.github.io/GR00T-E2E-Reference-Workflow/) · [G1 모델 카드](https://huggingface.co/nvidia/GR00T-E2E-Reference-Workflow-SIM-G1-N1.7-AppletoPlate-Model) · [H2 Plus 모델 카드](https://huggingface.co/nvidia/GR00T-E2E-Reference-Workflow-SIM-H2-N1.7-AppleHandoverPlate-Model)

## Cosmos Policy

초기 [Cosmos Policy](https://github.com/NVlabs/cosmos-policy)는 Cosmos-Predict2를 로봇 조작에 맞게 후학습한 정책입니다. ALOHA 플래닝 경로는 미래 관측과 가치 추정치를 이용해 후보 행동을 비교합니다. [LIBERO 체크포인트](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B#license)에는 NVIDIA One-Way Noncommercial License가 적용되고, 코드는 [Apache-2.0](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LICENSE)입니다.

[Cosmos 3 Edge Policy DROID](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID)와 [Nano Policy DROID](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID)는 OpenMDW-1.1로 공개된 DROID 행동 정책입니다. [Cosmos 3 대화형 시뮬레이션 체크포인트](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation)는 행동이나 시뮬레이션 제어값에서 관측을 생성합니다. 예를 들어 Sim-Bimanual은 로봇이나 카메라의 행동을 받아 다음 관측에 사용할 영상을 예측합니다.

## 다른 VLA

- **OpenVLA**는 7B 조작 기준 모델과 추론·파인튜닝 코드를 제공합니다. 모델 카드에는 MIT가 표시되며, 저장소는 Llama 2 조건도 적용된다고 명시합니다. [모델 카드](https://huggingface.co/openvla/openvla-7b) · [원본 저장소 이용 조건](https://github.com/openvla/openvla#pretrained-vlas)
- **MolmoAct 2**는 깊이 정보를 활용하며 베이스와 로봇별 체크포인트를 제공합니다. 사용할 로봇이나 평가 환경에 맞는 체크포인트를 고릅니다. [모델 카드](https://huggingface.co/allenai/MolmoAct2)
- **X-VLA**는 로봇 기종별 소프트 프롬프트를 사용합니다. 실행할 구현이 지원하는 관측과 행동 방식을 확인합니다. [베이스 모델 카드](https://huggingface.co/2toINF/X-VLA-Pt) · [LeRobot 연동](https://huggingface.co/docs/lerobot/xvla)

## 월드 액션 모델

비디오 액션 모델(VAM)은 영상에서 학습한 특징을 이용해 장면의 변화를 예측하고 로봇 명령을 만듭니다. 공개된 **FLUX-mimic** 구조에서는 작업 지시와 최근 카메라 프레임을 영상 백본에 넣습니다. 행동 예측 모듈은 백본의 중간 특징과 로봇 상태를 받아 궤적을 예측합니다. 학습에는 영상과 행동을 모두 사용합니다. 명령을 만들 때는 영상 노이즈를 한 차례 제거하는 과정에서 얻은 특징을 쓰므로 전체 영상을 생성할 필요는 없습니다. [산업 조작 연구와 구성도](https://www.mimicrobotics.com/blog/video-action-models-for-data-efficient-industrial-manipulation)

| 이름 | 2026년 11월 17일 기준 공개 범위 |
|---|---|
| **FLUX 3** | 이미지·영상·오디오를 다루는 Black Forest Labs의 멀티모달 백본입니다. FLUX-mimic-x, FLUX-mimic, FLUX 3 Action이 이 모델을 기반으로 합니다. [FLUX 3 × mimic 협업 발표](https://bfl.ai/blog/flux-3-mimic) |
| **FLUX-mimic-x** | mimic robotics가 11월 16일(UTC)에 공개한 7B 모델 프리뷰입니다. FLUX 3에 개선된 mimic-video 학습 방식을 적용했습니다. 개발팀은 RoboLab의 실시간 ‘System 1’ 모델 중 1위라고 발표했습니다. 확인 당시 공개 리더보드에는 이 이름의 결과가 없었으며, 다운로드 가능한 코드·가중치와 이용 조건은 미확인입니다. [mimic 공식 발표](https://x.com/mimicrobotics/status/2122343940653224018) · [NVIDIA RoboLab 리더보드](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html) |
| **FLUX-mimic** | mimic robotics와 Black Forest Labs가 앞서 발표한 산업 조작 연구 모델입니다. BMW Group과 진행한 연구에서 영상·행동을 함께 학습하는 구조와 네 가지 작업의 결과를 공개했습니다. 이 모델의 코드·가중치는 공개 여부가 미확인입니다. [논문](https://arxiv.org/abs/2611.15974) · [프로젝트와 시연](https://www.mimicrobotics.com/blog/video-action-models-for-data-efficient-industrial-manipulation) |
| **FLUX 3 Action** | Black Forest Labs가 별도로 공개한 7B 모델입니다. 코드는 Apache-2.0이며, SO-101·DROID 가중치는 Hugging Face 접근 절차와 FLUX Kommunity License v1.0이 적용됩니다. BFL은 NVIDIA의 Jetson 통합 지원과 Isaac Lab·RoboLab을 활용한 평가를 공개 자료에 명시했습니다. [공식 발표와 기술 자료](https://bfl.ai/models/flux-3-action) · [코드](https://github.com/black-forest-labs/flux-action) · [SO-101](https://huggingface.co/black-forest-labs/flux-3-action-so101) · [DROID](https://huggingface.co/black-forest-labs/flux-3-action-droid) |
| **mimic-video** | 앞서 공개한 연구 구현입니다. NVIDIA Cosmos Predict2를 기반으로 하며 코드는 Apache-2.0입니다. 영상 백본을 고정하고 중간 특징에서 행동을 예측하는 모듈을 학습하는 절차가 공개되어 있습니다. 가중치 이용 조건은 각 체크포인트에서 확인합니다. [논문](https://arxiv.org/abs/2512.15692) · [코드](https://github.com/mimic-video/mimic-video) |

### NVIDIA 정책과 비교할 만한 공개 모델

- **Cosmos3-Edge-Policy-DROID(4B)**와 **Cosmos3-Nano-Policy-DROID(16B)**는 NVIDIA가 OpenMDW-1.1로 공개한 DROID 조작 체크포인트입니다. 공식 예제에서 정책을 서버에 띄우고 RoboLab 클라이언트를 연결하는 과정을 확인할 수 있습니다. [Edge](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) · [Nano](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID) · [정책 실행 예제](https://nvidia.github.io/cosmos-framework/action_policy_droid_server/)
- **GR00T 2 / Turbo**는 11월 9일에 발표된 NVIDIA의 Cosmos 기반 월드 액션 모델입니다. NVIDIA Research는 2026년 12월에 코드를 공개할 예정이라고 안내합니다. 다운로드 가능한 가중치와 적용 약관은 아직 확인되지 않았습니다. [연구와 시연](https://research.nvidia.com/labs/gear/gr00t-2/) · [GR00T 가이드](groot-model.md)
- **DreamZero-DROID**는 NVIDIA GEAR가 영상과 행동을 함께 예측하도록 만든 연구용 기준 모델입니다. 참조 코드는 Apache-2.0이며, 모델 카드의 14B 가중치는 다운로드할 수 있고 CC BY-NC 4.0이 적용됩니다. [프로젝트](https://dreamzero0.github.io/) · [코드](https://github.com/dreamzero0/dreamzero) · [체크포인트와 이용 조건](https://huggingface.co/GEAR-Dreams/DreamZero-DROID)
- **Praxis-1**은 영상과 행동을 함께 예측하는 Runway의 27.3B 모델입니다. 코드와 베이스·DROID·YAM 가중치는 Apache-2.0이며, 가중치 다운로드에는 Hugging Face 접근 절차가 있습니다. 11월 11일 공개 자료에 LeRobot 연동과 RTX 5090·Jetson Thor 실행 환경이 안내되어 있습니다. [공식 발표](https://runway.com/news/company-news/praxis-1-is-now-available) · [체크포인트 모음](https://huggingface.co/collections/runwayml/praxis-1)

### 평가 결과에서 무엇을 보면 될까요?

**카메라 프레임 + 작업 지시 + 로봇 상태 → 정책 → 행동 묶음 → 시뮬레이터에서 실행 → 다음 관측.** 물체를 집어 그릇에 넣는 작업을 예로 들면, 정책은 카메라 영상과 현재 자세를 보고 일련의 동작을 내놓습니다. 성공 여부는 시뮬레이터가 명령을 실행하고 난 뒤 물체가 실제로 어디에 놓였는지로 판단합니다. 정책이 따로 예측한 영상은 장면이 어떻게 바뀔지 보여주는 출력입니다.

11월 17일에 확인한 RoboLab 공개 집계에서는 Praxis-1이 **555/1,200회**, FLUX 3 Action이 **515/1,200회**, Cosmos3-Nano-Policy가 **441/1,200회**, Cosmos3-Edge-Policy가 **275/1,200회** 성공했습니다. 모두 시뮬레이션에서 발표된 결과입니다. 직접 비교할 때는 정책 버전, 지시문 설정, 평가 횟수, 하드웨어를 함께 기록합니다. [RoboLab-120 리더보드](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html) · [정책 클라이언트 인터페이스](https://github.com/NVlabs/RoboLab/blob/main/policies/README.md) · [브라우저에서 GR00T 실행 결과 판정하기](labs/gr00t-placement.md#first-exercise)

RoboLab v0.3.3에서는 물체의 초기 배치를 시드로 재현하고 조명 프리셋을 선택할 수 있습니다. 같은 조건에서 다시 비교할 수 있도록 성공률과 함께 벤치마크 버전, 시드, 조명 설정을 남깁니다. [v0.3.3 릴리스 노트](https://github.com/NVlabs/RoboLab/releases/tag/v0.3.3)

## 최근 월드 액션 연구

| 연구 | 파이프라인에서 하는 일 | 확인하거나 활용할 수 있는 자료 |
|---|---|---|
| **ThinkWAM** (11월 16일) | 행동 묶음을 먼저 예측하고, 그 행동을 했을 때의 장면을 잠재 표현에서 갱신합니다. 갱신된 표현을 바탕으로 실행할 행동을 한 번 더 계산합니다. | 원본 코드 MIT, 포함된 SIGReg는 CC BY-NC 4.0. 공개 가중치에는 Apache-2.0이 적용되며 전용 평가 설정을 제공합니다. [논문](https://arxiv.org/abs/2611.21258) · [코드와 외부 구성 요소 약관](https://github.com/HaoyunT/Thinkwam#license) · [체크포인트](https://huggingface.co/Adrain11/ThinkWAM) |
| **VLALagBench** (11월 16일 개정) | 물체가 계속 움직이는 시뮬레이션에서 일부러 추론 지연을 주고, LIBERO의 동기·비동기 실행 방식에 따라 성공률이 어떻게 달라지는지 비교합니다. Isaac Sim에서도 일부 조건을 교차 확인했습니다. | 벤치마크 코드와 결과 공개. 원본 코드·데이터·문서는 CC BY-NC 4.0이며 모델과 시뮬레이터 에셋은 별도 조건입니다. [논문](https://arxiv.org/abs/2611.03103v2) · [저장소와 라이선스](https://github.com/codestrongestx/vla-lag-bench#license) |
| **Ego2Sim2Humanoid** (11월 14일) | 1인칭 RGB-D 촬영 기록에서 시뮬레이션용 로봇 카메라 영상과 실행 가능한 전신 궤적을 만듭니다. 연구팀은 이 데이터로 GR00T N1.7을 파인튜닝해 Unitree G1의 이동과 조작을 시험했습니다. | 논문과 평가 결과 그림 공개. 코드·데이터셋·파인튜닝 체크포인트 공개 여부 미확인. [논문](https://arxiv.org/abs/2611.19196) |
| **FOVI-Dex** (11월 12일) | NVIDIA 공동 연구팀은 카메라가 주시하는 영역을 정밀하게 렌더링하면서 주변 시야도 유지합니다. 관측 한 장에 드는 비용을 줄여 여러 시뮬레이션에서 물체 집기 정책을 병렬로 학습합니다. | 논문과 평가 영상 공개. 코드·가중치 공개 여부와 이용 조건 미확인. [NVIDIA Research](https://research.nvidia.com/publication/2026-11_fovi-dex-foveation-enables-efficient-perceptive-learning-dexterous-manipulation) · [프로젝트](https://fovi-dex.github.io/) |
| **SWAM** (11월 11일 개정) | 영상에는 언어와 장면의 관계를 학습시키고, 행동 정보가 있는 사람·로봇 시연에는 행동 학습을 더합니다. 영상과 행동 모듈은 어텐션으로 특징을 주고받습니다. | Apache-2.0 코드와 사전 학습 데이터 일부를 공개했습니다. 데이터는 원본별 조건이 적용되며 정책 가중치의 다운로드 가능 여부와 이용 조건은 미확인입니다. [논문](https://arxiv.org/abs/2611.12870v2) · [코드](https://github.com/shaaaaron/SWAM) · [데이터 조건](https://huggingface.co/datasets/FreDERicia/SWAM-Pretrain#source-terms-and-attribution) |
| **WISE** (11월 2일) | 모델을 다시 학습시키지 않고 여러 후보를 생성해 행동의 유효성, 예측 영상과 행동의 일치, 작업 진행도를 점검합니다. 논문은 후보를 네 개 썼을 때 Cosmos 3 Edge의 RoboLab 일부 과제에서 성공률이 6%에서 24%로, 에피소드 실행 시간이 약 3.4배로 늘었다고 보고합니다. | 프리프린트와 평가 절차 공개. 코드 공개 여부 미확인. [논문](https://arxiv.org/abs/2611.03585) |
| **DemoStream** (CoRL 2026 워크숍) | NVIDIA와 공동 연구팀이 과제 계획과 동작 최적화를 병렬 처리해, 시뮬레이션에서 정책 학습에 쓸 성공 시연을 만듭니다. | 공식 연구 페이지와 논문 공개. 코드와 시연 데이터셋 공개 여부 미확인. [NVIDIA Research](https://research.nvidia.com/publication/2026-11_demostream-batched-task-and-motion-plan-optimization-automated-learning) · [논문](https://arxiv.org/abs/2610.22020) |
| **FlashRT-PAI** (2026년 10월) | 연산을 합치고 런타임 실행 순서를 조정해 전체 추론을 가속합니다. 외부 프로젝트이며 GR00T N1.7, Cosmos3-Edge용 실행 경로를 제공합니다. | 코드 Apache-2.0. 지연 시간을 비교할 때 모델·GPU·정밀도·런타임을 확인합니다. [논문](https://arxiv.org/abs/2610.24349) · [FlashRT 저장소](https://github.com/flashrt-project/FlashRT) |
| **ARC** (10월 8일) | NVIDIA가 참여한 연구입니다. DROID 시연에 ‘왜 이 행동이 필요한가’를 설명하는 추론 라벨을 달고, 이를 이용해 π₀.₅와 Cosmos3-Nano-Policy를 후학습합니다. | 코드·모델·데이터셋·RoboLab-Reasoning-50은 공개 예정으로 안내되어 있습니다. [프로젝트와 공개 상태](https://arc-robot-reasoning.github.io/) · [논문](https://arxiv.org/abs/2610.12386) |

[GR00T 모델 계열](groot-model.md) · [Physical Intelligence π](physical-intelligence-pi.md) · [LeRobot](lerobot.md) · [Isaac Lab](isaac-lab.md) · [Alpamayo 주행 VLA](alpamayo.md)
