# 로봇 파운데이션 모델 선택과 평가

[← 모델 목록](../../README.ko.md#로봇-파운데이션-모델과-vla) · [English](../en/robot-foundation-models.md)

평가할 수 있는 로봇과 작업부터 정합니다. 사용할 카메라·그리퍼·벤치마크와 맞는 체크포인트를 고르면, 새 시연을 수집하거나 범용 모델을 파인튜닝하기 전에 재현 가능한 기준 결과를 얻을 수 있습니다.

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

## Cosmos Policy

초기 [Cosmos Policy](https://github.com/NVlabs/cosmos-policy)는 Cosmos-Predict2를 로봇 조작에 맞게 후학습한 정책입니다. ALOHA 플래닝 경로는 미래 관측과 가치 추정치를 이용해 후보 행동을 비교합니다. [LIBERO 체크포인트](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B#license)에는 NVIDIA One-Way Noncommercial License가 적용되고, 코드는 [Apache-2.0](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LICENSE)입니다.

[Cosmos 3 Edge Policy DROID](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID)와 [Nano Policy DROID](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID)는 OpenMDW-1.1로 공개된 DROID 행동 정책입니다. [Cosmos 3 대화형 시뮬레이션 체크포인트](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation)는 행동이나 시뮬레이션 제어값에서 관측을 생성합니다. 예를 들어 Sim-Bimanual은 로봇이나 카메라의 행동을 받아 다음 관측에 사용할 영상을 예측합니다.

## 다른 VLA

- **OpenVLA**는 7B 조작 기준 모델과 추론·파인튜닝 코드를 제공합니다. 모델 카드에는 MIT가 표시되며, 저장소는 Llama 2 조건도 적용된다고 명시합니다. [모델 카드](https://huggingface.co/openvla/openvla-7b) · [원본 저장소 이용 조건](https://github.com/openvla/openvla#pretrained-vlas)
- **MolmoAct 2**는 깊이 정보를 활용하며 베이스와 로봇별 체크포인트를 제공합니다. 사용할 로봇이나 평가 환경에 맞는 체크포인트를 고릅니다. [모델 카드](https://huggingface.co/allenai/MolmoAct2)
- **X-VLA**는 로봇 형태별 소프트 프롬프트를 사용합니다. 실행할 구현이 지원하는 관측과 행동 방식을 확인합니다. [베이스 모델 카드](https://huggingface.co/2toINF/X-VLA-Pt) · [LeRobot 연동](https://huggingface.co/docs/lerobot/xvla)
## 월드 액션 모델

- **Praxis-1**은 미래 영상과 로봇 행동을 함께 예측합니다. 베이스와 DROID·YAM 체크포인트는 Apache-2.0이며 Hugging Face에서 접근 절차를 거쳐 받을 수 있습니다. [공식 공개 발표](https://runway.com/news/company-news/praxis-1-is-now-available) · [베이스 체크포인트](https://huggingface.co/runwayml/praxis-1-base)

- **FLUX 3 Action**은 DROID·SO-101용 체크포인트를 제공합니다. 코드는 Apache-2.0이고 가중치에는 FLUX Kommunity License가 적용됩니다. [공식 프로젝트](https://bfl.ai/models/flux-3-action) · [SO-101 가중치 약관](https://huggingface.co/black-forest-labs/flux-3-action-so101/blob/main/LICENSE.md)

[GR00T 모델 계열](groot-model.md) · [Physical Intelligence π](physical-intelligence-pi.md) · [LeRobot](lerobot.md) · [Isaac Lab](isaac-lab.md) · [Alpamayo 주행 VLA](alpamayo.md)
