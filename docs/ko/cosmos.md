# Cosmos 및 Cosmos 3

[← 프로젝트 홈](../../README.ko.md) · [English](../en/cosmos.md)

<p align="center">
  <img src="../../assets/project-marks/cosmos.png" width="210" alt="NVIDIA Cosmos 로고"><br>
  <sub><a href="https://github.com/NVIDIA/cosmos/blob/71317702510f7c456ba3d702b84fb103546caea2/assets/brand/cosmos-logo.png">NVIDIA Cosmos 공식 로고</a></sub>
</p>

Cosmos는 영상과 센서 데이터를 생성하거나 해석하는 데 쓰는 NVIDIA의 피지컬 AI 플랫폼입니다. Cosmos 3 모델은 멀티모달 추론과 생성을 지원합니다. 데이터를 골라내고 모델을 학습시키거나 생성 결과를 평가하는 도구도 있습니다.

NVIDIA는 2026년 11월 [대화형 시뮬레이션 체크포인트](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation) 네 종을 OpenMDW-1.1로 공개했습니다. Sim-Bimanual은 로봇이나 카메라 행동에서 영상을 예측하고, Sim-Transfer는 시뮬레이터 제어값으로 영상을 생성합니다. Sim-Auto와 Transfer-Auto는 주행 워크플로에 사용합니다. 로봇 행동을 출력하는 모델은 [Cosmos Policy 목록](robot-foundation-models.md#cosmos-policy)에서 확인할 수 있습니다.

## 공식 아키텍처 읽기

![Cosmos 3의 Reasoner와 Generator 아키텍처](https://raw.githubusercontent.com/NVIDIA/cosmos/main/docs/assets/cosmos3-model-architecture.png)

Reasoner와 Generator는 표현을 공유하며 함께 학습하는 두 Transformer 타워입니다. Reasoner는 언어 요청을 영상 속 맥락과 연결합니다. Generator는 해석된 맥락과 생성 조건을 이용해 체크포인트가 지원하는 결과를 만듭니다. NIM 이미지에는 Reasoner와 Generator 런타임이 따로 있어, 내부 모델 구성을 이해한 뒤에도 호출별 입력 규격을 구분해야 합니다. [NVIDIA 기술 보고서](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf) · [NIM 아키텍처](https://docs.nvidia.com/nim/cosmos/latest/overview.html)

오른쪽 어텐션 마스크에서 보라색은 인과적 범위를 뜻합니다. Reasoner는 앞선 시각·언어 토큰을 보고 다음 텍스트를 예측합니다. 주황색은 Generator의 확산 토큰이 두 토큰 그룹을 모두 참조하는 범위입니다. 영상은 해당 분기의 시각 VAE를 거치고, 오디오와 행동에는 별도 인코더가 있습니다. 이렇게 Generator는 Reasoner가 해석한 맥락을 쓰고, Reasoner는 자체적으로도 동작합니다. [Cosmos 3 기술 보고서의 모델 아키텍처](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf)

| 작업 | 입력 | 출력 |
|---|---|---|
| 추론 | 영상과 물체의 움직임에 관한 질문 | 서빙 설정에 따른 텍스트 또는 구조화된 관찰 결과 |
| 순방향 동역학 | 초기 관측과 체크포인트 형식에 맞춘 행동 시퀀스 | 주어진 행동을 조건으로 생성한 롤아웃 |
| 변환 | 프롬프트와 지원되는 공간 제어 데이터 | 제공한 장면 배치를 따르도록 생성한 영상 |
| 정책 | 대상 로봇에 맞춘 카메라 뷰, 작업, 상태 | 해당 체크포인트의 표현으로 기록된 행동 예측 |

체크포인트마다 프레임 수, 입력 매체, 행동 차원을 확인합니다. Super, Nano, Edge는 계열 아키텍처를 공유하며 지원 작업과 추론 통합 방식에는 차이가 있습니다. [공식 모델 레퍼런스](https://docs.nvidia.com/cosmos/latest/cosmos3/model_reference.html)

### 같은 주행 영상이라도 과제에 따라 출력이 달라집니다

“차선을 바꾼 시점은 언제인가요?”라고 묻는다면 영상에 대한 설명을 기대합니다. 비가 오는 장면으로 바꾸고 싶다면, 선택한 생성 체크포인트가 지원하는 장면 조건과 프롬프트를 넣고 카메라 경로와 차선 배치가 유지됐는지 봅니다. 행동을 조건으로 주는 실험이라면 행동 순서를 바꿔 예측 영상이 어떻게 달라지는지 살펴봅니다.

실험 기록에는 **원본 클립 ID, 체크포인트, 작업 유형, 조건 또는 질문, 출력 파일**을 함께 적습니다. API 입력 형식은 선택한 체크포인트 문서를 확인하세요. 생성 영상에서 조건을 따랐는지 먼저 평가하고, 충돌 같은 물리 사건은 시뮬레이션 상태나 별도 관측 기록에서 확인합니다. [Cosmos 3 모델 레퍼런스](https://docs.nvidia.com/cosmos/latest/cosmos3/model_reference.html)

## 활용 예시 — 자율주행 장면 변형

![Cosmos 3의 주행 장면 제어 예제](https://raw.githubusercontent.com/NVIDIA/cosmos/main/assets/demos/transfer_worldscenario.gif)

NVIDIA 예제에는 주행 장면의 공간 제어 입력과 생성 영상이 함께 나옵니다. 실험에서는 카메라 경로와 배치 조건을 고정하고 날씨 프롬프트를 바꾼 뒤, 생성 영상의 객체 위치, 차선 배치, 움직임 타이밍을 원래 조건과 비교합니다. 모델 버전, 시드, 원본 시퀀스 ID를 결과마다 기록하고, 실제 주행 데이터에서 촬영 세션 단위로 분리한 검증 세트로 성능 변화를 측정합니다. 충돌이나 접촉 여부는 적합한 시뮬레이터나 관측 기록에서 확인합니다. [공식 예제와 레시피](https://github.com/NVIDIA/cosmos) · [Cosmos Evaluator](cosmos-evaluator.md)

## 공개 및 이용 조건

Cosmos 3 저장소는 코드와 모델에 OpenMDW-1.1을 명시합니다. 이전 [Predict2](cosmos-predict2.md), [Reason2](cosmos-reason2.md) 저장소는 각각 이용 조건을 안내합니다. [공식 라이선스](https://github.com/NVIDIA/cosmos#citation--license)

## 연관 도구

체크포인트별 학습·후학습·서빙 레시피는 [Cosmos Framework](cosmos-framework.md)를, 패키지형 추론 엔드포인트는 [NVIDIA NIM](nvidia-nim.md)을 참고하세요.
