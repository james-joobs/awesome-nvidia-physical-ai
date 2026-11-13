<div align="center">

# Awesome NVIDIA Physical AI

[English](README.md) · **한국어**

**만들고 싶은 결과를 고르고, 필요한 NVIDIA Physical AI 도구와 첫 실행을 위한 공식 예제를 찾으세요.**

시뮬레이션, 로보틱스, 자율주행과 이들이 함께 사용하는 데이터·3D 자산을 연결하는 비공식 커뮤니티 가이드입니다.

[목표별로 시작](#만들고-싶은-것부터-시작하세요) · [생태계 지도](#생태계-한눈에-보기) · [데이터와 자산](#데이터와-시뮬레이션-자산) · [NeMo](#nemo와-물리-ai-도구) · [로봇 모델](#로봇-파운데이션-모델과-vla) · [업스트림 릴리스](#최근-업스트림-릴리스) · [전체 목록](#1-오픈소스-코드가-확인된-프로젝트) · [최신 릴리스](https://github.com/james-joobs/awesome-nvidia-physical-ai/releases/latest)

<img src="assets/social-preview.jpg" alt="Awesome NVIDIA Physical AI 커뮤니티 가이드" width="460">

</div>

## 만들고 싶은 것부터 시작하세요

| 목표 | 시작 경로 | 처음 확인할 결과 |
| --- | --- | --- |
| **시뮬레이션용 3D 장면 만들기** | CAD가 있다면 [작업대 CAD → USD → Isaac Sim](docs/ko/workflows/workbench-cad-to-isaac-sim.md). 작업대 영상이 있다면 [SimFoundry](https://github.com/NVlabs/SimFoundry). | 실제와 같은 치수, 상판 위에 멈추는 큐브 |
| **자율주행 정책 평가하기** | [AlpaSim 폐루프 평가 가이드](docs/ko/workflows/alpasim-closed-loop.md) | 완료된 주행 에피소드와 충돌·도로 이탈 지표 |
| **카메라 장면을 렌더링하고 라벨 만들기** | [SimReady](docs/ko/simready.md) → [Isaac Sim](docs/ko/isaac-sim.md) → [Replicator](docs/ko/replicator.md) | 같은 프레임의 RGB 이미지·깊이·마스크 |
| **실사 장면을 3DGS로 복원하기** | 센서·주행 워크플로는 [NuRec](docs/ko/nurec.md), 복원 실험은 [fVDB Reality Capture](https://github.com/openvdb/fvdb-reality-capture) | 원래 카메라 시점으로 다시 렌더링한 영상과 충돌체가 필요한 영역 |
| **물리 백엔드 고르기** | [Isaac Lab 물리 백엔드](https://docs.nvidia.com/isaaclab/concepts/physics-backends) · [렌더러 호환성](https://docs.nvidia.com/isaaclab/concepts/renderers) | 지원되는 렌더러 조합에서 접촉·관절 테스트 하나 |
| **로봇팔로 물체 집어 옮기기** | [Isaac Manipulator](docs/ko/isaac-manipulator.md) · [Isaac ROS cuMotion](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_cumotion) | 실행 가능한 궤적과 물체를 집고 놓은 결과 |
| **원격조작 시연으로 로봇 정책 학습하기** | [SO-101 공식 과정](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/) · [Isaac Capture](docs/ko/isaac-capture.md) · [Isaac Lab](docs/ko/isaac-lab.md) | 재생할 수 있는 시연 기록과 반복 측정할 수 있는 작업 성공률 |
| **사전 학습된 로봇 정책 고르기** | [로봇 파운데이션 모델과 VLA](#로봇-파운데이션-모델과-vla) · [모델 선택과 평가](docs/ko/robot-foundation-models.md) | 지원 로봇이나 벤치마크를 고르고 재현 가능한 실행 한 번 완료 |
| **공장·창고 디지털 트윈 만들기** | [AIF CAD → USD 예제](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/main/docs/get-started/cad-to-usd-workflow.md) → [Omniverse](docs/ko/omniverse.md) · 다중 로봇은 [Mega Blueprint](https://blogs.nvidia.com/blog/mega-omniverse-blueprint/) | 치수를 검증한 구역 하나와 운영 시나리오 하나 |
| **영상 분석 에이전트 만들기** | [Metropolis VSS](docs/ko/metropolis-vss.md) · 모델 요청을 분기한다면 [Switchyard](docs/ko/nemo-switchyard.md) | 영상의 타임스탬프를 근거로 제시하는 답변 |

**시뮬레이션에서 실물 로봇까지** · [Isaac Lab과 Newton을 사용하는 Microduck](docs/ko/microduck.md) · [브라우저 시뮬레이터](https://huggingface.co/spaces/pollen-robotics/microduck-simulator)

## 생태계 한눈에 보기

가지고 있는 입력에서 출발해 원하는 결과가 나오는 단계까지 따라갑니다. CAD 경로는 라벨이 붙은 프레임에서, 자율주행 경로는 주행 평가 보고서에서, 로봇 학습 경로는 시뮬레이션이나 실기에서 평가한 정책에서 마칠 수 있습니다.

![NVIDIA Physical AI 생태계의 세 경로. CAD와 3D 자산은 시뮬레이션, 렌더링, 디지털 트윈에 쓰이는 OpenUSD 장면이 됩니다. 카메라 영상과 주행 로그는 폐루프 평가용으로 복원한 장면이 됩니다. 원격조작 시연은 로봇 정책 학습용 데이터셋이 됩니다. 평가 결과는 다음 반복에 반영합니다.](assets/ecosystem/physical-ai-ecosystem.ko.svg)

**장면 표현, 물리, 렌더링을 따로 선택합니다.** OpenUSD는 장면을 구성합니다. 3D Gaussian Splatting(3DGS)은 카메라에서 보이는 외형을 표현하고, 충돌체·질량·관절은 물리적 상호작용을 정의합니다. PhysX와 Newton은 시뮬레이션 상태를 계산하고, RTX 렌더링과 센서 시뮬레이션은 관측값을 만듭니다. 도구를 고를 때는 백엔드와 렌더러의 호환성을 확인하세요.

<details>
<summary>공식 도구 자료와 기존 시각 자료 출처</summary>

- **데이터·시뮬레이션** · [V2D](https://nvidia-isaac.github.io/video_to_data/) · [Isaac Sim](https://github.com/isaac-sim/IsaacSim/blob/7c206f75bdadd9e05fc457f19863ca4c3f0cb693/source/deprecated/isaacsim.replicator.domain_randomization/python/nodes/icons/isaac-sim.svg)
- **모델 개발** · [Isaac GR00T](https://github.com/NVIDIA/Isaac-GR00T/blob/7aa0bca50f1097f8b17f5c274c98264b72a1419f/media/header_compress.png) · [Cosmos Framework](https://github.com/NVIDIA/cosmos-framework/blob/5950e7b4ea3677b99a2de279a7ed7058b5446e42/tools/docs/images/cosmos-logo.png)
- **배포·서빙** · [NeMo Switchyard](https://github.com/NVIDIA-NeMo/Switchyard/blob/88fe33e323d48bedc82b4c55920b6764548411fd/experimental/switchyard-desktop/icons/icon.png)
- **단계별 아이콘** · [Lucide](https://lucide.dev/icons/) ([ISC 라이선스](assets/icons/LICENSE))

</details>

확인일: 2026-11-09. 연결된 대화에서 언급된 프로젝트와 추가 조사한 시뮬레이션 자산·데이터셋을 정리했다. NVIDIA 외부 프로젝트도 관련된 경우 포함했다. 공식 저장소와 문서를 기준으로 했으며, 링크에 접속할 수 있다는 사실은 모든 코드·모델·데이터가 같은 조건으로 이용 가능하다는 의미가 아니다.

**분류 기준:** 아래 첫 표는 공개 코드에 대해 오픈소스 라이선스가 확인된 프로젝트다. 코드의 라이선스는 모델 가중치, 데이터, 바이너리, 클라우드 서비스 및 의존성에 자동으로 적용되지 않는다. 표의 라이선스는 지정한 저장소의 기본적인 코드 조건이며, 개별 파일과 버전은 직접 확인해야 한다. 두 번째 표는 플랫폼·모델·제품·표준, 제한적 공개 코드, 또는 라이선스가 불명확한 항목이다. NVIDIA 고유 모델도 소스가 공개되었다는 이유만으로 오픈소스로 분류하지 않았다.

> 상세 페이지에서 구조, 워크플로 예시와 이미지 출처를 확인할 수 있습니다. 데이터셋 이름은 공식 카드로 바로 연결됩니다.

**워크플로와 신규 목록 항목 확인일** · 2026-11-10. 두 가이드는 공식 자료 대조와 GPU 실행 검증을 구분합니다.

## 최근 업스트림 릴리스

2026년 11월 13일 공식 자료 확인. 정식판과 프리뷰는 공개 상태를 함께 표시합니다.

- **Isaac Sim** · 현재 정식판은 [6.2.0](https://github.com/isaac-sim/IsaacSim/releases/tag/v6.2.0)입니다. [7.0 Alpha 1](https://github.com/isaac-sim/IsaacSim/releases/tag/v7.0.0a1)은 Kit 없이 물리 계산과 로봇 제어를 수행하는 모듈형 라이브러리의 미리보기입니다. [가이드](docs/ko/isaac-sim.md)
- **Isaac Lab** · [3.0 정식판](https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0)은 같은 작업 API에서 물리 엔진과 렌더러를 선택할 수 있게 합니다. Kit 기반 워크플로의 기준 버전은 Isaac Sim 6.2입니다. [가이드](docs/ko/isaac-lab.md)
- **Newton / Warp** · [Newton 1.8.0](https://github.com/newton-physics/newton/releases/tag/v1.8.0)은 실험 기능인 SolverSteel을, [Warp 1.19.0](https://github.com/NVIDIA/warp/releases/tag/v1.19.0)은 재사용 가능한 희소 행렬 조립과 Surface Nets를 추가했습니다. 함께 설치할 때는 Isaac Lab이 지정한 버전을 확인하세요.
- **Alpamayo 2** · [Super](https://huggingface.co/nvidia/Alpamayo2-Super)는 34B 주행 VLA입니다. 차량 탑재 환경을 위한 [Edge](https://huggingface.co/nvidia/Alpamayo2-Edge)는 11월 10일 가중치를 공개했습니다. 두 모델 카드 모두 OpenMDW-1.1을 명시합니다. [가이드](docs/ko/alpamayo.md)
- **Cosmos 3** · NVIDIA가 영상 및 주행 센서 관측을 생성하는 [대화형 시뮬레이션 체크포인트](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation)를 공개했습니다. [가이드](docs/ko/cosmos.md)
- **Isaac Lab-Arena** · NVIDIA가 CoRL에서 [0.4 개발자 프리뷰](https://blogs.nvidia.com/blog/robotics-simulation-advancements-corl/)를 발표했습니다. Arena로 반복 가능한 로봇 정책 평가를 구성할 수 있습니다. [가이드](docs/ko/isaac-lab-arena.md)

## 1. 오픈소스 코드가 확인된 프로젝트

최근 커밋은 연결된 저장소의 기본 브랜치를 기준으로 UTC 날짜를 표시하며, 매주 갱신합니다. 라이선스 링크는 2026년 11월 13일에 확인한 원문을 가리킵니다. OvPhysX의 날짜는 상위 PhysX 저장소를 기준으로 합니다.

### 물리, 3D 및 시뮬레이션

![두 시뮬레이션 경로. OpenUSD 장면은 Isaac Sim과 PhysX에서 실행할 수 있고, Warp 기반 Newton은 Isaac Lab 학습 환경을 독립 실행할 수 있습니다.](assets/section-diagrams/physics-simulation.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 최근 커밋 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|---|
| **Newton** | Warp 기반 GPU 물리 엔진과 로봇 시뮬레이션 솔버 | [Apache-2.0](https://github.com/newton-physics/newton/blob/c552d3653352a472dcc1f7e74e004aacac202f74/LICENSE.md) | [2026-11-12](https://github.com/newton-physics/newton/commit/c552d3653352a472dcc1f7e74e004aacac202f74) | [저장소](https://github.com/newton-physics/newton) | [상세 보기](docs/ko/newton.md) |
| **NVIDIA Warp** | GPU 가속 물리·기하 계산용 Python 프레임워크 | [Apache-2.0](https://github.com/NVIDIA/warp/blob/82dab030eeb6088e180922bc60aa167a2038e457/LICENSE.md) | [2026-11-13](https://github.com/NVIDIA/warp/commit/82dab030eeb6088e180922bc60aa167a2038e457) | [저장소](https://github.com/NVIDIA/warp) | [상세 보기](docs/ko/nvidia-warp.md) |
| **NVIDIA PhysX** | 강체·충돌 등 물리 시뮬레이션 엔진 | [BSD-3-Clause](https://github.com/NVIDIA-Omniverse/PhysX/blob/b97365c6ddb32fda8469bc788ec18024862b0368/LICENSE.md); 일부 추가 구성 요소는 별도 조건 확인 | [2026-10-15](https://github.com/NVIDIA-Omniverse/PhysX/commit/b97365c6ddb32fda8469bc788ec18024862b0368) | [저장소](https://github.com/NVIDIA-Omniverse/PhysX) | [상세 보기](docs/ko/nvidia-physx.md) |
| **MuJoCo Warp (MJWarp)** | MuJoCo 물리 계산의 Warp 기반 가속 구현 | [Apache-2.0](https://github.com/google-deepmind/mujoco_warp/blob/5242c6b660de08b4585628d18d803594be71f300/LICENSE); Google DeepMind 프로젝트 | [2026-11-12](https://github.com/google-deepmind/mujoco_warp/commit/5242c6b660de08b4585628d18d803594be71f300) | [저장소](https://github.com/google-deepmind/mujoco_warp) | [상세 보기](docs/ko/mujoco-warp.md) |
| **OpenUSD** | 3D 장면과 자산 교환·구성을 위한 프레임워크 | [TOST 1.0](https://github.com/PixarAnimationStudios/OpenUSD/blob/39c5ce8fa2255956c18c6ea34c33733980708acd/LICENSE.txt) (Apache-2.0 기반, 상표 조항 수정). 에셋과 명세에는 별도 조건 적용 | [2026-11-10](https://github.com/PixarAnimationStudios/OpenUSD/commit/39c5ce8fa2255956c18c6ea34c33733980708acd) | [저장소](https://github.com/PixarAnimationStudios/OpenUSD) | [상세 보기](docs/ko/openusd.md) |
| **Isaac Sim** | 로봇·센서·환경 시뮬레이션 참조 애플리케이션 | 저장소 코드 [Apache-2.0](https://github.com/isaac-sim/IsaacSim/blob/09f95b4752a5bc04508acfd6e6b5e5d588a57bf1/LICENSE); 전체 배포물·의존성은 별도 NVIDIA 약관이 적용될 수 있음 | [2026-11-05](https://github.com/isaac-sim/IsaacSim/commit/09f95b4752a5bc04508acfd6e6b5e5d588a57bf1) | [저장소](https://github.com/isaac-sim/IsaacSim) | [상세 보기](docs/ko/isaac-sim.md) |
| **PhysicsNeMo** | 물리 기반 AI 및 대리 모델 학습 프레임워크 | [Apache-2.0](https://github.com/NVIDIA/physicsnemo/blob/d919d80359192ebdd6958882c28d0b6aeb578acd/LICENSE.txt) | [2026-11-13](https://github.com/NVIDIA/physicsnemo/commit/d919d80359192ebdd6958882c28d0b6aeb578acd) | [저장소](https://github.com/NVIDIA/physicsnemo) | [상세 보기](docs/ko/physicsnemo.md) |
| **OpenUSD Exchange SDK** | OpenUSD 장면 작성과 교환을 돕는 SDK | [Apache-2.0](https://github.com/NVIDIA-Omniverse/usd-exchange/blob/3faf293720c8aa6854b92a16f492f4f8159cf494/LICENSE.md) | [2026-10-07](https://github.com/NVIDIA-Omniverse/usd-exchange/commit/3faf293720c8aa6854b92a16f492f4f8159cf494) | [저장소](https://github.com/NVIDIA-Omniverse/usd-exchange) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **AIF Pipeline Samples** | CAD 변환·USD 검증·최적화·메타데이터 설정 예제 | 샘플 코드 [MIT](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/LICENSE). Kit와 변환기는 별도 조건 | [2026-03-13](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/commit/41038967ef0a2459b128a225161f8d59beb3b424) | [저장소](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **SimFoundry** | 작업대 영상에서 객체와 물리 속성이 있는 편집 가능한 시뮬레이션 장면 생성 | 코드 [Apache-2.0](https://github.com/NVlabs/SimFoundry/blob/9e34ebefcd020583fbb755a8b57268dce78eca26/LICENSE). 외부 모델과 자산은 별도 조건 | [2026-08-27](https://github.com/NVlabs/SimFoundry/commit/9e34ebefcd020583fbb755a8b57268dce78eca26) | [저장소](https://github.com/NVlabs/SimFoundry) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **fVDB Core** | GPU 가속 희소 볼륨 자료구조와 3D 연산 | [Apache-2.0](https://github.com/openvdb/fvdb-core/blob/57887afd59171716164c9ba00f7079660fecea34/LICENSE) | [2026-11-13](https://github.com/openvdb/fvdb-core/commit/a9a64216bfa3cb12fcd748e4827d9fb866e44e34) | [저장소](https://github.com/openvdb/fvdb-core) | — |
| **fVDB Reality Capture** | fVDB 기반 3D Gaussian Splatting 복원·처리 도구 | 코드 [Apache-2.0](https://github.com/openvdb/fvdb-reality-capture/blob/461117232d68fc4e4a0538abf3a6d781bbbf9da2/LICENSE). 샘플과 의존성은 별도 확인 | [2026-11-13](https://github.com/openvdb/fvdb-reality-capture/commit/9d4ce6b90d28640414466fa9e947445510d93704) | [저장소](https://github.com/openvdb/fvdb-reality-capture) | — |
| **gsplat** | NuRec이 사용하는 CUDA 가속 Gaussian Splatting 라이브러리 | 코드 [Apache-2.0](https://github.com/nerfstudio-project/gsplat/blob/512d366b67073d77ca099ede742683c165dfc23b/LICENSE). NVIDIA가 기여하는 Nerfstudio 독립 프로젝트 | [2026-09-19](https://github.com/nerfstudio-project/gsplat/commit/512d366b67073d77ca099ede742683c165dfc23b) | [저장소](https://github.com/nerfstudio-project/gsplat) | — |
| **3DGRUT** | Gaussian 레이 트레이싱과 하이브리드 래스터화 연구 코드 | 코드 [Apache-2.0](https://github.com/nv-tlabs/3dgrut/blob/dfd3d54c8c612003fb7948443edf7778f2bcd5ec/LICENSE). 의존성 조건은 별도 확인 | [2026-11-06](https://github.com/nv-tlabs/3dgrut/commit/dfd3d54c8c612003fb7948443edf7778f2bcd5ec) | [저장소](https://github.com/nv-tlabs/3dgrut) | — |
| **OvPhysX** | Kit 설치 없이 PhysX SDK로 USD 장면의 물리 계산 | 소스 [Apache-2.0](https://github.com/NVIDIA-Omniverse/PhysX/blob/b97365c6ddb32fda8469bc788ec18024862b0368/ovphysx/LICENSE.txt). 배포 wheel과 SDK는 NVIDIA Omniverse License | [2026-10-15](https://github.com/NVIDIA-Omniverse/PhysX/commit/b97365c6ddb32fda8469bc788ec18024862b0368) | [소스·라이선스](https://github.com/NVIDIA-Omniverse/PhysX/blob/main/ovphysx/README.md#5-licensing) | [관련 가이드](docs/ko/nvidia-physx.md) |

### 로봇 학습, 수집 및 제어

![Isaac Capture나 V2D로 시연을 확보하고, 데이터를 준비해 정책을 학습한 뒤 Lab-Arena에서 평가합니다. LEAPP나 Isaac ROS로 배포하고 운영 결과를 다음 수집에 반영합니다.](assets/section-diagrams/robot-learning.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 최근 커밋 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|---|
| **Isaac Lab** | 강화·모방학습 및 로봇 학습 환경 | [BSD-3-Clause](https://github.com/isaac-sim/IsaacLab/blob/7bca8097a5ed27c26744686c84355d1786769e81/LICENSE); 선택한 백엔드와 의존성은 별도 조건 | [2026-11-12](https://github.com/isaac-sim/IsaacLab/commit/7bca8097a5ed27c26744686c84355d1786769e81) | [저장소](https://github.com/isaac-sim/IsaacLab) | [상세 보기](docs/ko/isaac-lab.md) |
| **Isaac Lab-Arena** | 조합 가능한 로봇 작업 환경과 정책 평가 | [Apache-2.0](https://github.com/isaac-sim/IsaacLab-Arena/blob/b724395e2a0c5963757021003aeb664c84a10e90/LICENSE.md); Isaac Sim 등 의존성 별도 | [2026-11-13](https://github.com/isaac-sim/IsaacLab-Arena/commit/fc9354a419ca69ec98c510ca88f5391b1f6ad7be) | [저장소](https://github.com/isaac-sim/IsaacLab-Arena) | [상세 보기](docs/ko/isaac-lab-arena.md) |
| **RoboLab** | Isaac Lab 기반 로봇팔 조작 정책 평가 벤치마크 | 코드 [Apache-2.0](https://github.com/NVlabs/RoboLab/blob/9cce00cadd5dc575fd2b8ea3836f5bdcde574229/LICENSE). 작업 자산과 정책 이용 조건은 별도 확인 | [2026-10-27](https://github.com/NVlabs/RoboLab/commit/9cce00cadd5dc575fd2b8ea3836f5bdcde574229) | [저장소](https://github.com/NVlabs/RoboLab) | [관련 가이드](docs/ko/isaac-lab.md) |
| **Microduck 로봇 소프트웨어** | ONNX 정책 실행, 서보 제어, 장치 서비스를 담당하는 온보드 Rust 런타임 | 코드 [Apache-2.0](https://github.com/pollen-robotics/microduck/blob/86b222a598efeeb258fdd94473bad924fd872785/LICENSE) | [2026-11-13](https://github.com/pollen-robotics/microduck/commit/86b222a598efeeb258fdd94473bad924fd872785) | [저장소](https://github.com/pollen-robotics/microduck) | [상세 보기](docs/ko/microduck.md) |
| **Microduck RL** | Pollen Robotics의 mjlab·PPO 기반 Microduck 학습 환경 | 코드 [Apache-2.0](https://github.com/pollen-robotics/microduck_rl/blob/0daab160d3fb1c2cbaba16a4a19052f36709dd9e/LICENSE), 지정된 STL 메시는 [CC BY-NC-SA 4.0](https://github.com/pollen-robotics/microduck_rl/blob/0daab160d3fb1c2cbaba16a4a19052f36709dd9e/LICENSE-MODELS.md) | [2026-11-10](https://github.com/pollen-robotics/microduck_rl/commit/0daab160d3fb1c2cbaba16a4a19052f36709dd9e) | [저장소](https://github.com/pollen-robotics/microduck_rl) | [상세 보기](docs/ko/microduck.md) |
| **Isaac Capture (이전 Isaac Teleop 포함)** | 원격 조작 및 1인칭 데이터 수집·기록·리타기팅 | 기본 [Apache-2.0](https://github.com/NVIDIA/IsaacCapture/blob/c0b62921e2512aa5b5a643f2f33184d0b8cfe156/LICENSE.md); EgoPost는 OpenMDW-1.1, CloudXR과 일부 선택 패키지는 별도 독점 조건 | [2026-11-12](https://github.com/NVIDIA/IsaacCapture/commit/c0b62921e2512aa5b5a643f2f33184d0b8cfe156) | [저장소](https://github.com/NVIDIA/IsaacCapture) | [상세 보기](docs/ko/isaac-capture.md) |
| **AutoData** | 소수의 시연을 다양한 작업 조건의 궤적으로 확장 | [Apache-2.0](https://github.com/isaac-sim/AutoData/blob/073c393e90d4188937d916096356fba992a3906c/LICENSE.md); Isaac Sim 및 특정 cuRobo 구성 요소 별도 조건 | [2026-11-06](https://github.com/isaac-sim/AutoData/commit/073c393e90d4188937d916096356fba992a3906c) | [저장소](https://github.com/isaac-sim/AutoData) | [상세 보기](docs/ko/autodata.md) |
| **Video-to-Data (V2D)** | 영상의 장면·동작을 복원하고 로봇 학습에 연결하는 파이프라인 | 소스 [Apache-2.0](https://github.com/nvidia-isaac/video_to_data/blob/1e862a8984bf28474c324c1b49db99b2da7ece80/LICENSE), 문서·스킬 [CC-BY-4.0](https://github.com/nvidia-isaac/video_to_data/blob/1e862a8984bf28474c324c1b49db99b2da7ece80/LICENSE); 의존 모델 별도 | [2026-11-12](https://github.com/nvidia-isaac/video_to_data/commit/1e862a8984bf28474c324c1b49db99b2da7ece80) | [저장소](https://github.com/nvidia-isaac/video_to_data) | [상세 보기](docs/ko/video-to-data.md) |
| **Isaac GR00T 코드** | GR00T 로봇 정책의 학습·추론·배포 코드 | 코드 [Apache-2.0](https://github.com/NVIDIA/Isaac-GR00T/blob/3b49067943eb1ab2eb2203b93d461c4390c78da3/LICENSE); 모델과 가중치는 별도 조건 | [2026-11-10](https://github.com/NVIDIA/Isaac-GR00T/commit/3b49067943eb1ab2eb2203b93d461c4390c78da3) | [저장소](https://github.com/NVIDIA/Isaac-GR00T) | [상세 보기](docs/ko/isaac-gr00t.md) |
| **cuRobo** | GPU 기반 로봇 역기구학·동작계획 | 저장소 [Apache-2.0](https://github.com/NVlabs/curobo/blob/8991ec140f1f03cca2725118575c857aa3aef70e/LICENSE); AutoData 배포의 특정 구성 요소는 별도 약관 확인 | [2026-11-11](https://github.com/NVlabs/curobo/commit/8991ec140f1f03cca2725118575c857aa3aef70e) | [저장소](https://github.com/NVlabs/curobo) | [상세 보기](docs/ko/curobo.md) |
| **LeRobot** | 로봇 데이터셋과 모델 학습 도구; Capture와 연동 가능 | [Apache-2.0](https://github.com/huggingface/lerobot/blob/e6ffde60312365c5452c46189a26872483943154/LICENSE); Hugging Face 프로젝트 | [2026-11-12](https://github.com/huggingface/lerobot/commit/e6ffde60312365c5452c46189a26872483943154) | [저장소](https://github.com/huggingface/lerobot) | [상세 보기](docs/ko/lerobot.md) |
| **Isaac ROS Visual SLAM** | ROS 2 기반 시각 주행거리 추정·SLAM 연동 | [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam/blob/9058506efd0b967ac894a717bdbe98df017637e5/LICENSE); cuVSLAM은 별도 약관 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam/commit/9058506efd0b967ac894a717bdbe98df017637e5) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam) | [상세 보기](docs/ko/isaac-ros-visual-slam.md) |
| **Isaac ROS Nvblox** | ROS 2 3D 지도 및 Nav2 장애물 비용 지도 | [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox/blob/79654d29c9f862db6b24c1116ab23a360f3294d5/LICENSE); 의존성 별도 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox/commit/79654d29c9f862db6b24c1116ab23a360f3294d5) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox) | [상세 보기](docs/ko/isaac-ros-nvblox.md) |
| **Isaac ROS Pose Estimation** | GPU 가속 물체 자세 추정 패키지 | 코드 [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation/blob/7772773263d9e401bfbb0ca37cf00133ac1efeeb/LICENSE); 모델 별도 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation/commit/7772773263d9e401bfbb0ca37cf00133ac1efeeb) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation) | [상세 보기](docs/ko/isaac-ros-pose-estimation.md) |
| **Isaac ROS Manipulation** | ROS 2 기반 로봇팔 조작 워크플로 | 코드 [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_manipulation/blob/94cdd950873ee90dab5fab2c5a3bc0ab84c6a9d5/LICENSE); 모델·의존성 별도 | [2026-10-31](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_manipulation/commit/94cdd950873ee90dab5fab2c5a3bc0ab84c6a9d5) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_manipulation) | [상세 보기](docs/ko/isaac-ros-manipulation.md) |
| **Isaac ROS DNN Stereo Depth** | ROS 2 신경망 스테레오 깊이 추정 | 코드 [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth/blob/9bbb1feb55162e42543519a691f03f5715f496e9/LICENSE); 모델 별도 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth/commit/9bbb1feb55162e42543519a691f03f5715f496e9) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth) | [상세 보기](docs/ko/isaac-ros-dnn-stereo-depth.md) |
| **Isaac ROS DNN Inference** | ROS 2용 TensorRT·Triton 추론 연동 | 코드 [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference/blob/af98dec2e81e4b5f51273fc66872cc2059bdae31/LICENSE); 런타임·모델 별도 | [2026-09-24](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference/commit/af98dec2e81e4b5f51273fc66872cc2059bdae31) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference) | [상세 보기](docs/ko/isaac-ros-dnn-inference.md) |
| **LEAPP** | 로봇 정책의 전체 추론 파이프라인 내보내기·배포 | [Apache-2.0](https://github.com/nvidia-isaac/leapp/blob/a565ce7ec8f2d2aab6733c3031aaf117a25dc42f/LICENSE); 모델·런타임 의존성 별도 | [2026-11-12](https://github.com/nvidia-isaac/leapp/commit/a565ce7ec8f2d2aab6733c3031aaf117a25dc42f) | [저장소](https://github.com/nvidia-isaac/leapp) | [상세 보기](docs/ko/leapp.md) |
| **WBC-AGILE** | Isaac Lab 기반 휴머노이드 전신 이동·조작 학습 | 대부분 [Apache-2.0](https://github.com/nvidia-isaac/WBC-AGILE/blob/f5c388ebc7c1b056de891e3edb8f47693a50d5d3/LICENCE), RSL-RL 패치는 [BSD-3-Clause](https://github.com/nvidia-isaac/WBC-AGILE/blob/f5c388ebc7c1b056de891e3edb8f47693a50d5d3/LICENCE) | [2026-10-23](https://github.com/nvidia-isaac/WBC-AGILE/commit/f5c388ebc7c1b056de891e3edb8f47693a50d5d3) | [저장소](https://github.com/nvidia-isaac/WBC-AGILE) | [상세 보기](docs/ko/wbc-agile.md) |
| **FoundationPose Inference Library** | 배포용 물체 자세 추정 라이브러리 | 코드 [Apache-2.0](https://github.com/nvidia-isaac/foundation-pose-inference-library/blob/89dd4cfec75f944b9fca52d9cb282725f1666c12/LICENSE); 모델 가중치 별도 | [2026-09-16](https://github.com/nvidia-isaac/foundation-pose-inference-library/commit/89dd4cfec75f944b9fca52d9cb282725f1666c12) | [저장소](https://github.com/nvidia-isaac/foundation-pose-inference-library) | [상세 보기](docs/ko/foundationpose-inference-library.md) |
| **Isaac Automator** | Isaac 시뮬레이션 워크플로 설치·배포 자동화 | [Apache-2.0](https://github.com/isaac-sim/IsaacAutomator/blob/eb90c0e2eaf244f4541738cb27afc50c9c73b9cd/LICENSE); 설치되는 구성 요소는 별도 약관 | [2026-10-27](https://github.com/isaac-sim/IsaacAutomator/commit/eb90c0e2eaf244f4541738cb27afc50c9c73b9cd) | [저장소](https://github.com/isaac-sim/IsaacAutomator) | [상세 보기](docs/ko/isaac-automator.md) |
| **Isaac ROS Object Detection** | ROS 2 물체 탐지 패키지 | [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection/blob/5a2a25e9581eefef1500d0ed00dca97588bb0244/LICENSE); 모델 별도 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection/commit/5a2a25e9581eefef1500d0ed00dca97588bb0244) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection) | [상세 보기](docs/ko/isaac-ros-object-detection.md) |
| **Isaac ROS Image Segmentation** | ROS 2 이미지 의미 분할 | [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation/blob/c81a19d1f293d70db3c49c81b42f0de23c78bc36/LICENSE); 모델 별도 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation/commit/c81a19d1f293d70db3c49c81b42f0de23c78bc36) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation) | [상세 보기](docs/ko/isaac-ros-image-segmentation.md) |
| **Isaac ROS Deploy** | 학습된 로봇 정책을 시뮬레이션 및 실제 하드웨어에 배포 | [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_deploy/blob/f3aa6b89b89fb009c9d3a338feb8c549eb00a1b3/LICENSE); 런타임·모델 별도 | [2026-09-24](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_deploy/commit/f3aa6b89b89fb009c9d3a338feb8c549eb00a1b3) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_deploy) | [상세 보기](docs/ko/isaac-ros-deploy.md) |
| **Isaac ROS Teleop** | ROS 2 기반 XR 로봇 원격 조작 | [Apache-2.0](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_teleop/blob/e80602863a0c4c94360a22b02248164c2dad6fa4/LICENSE); 장치 소프트웨어 별도 | [2026-09-22](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_teleop/commit/e80602863a0c4c94360a22b02248164c2dad6fa4) | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_teleop) | [상세 보기](docs/ko/isaac-ros-teleop.md) |
| **GR00T-VisualSim2Real** | 휴머노이드 시각 기반 이동·조작의 시뮬레이션-현실 전이 | [Apache-2.0](https://github.com/NVlabs/GR00T-VisualSim2Real/blob/92bf0863d4a9b6ee29849736152b7769bd45c49c/LICENSE); 모델·로봇 자산 별도 | [2026-04-20](https://github.com/NVlabs/GR00T-VisualSim2Real/commit/92bf0863d4a9b6ee29849736152b7769bd45c49c) | [저장소](https://github.com/NVlabs/GR00T-VisualSim2Real) | [상세 보기](docs/ko/gr00t-visualsim2real.md) |
| **GR00T-H 코드** | 의료·수술 로봇 정책 학습 및 추론 코드 | 코드 [Apache-2.0](https://github.com/NVIDIA-Medtech/GR00T-H/blob/d8369db7c85ae0ae9f2cbd08b5ec2ca52d69af55/LICENSE); 의료 모델 가중치·데이터 별도 약관 | [2026-06-01](https://github.com/NVIDIA-Medtech/GR00T-H/commit/d8369db7c85ae0ae9f2cbd08b5ec2ca52d69af55) | [저장소](https://github.com/NVIDIA-Medtech/GR00T-H) | [상세 보기](docs/ko/gr00t-h.md) |
| **Cosmos Reason2 코드** | 월드 추론 모델의 추론·학습 코드 | 코드 [Apache-2.0](https://github.com/nvidia-cosmos/cosmos-reason2/blob/a3b4a1db4065fe13c4b1f4d2fb8605bad647f4b9/LICENSE); 모델 가중치 별도 약관 | [2026-06-07](https://github.com/nvidia-cosmos/cosmos-reason2/commit/a3b4a1db4065fe13c4b1f4d2fb8605bad647f4b9) | [저장소](https://github.com/nvidia-cosmos/cosmos-reason2) | [상세 보기](docs/ko/cosmos-reason2.md) |
| **Cosmos Predict2 코드** | 월드·영상 생성 모델 코드 | 코드 [Apache-2.0](https://github.com/nvidia-cosmos/cosmos-predict2/blob/661da4774b0ca41d082a0ecbeb47550bcf07e03f/LICENSE); 모델 가중치 별도 약관 | [2025-10-07](https://github.com/nvidia-cosmos/cosmos-predict2/commit/661da4774b0ca41d082a0ecbeb47550bcf07e03f) · 보관됨 | [저장소](https://github.com/nvidia-cosmos/cosmos-predict2) | [상세 보기](docs/ko/cosmos-predict2.md) |
| **openpi** | Physical Intelligence π 정책의 학습·추론·파인튜닝 코드 | [Apache-2.0](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/LICENSE). 체크포인트와 백본 조건은 별도 | [2026-08-24](https://github.com/Physical-Intelligence/openpi/commit/215abfb217dbac7d5f1273282331b9b1866c0479) | [저장소](https://github.com/Physical-Intelligence/openpi) | [가이드](docs/ko/physical-intelligence-pi.md) |
| **Cosmos Policy code** | Predict2 기반 로봇 조작 정책의 후학습·추론 | [Apache-2.0](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LICENSE). 공개 체크포인트는 별도 조건 | [2026-01-23](https://github.com/NVlabs/cosmos-policy/commit/18a2accadf4e7a3531e56754102af5a24d2316da) | [저장소](https://github.com/NVlabs/cosmos-policy) | [가이드](docs/ko/robot-foundation-models.md#cosmos-policy) |
| **OpenVLA code** | 7B 로봇 조작 VLA 추론·파인튜닝 코드 | [MIT](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/LICENSE). 가중치에 Llama 2 조건도 적용 | [2025-03-23](https://github.com/openvla/openvla/commit/c8f03f48af692657d3060c19588038c7220e9af9) | [저장소](https://github.com/openvla/openvla) | [가이드](docs/ko/robot-foundation-models.md#다른-vla) |
| **MolmoAct 2 code** | 깊이 정보를 활용하는 조작 모델의 추론·파인튜닝 | [Apache-2.0](https://github.com/allenai/molmoact2/blob/6070080a20321b4f498ab30f28e1d09ac465edb7/LICENSE) | [2026-10-02](https://github.com/allenai/molmoact2/commit/6070080a20321b4f498ab30f28e1d09ac465edb7) | [저장소](https://github.com/allenai/molmoact2) | [가이드](docs/ko/robot-foundation-models.md#다른-vla) |
| **X-VLA code** | 로봇 형태별 소프트 프롬프트를 사용하는 로봇 정책 | [Apache-2.0](https://github.com/2toinf/X-VLA/blob/6c4ecfb8be458ae7c0c96094e4b0add4174f4fe2/LICENSE) | [2026-10-20](https://github.com/2toinf/X-VLA/commit/6c4ecfb8be458ae7c0c96094e4b0add4174f4fe2) | [저장소](https://github.com/2toinf/X-VLA) | [가이드](docs/ko/robot-foundation-models.md#다른-vla) |
| **Praxis-1 code** | 미래 영상·행동 공동 예측과 추론·파인튜닝 코드 | [Apache-2.0](https://github.com/runwayml/praxis-1-oss/blob/afef2e18a0af22b2e9926e9f743dc4694ab8b6b5/LICENSE). 가중치는 Hugging Face 접근 절차 필요 | [2026-11-12](https://github.com/runwayml/praxis-1-oss/commit/afef2e18a0af22b2e9926e9f743dc4694ab8b6b5) | [저장소](https://github.com/runwayml/praxis-1-oss) | [가이드](docs/ko/robot-foundation-models.md#월드-액션-모델) |
| **FLUX 3 Action code** | 영상·행동을 함께 예측하는 모델의 추론·파인튜닝 | [Apache-2.0](https://github.com/black-forest-labs/flux-action/blob/aea7863fbbbda1e282fa7bde2054e290bf09b3f8/LICENSE). 가중치는 별도 이용 조건 | [2026-11-10](https://github.com/black-forest-labs/flux-action/commit/aea7863fbbbda1e282fa7bde2054e290bf09b3f8) | [저장소](https://github.com/black-forest-labs/flux-action) | [가이드](docs/ko/robot-foundation-models.md#월드-액션-모델) |

### 데이터 생성·처리 및 실행

![Cosmos Data Factory의 예시 흐름. 시뮬레이션 장면이나 기존 영상을 정제·증강하고 라벨과 품질을 확인해 데이터셋으로 내보냅니다.](assets/section-diagrams/data-generation.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 최근 커밋 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|---|
| **Cosmos Data Factory (CDF; 이전 Physical AI Data Factory)** | 영상·이미지 생성 및 처리 워크플로와 스킬 모음 | 코드 [Apache-2.0](https://github.com/NVIDIA/cosmos-data-factory/blob/6a22fd17c563d16f50cd389c17321d15420b6fd0/LICENSE), 문서·스킬 [CC-BY-4.0](https://github.com/NVIDIA/cosmos-data-factory/blob/6a22fd17c563d16f50cd389c17321d15420b6fd0/LICENSE); 사용 모델·서비스 별도 | [2026-10-30](https://github.com/NVIDIA/cosmos-data-factory/commit/6a22fd17c563d16f50cd389c17321d15420b6fd0) | [저장소](https://github.com/NVIDIA/cosmos-data-factory) | [상세 보기](docs/ko/cosmos-data-factory.md) |
| **CDF Auto Labeling (이전 paidf-auto-labeling)** | 영상·이미지 자동 주석 워크플로 | [Apache-2.0](https://github.com/NVIDIA/cdf-auto-labeling/blob/6c75c76c52a6c76c3866a38d30885e11123b0981/LICENSE); 모델·서비스 별도 | [2026-10-20](https://github.com/NVIDIA/cdf-auto-labeling/commit/6c75c76c52a6c76c3866a38d30885e11123b0981) | [저장소](https://github.com/NVIDIA/cdf-auto-labeling) | [상세 보기](docs/ko/cdf-auto-labeling.md) |
| **CDF Augmentation (이전 paidf-augmentation)** | 영상·이미지·텍스트 증강 워크플로 | [Apache-2.0](https://github.com/NVIDIA/cdf-augmentation/blob/73c861c43a4952b6060c87265bf39f4abc48199a/LICENSE) 기반(상표 조항 수정). 모델과 서비스에는 별도 조건 적용 | [2026-10-20](https://github.com/NVIDIA/cdf-augmentation/commit/73c861c43a4952b6060c87265bf39f4abc48199a) | [저장소](https://github.com/NVIDIA/cdf-augmentation) | [상세 보기](docs/ko/cdf-augmentation.md) |
| **CDF Simulation (이전 paidf-simulation)** | Isaac Sim·Replicator 기반 합성 데이터 생성 | [Apache-2.0](https://github.com/NVIDIA/cdf-simulation/blob/fe4405836d4bb3cf52ce7d1cd24762e46c2fd590/LICENSE); 시뮬레이터 및 자산 별도 | [2026-10-27](https://github.com/NVIDIA/cdf-simulation/commit/fe4405836d4bb3cf52ce7d1cd24762e46c2fd590) | [저장소](https://github.com/NVIDIA/cdf-simulation) | [상세 보기](docs/ko/cdf-simulation.md) |
| **Cosmos Curator** | 영상·이미지 분할, 필터링, 주석, 중복 제거 | [Apache-2.0](https://github.com/NVIDIA/cosmos-curator/blob/95675431e309fd86c1c559a39fcb694ddedaa2a9/LICENSE); 모델은 별도 | [2026-11-10](https://github.com/NVIDIA/cosmos-curator/commit/95675431e309fd86c1c559a39fcb694ddedaa2a9) | [저장소](https://github.com/NVIDIA/cosmos-curator) | [상세 보기](docs/ko/cosmos-curator.md) |
| **Cosmos Evaluator** | 생성 영상의 객체 일관성·물리적 개연성 등 평가 | [Apache-2.0](https://github.com/NVIDIA/cosmos-evaluator/blob/a4915ca4faa1f15d3e6fb1825c37f18b1e187a73/LICENSE); 체커별 모델 조건 별도 | [2026-11-03](https://github.com/NVIDIA/cosmos-evaluator/commit/a4915ca4faa1f15d3e6fb1825c37f18b1e187a73) | [저장소](https://github.com/NVIDIA/cosmos-evaluator) | [상세 보기](docs/ko/cosmos-evaluator.md) |
| **CDF Orchestration** | 데이터 팩토리 작업 실행·관리 구성 요소 | 코드 [Apache-2.0](https://github.com/NVIDIA/cdf-orchestration/blob/5edf7474107eb38643a18d7345b94f6cfa8b3e1f/LICENSE); 실행 서비스와 의존성은 별도 조건 | [2026-10-29](https://github.com/NVIDIA/cdf-orchestration/commit/5edf7474107eb38643a18d7345b94f6cfa8b3e1f) | [저장소](https://github.com/NVIDIA/cdf-orchestration) | [상세 보기](docs/ko/cdf-orchestration.md) |
| **OSMO** | GPU 자원을 사용하는 시뮬레이션·학습 워크플로 실행 관리 | [Apache-2.0](https://github.com/NVIDIA/OSMO/blob/c86131031a53cdd725dd2241354ced94d997a214/LICENSE) | [2026-11-10](https://github.com/NVIDIA/OSMO/commit/c86131031a53cdd725dd2241354ced94d997a214) | [저장소](https://github.com/NVIDIA/OSMO) | [상세 보기](docs/ko/osmo.md) |
| **TensorRT 공개 코드** | 추론 최적화 관련 샘플·플러그인·도구 | 저장소 [Apache-2.0](https://github.com/NVIDIA/TensorRT/blob/72fc1a3d23a163216893b363fb562b9464865afb/LICENSE); TensorRT 바이너리 SDK 전체가 같은 라이선스라는 뜻은 아님 | [2026-11-05](https://github.com/NVIDIA/TensorRT/commit/72fc1a3d23a163216893b363fb562b9464865afb) | [저장소](https://github.com/NVIDIA/TensorRT) | [상세 보기](docs/ko/tensorrt.md) |
| **Holoscan SDK** | 저지연 스트리밍·센서 AI 파이프라인 | [Apache-2.0](https://github.com/nvidia-holoscan/holoscan-sdk/blob/358c772f2d2e88d117651a961d6f6bf9b650cf8d/LICENSE.txt); 외부 구성 요소 별도 | [2026-10-20](https://github.com/nvidia-holoscan/holoscan-sdk/commit/358c772f2d2e88d117651a961d6f6bf9b650cf8d) | [저장소](https://github.com/nvidia-holoscan/holoscan-sdk) | [상세 보기](docs/ko/holoscan-sdk.md) |

### NeMo와 물리 AI 도구

![NeMo의 데이터셋 준비·학습·평가 경로와, 앱에서 Switchyard를 거쳐 모델 엔드포인트로 보내는 선택적 요청 경로.](assets/section-diagrams/nemo-tooling.ko.svg)

NeMo 도구는 데이터 준비, 모델 후학습과 에이전트 운영에 쓰입니다. AlpaGym과 Curator에 연결되는 Cosmos RL과 Xenna도 이 표에서 함께 볼 수 있습니다. 상세 문서에서는 공식 연동 사례와 설명용 워크플로를 구분합니다.

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 최근 커밋 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|---|
| **NeMo Switchyard** | LLM 에이전트와 애플리케이션의 모델 요청 라우팅 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Switchyard/blob/237b918f91a5c594f9b1d1ddd8f336ee3c739b56/LICENSE) | [2026-11-13](https://github.com/NVIDIA-NeMo/Switchyard/commit/237b918f91a5c594f9b1d1ddd8f336ee3c739b56) | [저장소](https://github.com/NVIDIA-NeMo/Switchyard) | [상세 보기](docs/ko/nemo-switchyard.md) |
| **NeMo Curator** | 텍스트·이미지·영상·오디오 데이터셋 분산 정제 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Curator/blob/a3e864f2e245d45f8de321dad9d104b9eb559d7c/LICENSE) | [2026-11-13](https://github.com/NVIDIA-NeMo/Curator/commit/a3e864f2e245d45f8de321dad9d104b9eb559d7c) | [저장소](https://github.com/NVIDIA-NeMo/Curator) | [상세 보기](docs/ko/nemo-curator.md) |
| **NeMo Data Designer** | 스키마와 시드 데이터를 이용한 합성 데이터 생성 | [Apache-2.0](https://github.com/NVIDIA-NeMo/DataDesigner/blob/2d5857e0deb19f58bbb1d334463e772100a34ead/LICENSE) | [2026-11-11](https://github.com/NVIDIA-NeMo/DataDesigner/commit/2d5857e0deb19f58bbb1d334463e772100a34ead) | [저장소](https://github.com/NVIDIA-NeMo/DataDesigner) | [상세 보기](docs/ko/nemo-data-designer.md) |
| **NeMo AutoModel** | 지원 언어·멀티모달 모델의 PyTorch 기반 분산 학습 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Automodel/blob/6f44dbf2390a4eb31bcdc67898bde98ce408f915/LICENSE) | [2026-11-12](https://github.com/NVIDIA-NeMo/Automodel/commit/6f44dbf2390a4eb31bcdc67898bde98ce408f915) | [저장소](https://github.com/NVIDIA-NeMo/Automodel) | [상세 보기](docs/ko/nemo-automodel.md) |
| **NeMo Megatron Bridge** | Megatron Core 학습 레시피와 Hugging Face 체크포인트 양방향 변환 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/f5c9841bb1ed12342ef69f58b278a0f0e4525a9a/LICENSE) | [2026-11-12](https://github.com/NVIDIA-NeMo/Megatron-Bridge/commit/f5c9841bb1ed12342ef69f58b278a0f0e4525a9a) | [저장소](https://github.com/NVIDIA-NeMo/Megatron-Bridge) | [상세 보기](docs/ko/nemo-megatron-bridge.md) |
| **NeMo RL** | 지원 LLM·VLM의 분산 지도 미세조정과 강화학습 | [Apache-2.0](https://github.com/NVIDIA-NeMo/RL/blob/c33a104f94c136aee8af9c079cb8fcf0f40fa81f/LICENSE) | [2026-11-13](https://github.com/NVIDIA-NeMo/RL/commit/c33a104f94c136aee8af9c079cb8fcf0f40fa81f) | [저장소](https://github.com/NVIDIA-NeMo/RL) | [상세 보기](docs/ko/nemo-rl.md) |
| **NeMo Gym** | 도구를 사용하는 에이전트의 롤아웃 환경과 검증기 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Gym/blob/1f88c43d55b61143378b0823ad9ce45d85cd4f16/LICENSE) | [2026-11-13](https://github.com/NVIDIA-NeMo/Gym/commit/1f88c43d55b61143378b0823ad9ce45d85cd4f16) | [저장소](https://github.com/NVIDIA-NeMo/Gym) | [상세 보기](docs/ko/nemo-gym.md) |
| **NeMo Evaluator** | 모델 엔드포인트를 대상으로 재현 가능한 모델·에이전트 평가 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Evaluator/blob/ea35ba36756abd59de201f60af8a2feba014744d/LICENSE) | [2026-10-19](https://github.com/NVIDIA-NeMo/Evaluator/commit/ea35ba36756abd59de201f60af8a2feba014744d) | [저장소](https://github.com/NVIDIA-NeMo/Evaluator) | [상세 보기](docs/ko/nemo-evaluator.md) |
| **NeMo Guardrails** | 모델 입력·검색 문맥·도구 실행·출력의 정책 검사 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Guardrails/blob/200cd26fa771b4205c2339a1a13a1d7e2623e756/LICENSE.md) | [2026-11-12](https://github.com/NVIDIA-NeMo/Guardrails/commit/200cd26fa771b4205c2339a1a13a1d7e2623e756) | [저장소](https://github.com/NVIDIA-NeMo/Guardrails) | [상세 보기](docs/ko/nemo-guardrails.md) |
| **NeMo Retriever Library** | 멀티모달 문서 추출·색인과 근거 검색 | [Apache-2.0](https://github.com/NVIDIA/NeMo-Retriever/blob/cc4da5fda4e21fb0a1c575f75ee85e1dbc63abd9/LICENSE) | [2026-11-13](https://github.com/NVIDIA/NeMo-Retriever/commit/cc4da5fda4e21fb0a1c575f75ee85e1dbc63abd9) | [저장소](https://github.com/NVIDIA/NeMo-Retriever) | [상세 보기](docs/ko/nemo-retriever.md) |
| **NeMo Agent Toolkit** | 에이전트 연결·프로파일링 도구와 공식 로봇 합성 데이터 사례 | [Apache-2.0](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/b95651f5a385b26ad1b976bf647efd3d56a8c644/LICENSE.md) (사용 중단 안내, 2026년 말 지원 종료 예정) | [2026-11-12](https://github.com/NVIDIA/NeMo-Agent-Toolkit/commit/b95651f5a385b26ad1b976bf647efd3d56a8c644) | [저장소](https://github.com/NVIDIA/NeMo-Agent-Toolkit) | [상세 보기](docs/ko/nemo-agent-toolkit.md) |
| **NeMo Relay** | 에이전트 모델·도구 호출 추적, 미들웨어와 정책 관리 | [Apache-2.0](https://github.com/NVIDIA/NeMo-Relay/blob/3c29c9d2e74a5aa2b3a02d853f400618c482e15c/LICENSE) | [2026-11-12](https://github.com/NVIDIA/NeMo-Relay/commit/3c29c9d2e74a5aa2b3a02d853f400618c482e15c) | [저장소](https://github.com/NVIDIA/NeMo-Relay) | [상세 보기](docs/ko/nemo-relay.md) |
| **NeMo Fabric** | 지원 에이전트 하네스의 어댑터 기반 실행 | [Apache-2.0](https://github.com/NVIDIA/NeMo-Fabric/blob/3bf6e1324acc4a08a2176ed203b78505109b4c3a/LICENSE) | [2026-11-12](https://github.com/NVIDIA/NeMo-Fabric/commit/3bf6e1324acc4a08a2176ed203b78505109b4c3a) | [저장소](https://github.com/NVIDIA/NeMo-Fabric) | [상세 보기](docs/ko/nemo-fabric.md) |
| **NeMo Helix** | 에이전트 평가·최적화·보안 테스트를 위한 제어 계층 | [Apache-2.0](https://github.com/NVIDIA-NeMo/nemo-helix/blob/86197e35f566fc88d9774dab78dd9710e90e743a/LICENSE) | [2026-11-13](https://github.com/NVIDIA-NeMo/nemo-helix/commit/86197e35f566fc88d9774dab78dd9710e90e743a) | [저장소](https://github.com/NVIDIA-NeMo/nemo-helix) | [상세 보기](docs/ko/nemo-helix.md) |
| **NemoClaw** | 지원 에이전트를 실행하는 OpenShell 기반 참조 스택 | [Apache-2.0](https://github.com/NVIDIA/NemoClaw/blob/4ecbcb3dc4bd7c3f0a32dc71b721ff4ec85b9851/LICENSE) | [2026-11-12](https://github.com/NVIDIA/NemoClaw/commit/4ecbcb3dc4bd7c3f0a32dc71b721ff4ec85b9851) | [저장소](https://github.com/NVIDIA/NemoClaw) | [상세 보기](docs/ko/nemoclaw.md) |
| **NeMo Speech** | 음성 인식·합성 등 음성 모델 학습과 추론 | [Apache-2.0](https://github.com/NVIDIA-NeMo/Speech/blob/079e48770098a4cffcf542a4bc974cafc84502a3/LICENSE) | [2026-11-12](https://github.com/NVIDIA-NeMo/Speech/commit/079e48770098a4cffcf542a4bc974cafc84502a3) | [저장소](https://github.com/NVIDIA-NeMo/Speech) | [상세 보기](docs/ko/nemo-speech.md) |
| **Cosmos RL** | AlpaGym에서 사용하는 분산 강화학습 인프라 | [Apache-2.0](https://github.com/nvidia-cosmos/cosmos-rl/blob/614e7c55b73a0d643c13b69c65caac13a2ce1b2a/LICENSE) (제한적 유지보수) | [2026-11-11](https://github.com/nvidia-cosmos/cosmos-rl/commit/614e7c55b73a0d643c13b69c65caac13a2ce1b2a) | [저장소](https://github.com/nvidia-cosmos/cosmos-rl) | [상세 보기](docs/ko/cosmos-rl.md) |
| **Cosmos Xenna** | 데이터 정제 파이프라인에서 사용하는 Ray 기반 분산 단계 실행 | [Apache-2.0](https://github.com/nvidia-cosmos/cosmos-xenna/blob/d9d0defb90b6c32935c379db71466f266ff8e35f/LICENSE) (제한적 유지보수) | [2026-11-09](https://github.com/nvidia-cosmos/cosmos-xenna/commit/d9d0defb90b6c32935c379db71466f266ff8e35f) | [저장소](https://github.com/nvidia-cosmos/cosmos-xenna) | [상세 보기](docs/ko/cosmos-xenna.md) |

### 자율주행

![AlpaSim에서 관측과 행동을 반복해 차량 상태를 갱신합니다. 선택적 후학습 경로에서는 AlpaGym이 에피소드를 채점하고 Cosmos RL이 정책을 업데이트합니다.](assets/section-diagrams/autonomous-driving.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 최근 커밋 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|---|
| **AlpaSim** | 자율주행 정책의 폐루프 시뮬레이션 | [Apache-2.0](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/LICENSE) 코드; 모델·데이터 별도 | [2026-08-18](https://github.com/NVlabs/alpasim/commit/affc2eab209fa43bdfa2f26c0f8d437922d78a68) | [저장소](https://github.com/NVlabs/alpasim) | [상세 보기](docs/ko/alpasim.md) |
| **AlpaGym** | 자율주행 정책 강화학습 | [Apache-2.0](https://github.com/NVlabs/alpagym/blob/972d160eed0e23d388497851504a3a233fec5879/LICENSE) 코드; 의존성·모델 별도 | [2026-07-21](https://github.com/NVlabs/alpagym/commit/972d160eed0e23d388497851504a3a233fec5879) | [저장소](https://github.com/NVlabs/alpagym) | [상세 보기](docs/ko/alpagym.md) |
| **NuRec SDK source** | 신경 장면 복원과 센서 렌더링용 GPU 라이브러리·앱·API | 저장소 [Apache-2.0](https://github.com/NVIDIA/NuRec/blob/ffce3667841691c7fe2ca763c5c10e2949c8ca0e/LICENSE.md). 런타임 이미지·가중치·데이터는 별도 배포 | [2026-10-30](https://github.com/NVIDIA/NuRec/commit/ffce3667841691c7fe2ca763c5c10e2949c8ca0e) | [저장소](https://github.com/NVIDIA/NuRec) · [라이선스](https://github.com/NVIDIA/NuRec/blob/main/LICENSE.md) | [상세 보기](docs/ko/nurec.md) |
| **NCore** | 센서 기록과 보정값·자세를 담는 공통 형식 및 변환용 Python 도구 | 코드 [Apache-2.0](https://github.com/NVIDIA/ncore/blob/ffad25e40b38721ef23216d365251a698be175b5/LICENSE). 주행 데이터셋과 변환 플러그인은 별도 조건 | [2026-11-12](https://github.com/NVIDIA/ncore/commit/ffad25e40b38721ef23216d365251a698be175b5) | [저장소](https://github.com/NVIDIA/ncore) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **Asset Harvester** | 주행 로그에서 NuRec 장면에 삽입할 Gaussian 객체 자산 추출 | 코드 [Apache-2.0](https://github.com/NVIDIA/asset-harvester/blob/b45e5dec6d23751682f44ff2225ac9aa23d564a3/LICENSE.txt). 체크포인트 접근·이용 조건은 별도 | [2026-11-06](https://github.com/NVIDIA/asset-harvester/commit/b45e5dec6d23751682f44ff2225ac9aa23d564a3) | [저장소](https://github.com/NVIDIA/asset-harvester) · [모델 카드](https://huggingface.co/nvidia/asset-harvester) | [관련 가이드](docs/ko/nurec.md) |
| **NuRec Skills** | 복원 및 객체 자산 처리를 포함한 NuRec 작업용 에이전트 스킬 | [Apache-2.0](https://github.com/NVIDIA/nurec-skills/blob/28fdd9c83cc2952dd265f33012c813d662e2ed90/LICENSE) 기반(상표 조항 수정). NuRec 런타임과 가져온 에셋에는 별도 조건 적용 | [2026-11-05](https://github.com/NVIDIA/nurec-skills/commit/28fdd9c83cc2952dd265f33012c813d662e2ed90) | [저장소](https://github.com/NVIDIA/nurec-skills) | [관련 가이드](docs/ko/nurec.md) |
| **Alpamayo Recipes** | Alpamayo 모델 튜닝·양자화·배포 예제 | 코드 [Apache-2.0](https://github.com/NVlabs/alpamayo-recipes/blob/622f9d23ff9e4961ba8c6aac71367776cdf6b016/LICENSE). 모델과 데이터는 별도 조건 | [2026-11-11](https://github.com/NVlabs/alpamayo-recipes/commit/622f9d23ff9e4961ba8c6aac71367776cdf6b016) | [저장소](https://github.com/NVlabs/alpamayo-recipes) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **OmniDreams** | 자율주행 시뮬레이션용 자기회귀 영상 모델 코드와 선택형 AlpaSim 렌더러 경로 | 저장소 [Apache-2.0](https://github.com/nv-tlabs/omni-dreams/blob/50f36212c03012a85f12fe3b33e9deb23c8da749/LICENSE). 가중치와 접근 조건은 별도 | [2026-10-02](https://github.com/nv-tlabs/omni-dreams/commit/50f36212c03012a85f12fe3b33e9deb23c8da749) | [저장소](https://github.com/nv-tlabs/omni-dreams) · [모델 카드](https://huggingface.co/nvidia/omni-dreams-models) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **FlashDreams** | 자기회귀 영상·월드 모델 추론 가속 및 서비스 연동 | 소스 대부분 [Apache-2.0](https://github.com/NVIDIA/flashdreams/blob/614969691a78400c868225db2d192b33cc55a25e/LICENSE). 파일별 예외와 외부 모델 조건은 별도 확인 | [2026-11-11](https://github.com/NVIDIA/flashdreams/commit/614969691a78400c868225db2d192b33cc55a25e) | [저장소](https://github.com/NVIDIA/flashdreams) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **Alpamayo 2 Super code** | 추론 근거·궤적 생성과 자동 라벨링을 위한 34B 주행 VLA 추론 | [Apache-2.0](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/LICENSE). 가중치는 OpenMDW-1.1 | [2026-10-07](https://github.com/NVlabs/alpamayo2/commit/59776920bbd981f2c989213bba5ee8594e71ed1d) | [저장소](https://github.com/NVlabs/alpamayo2) | [가이드](docs/ko/alpamayo.md) |
| **Alpamayo 2 Edge code** | 차량 탑재 환경용 경량 주행 VLA 추론·내보내기 도구 | [Apache-2.0](https://github.com/NVlabs/alpamayo2-edge/blob/02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e/LICENSE). 가중치는 OpenMDW-1.1 | [2026-11-10](https://github.com/NVlabs/alpamayo2-edge/commit/02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e) | [저장소](https://github.com/NVlabs/alpamayo2-edge) | [가이드](docs/ko/alpamayo.md) |
| **AlpaJudge code** | 주행 궤적과 추론 근거를 평가하는 VLM | [Apache-2.0](https://github.com/NVlabs/alpajudge/blob/607ae9d2c56e08a9f55a1093ce625af43a53b114/LICENSE). [가중치는 OpenMDW-1.1](https://huggingface.co/nvidia/alpajudge) | [2026-10-29](https://github.com/NVlabs/alpajudge/commit/607ae9d2c56e08a9f55a1093ce625af43a53b114) | [저장소](https://github.com/NVlabs/alpajudge) | [가이드](docs/ko/alpamayo.md) |

## 데이터와 시뮬레이션 자산

![SimReady에서 OpenUSD 장면 자산을 찾고, Hugging Face의 NVIDIA Physical AI 컬렉션에서 학습·평가용 데이터를 탐색하는 두 경로.](assets/section-diagrams/data-assets.ko.svg)

### 검색 플랫폼과 도구

| 항목 | 역할 | 공개 및 이용 조건 | 공식 출처 | 상세 설명 |
|---|---|---|---|---|
| **SimReady Foundation** | OpenUSD 자산 프로파일·규격·검증 도구 및 예제 | NVIDIA 작성 콘텐츠 Apache-2.0; 제3자 자산은 별도 라이선스 | [GitHub](https://github.com/NVIDIA/simready-foundation) | [상세 보기](docs/ko/simready-foundation.md) |
| **SimReady Central Library** | NVIDIA와 다른 소유자의 시뮬레이션 자산 검색·탐색 | 공개 탐색 가능; 자산별 라이선스가 다르며 비상업용 자산도 포함 | [Hugging Face Space](https://huggingface.co/spaces/nvidia/simready-central) · [공식 문서](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html) | [상세 보기](docs/ko/simready-central-library.md) |
| **SimReady Central** | 소유자가 Hugging Face에 보관한 자산의 제출·검토 인덱스 | 저장소 공개; 제출을 위한 온보딩과 자산 이용 조건은 별도 | [GitHub](https://github.com/NVIDIA-Omniverse/simready-central) | [상세 보기](docs/ko/simready-central.md) |
| **NVIDIA Physical AI 데이터셋 컬렉션** | 로봇·자율주행 등 NVIDIA 데이터셋의 통합 탐색 출발점 | 데이터셋별 접근 및 이용 조건 상이 | [컬렉션](https://huggingface.co/collections/nvidia/physical-ai) · [NVIDIA 전체 데이터셋](https://huggingface.co/nvidia/datasets) | [상세 보기](docs/ko/physical-ai-dataset-collection.md) |
| **Human-1M Explorer** | 사람의 1인칭 촬영 및 복원 사례 탐색 | Space 공개; 데이터셋 접근과 약관은 별도 | [Hugging Face Space](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer) | [상세 보기](docs/ko/human-1m-explorer.md) |

아래 라이선스는 **2026년 11월 9일**에 확인한 Hugging Face 라이선스 태그이며 데이터 카드와 실제 약관을 대신하지 않는다. ‘공개’는 접근 제한이 표시되지 않았다는 뜻으로, 오픈소스 또는 무제한 이용을 의미하지 않는다. CC BY는 출처 표시가 필요하며 CC BY-NC는 상업적 사용을 제한한다. `기타` 또는 태그가 없는 경우 개별 확인이 필요하다. 자산에 포함된 제3자 자료에도 별도 조건이 적용될 수 있다.

### 3D 자산과 환경

| 데이터셋 | 역할 | 라이선스 태그 · 접근 | 상세 설명 |
|---|---|---|---|
| **[simready-assets](https://huggingface.co/datasets/nvidia/simready-assets)** | SimReady 3D 소품·물체 자산 | CC BY 4.0; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#simready-assets) |
| **[simready-dsx](https://huggingface.co/datasets/nvidia/simready-dsx)** | AI 팩토리 디지털 트윈용 SimReady 자산 | CC BY 4.0; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#simready-dsx) |
| **[isaacsim-assets](https://huggingface.co/datasets/nvidia/isaacsim-assets)** | Isaac Sim 자산 및 예제 콘텐츠 | 라이선스 미확인 | [상세 보기](docs/ko/datasets-3d-assets.md#isaacsim-assets) |
| **[PhysicalAI-SimReady-Warehouse-01](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01)** | OpenUSD 기반 창고 시뮬레이션 장면 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#physicalai-simready-warehouse-01) |
| **[PhysicalAI-DigitalCousin-Assets](https://huggingface.co/datasets/nvidia/PhysicalAI-DigitalCousin-Assets)** | GR1 탁상 작업 환경용 시뮬레이션 자산 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#physicalai-digitalcousin-assets) |
| **[PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF)** | MJCF 형식의 주방 물체 자산 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#physicalai-robotics-manipulation-objects-kitchen-mjcf) |
| **[PhysicalAI-Robotics-PhysicalAssets-VoMP](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP)** | 시각 기반 로봇 동작계획 연구용 자산 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#physicalai-robotics-physicalassets-vomp) |
| **[PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval)** | 시각 기반 동작계획 평가용 자산 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-3d-assets.md#physicalai-robotics-physicalassets-vomp-eval) |

### 로봇 시연과 동작

| 데이터셋 | 역할 | 라이선스 태그 · 접근 | 상세 설명 |
|---|---|---|---|
| **[PhysicalAI-Robotics-GR00T-X-Embodiment-Sim](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-X-Embodiment-Sim)** | 여러 로봇 형태의 GR00T 후학습용 시뮬레이션 궤적 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-gr00t-x-embodiment-sim) |
| **[PhysicalAI-GR00T-Tuned-Tasks](https://huggingface.co/datasets/nvidia/PhysicalAI-GR00T-Tuned-Tasks)** | GR1 탁상 조작을 위한 멀티모달 궤적 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-gr00t-tuned-tasks) |
| **[PhysicalAI-Robotics-GR00T-GR1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-GR1)** | GR1 로봇 작업을 촬영한 제3자 시점 영상 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-gr00t-gr1) |
| **[PhysicalAI-Robotics-GR00T-Teleop-G1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1)** | 원격 조작으로 수집한 Unitree G1 시연 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-gr00t-teleop-g1) |
| **[GR00T-N1.7-AppleToPlate](https://huggingface.co/datasets/nvidia/GR00T-N1.7-AppleToPlate)** | G1 사과 옮기기 원격 조작 시연 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#gr00t-n1-7-appletoplate) |
| **[PhysicalAI-Robotics-GR00T-Teleop-Sim](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-Sim)** | 시뮬레이션 원격 조작 시연 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-gr00t-teleop-sim) |
| **[PhysicalAI-Robotics-GR00T-Teleop-GR1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-GR1)** | GR1 원격 조작 데이터 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-gr00t-teleop-gr1) |
| **[PhysicalAI-Robotics-GR00T-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Eval)** | GR00T 로봇 평가 데이터 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-gr00t-eval) |
| **[PhysicalAI-Robotics-Manipulation-Kitchen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen)** | LeRobot 형식의 주방 조작 시뮬레이션 궤적 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-manipulation-kitchen) |
| **[PhysicalAI-Robotics-Manipulation-SingleArm](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-SingleArm)** | 단일 로봇팔 조작 시뮬레이션 데이터 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-manipulation-singlearm) |
| **[PhysicalAI-Robotics-Manipulation-Objects](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects)** | 물체 집기·놓기 시뮬레이션 궤적 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-manipulation-objects) |
| **[PhysicalAI-Robotics-Manipulation-Augmented](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Augmented)** | 합성·주석 처리된 큐브 쌓기 시연 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-manipulation-augmented) |
| **[PhysicalAI-Robotics-Manipulation-Kitchen-Demos](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen-Demos)** | 사람의 원격 조작으로 수집한 주방 작업 시연 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-manipulation-kitchen-demos) |
| **[PhysicalAI-Robotics-GraspGen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen)** | 여러 그리퍼와 물체에 대한 파지 후보 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-graspgen) |
| **[PhysicalAI-Robotics-Locomanipulation-GRAIL](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL)** | 로봇 이동·조작 동작 데이터 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-locomanipulation-grail) |
| **[PhysicalAI-Robotics-Open-H-Embodiment](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment)** | 수술 로봇·초음파 자율화 데이터 이니셔티브 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-open-h-embodiment) |
| **[PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box)** | GR1 드릴을 상자에 넣는 작업 궤적 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-mindmap-gr1-drill-in-box) |
| **[PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin)** | GR1 막대를 통에 넣는 작업 궤적 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-mindmap-gr1-stick-in-bin) |
| **[PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer)** | Franka 머그잔을 서랍에 넣는 작업 궤적 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-mindmap-franka-mug-in-drawer) |
| **[PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking)** | Franka 큐브 쌓기 작업 궤적 | CC-BY-NC-4.0; 공개 | [상세 보기](docs/ko/datasets-robot-demonstrations.md#physicalai-robotics-mindmap-franka-cube-stacking) |

### 로봇 인지

| 데이터셋 | 역할 | 라이선스 태그 · 접근 | 상세 설명 |
|---|---|---|---|
| **[Microduck Duck Detector Dataset](https://huggingface.co/datasets/pollen-robotics/microduck-duck-detector-dataset)** | 다른 Microduck을 탐지하기 위한 로봇 카메라 이미지와 바운딩 박스 | Apache-2.0, 공개 | [상세 보기](docs/ko/microduck.md#hugging-face-리소스) |

### 자율주행·영상·월드 모델 데이터

| 데이터셋 | 역할 | 라이선스 태그 · 접근 | 상세 설명 |
|---|---|---|---|
| **[PhysicalAI-Autonomous-Vehicles](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)** | 실제 자율주행 다중 센서 데이터 | 별도 약관 확인; 로그인·접근 동의 필요 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-autonomous-vehicles) |
| **[PhysicalAI-Autonomous-Vehicles-NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec)** | NuRec으로 재구성한 주행 장면 | 별도 약관 확인; 로그인·접근 동의 필요 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-autonomous-vehicles-nurec) |
| **[NuRec-AV-Object-Benchmark](https://huggingface.co/datasets/nvidia/NuRec-AV-Object-Benchmark)** | 자율주행 물체 중심 3D 재구성 벤치마크 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#nurec-av-object-benchmark) |
| **[PhysicalAI-Autonomous-Vehicles-NCore](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NCore)** | NCore 기반 자율주행 센서 데이터 | 별도 약관 확인; 로그인·접근 동의 필요 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-autonomous-vehicles-ncore) |
| **[PhysicalAI-Autonomous-Vehicles-Foundation4D](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-Foundation4D)** | 4D 재구성을 위한 자율주행 데이터 | 별도 약관 확인; 로그인·접근 동의 필요 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-autonomous-vehicles-foundation4d) |
| **[PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams)** | Cosmos 기반 합성 주행 데이터 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-autonomous-vehicle-cosmos-drive-dreams) |
| **[PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic)** | 합성 주행 데이터; 데이터 카드에서 Cosmos Drive Dreams 참조 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-autonomous-vehicle-cosmos-synthetic) |
| **[PhysicalAI-SmartSpaces](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces)** | 사람과 이동 장비 추적을 위한 다중 카메라 영상 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-smartspaces) |
| **[PhysicalAI-Traffic-Anomaly-Reasoning](https://huggingface.co/datasets/nvidia/PhysicalAI-Traffic-Anomaly-Reasoning)** | 교통 이상 상황 추론·평가 데이터 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-traffic-anomaly-reasoning) |
| **[PhysicalAI-Human-1M-100K](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)** | 동작·언어 주석이 포함된 사람의 1인칭 영상 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-human-1m-100k) |
| **[PhysicalAI-Spatial-Intelligence-Warehouse](https://huggingface.co/datasets/nvidia/PhysicalAI-Spatial-Intelligence-Warehouse)** | 창고 장면의 공간 지능 데이터 | CC-BY-4.0; 로그인·접근 동의 필요 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-spatial-intelligence-warehouse) |
| **[PhysicalAI-Robotics-NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-NuRec)** | 로봇용 신경 재구성 데이터 | CC-BY-4.0; 로그인·접근 동의 필요 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-robotics-nurec) |
| **[PhysicalAI-NuRec-PPISP](https://huggingface.co/datasets/nvidia/PhysicalAI-NuRec-PPISP)** | 재구성·이미지 처리를 위한 장면 촬영 데이터 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-nurec-ppisp) |
| **[PhysicalAI-SpatialIntelligence-Lyra-SDG](https://huggingface.co/datasets/nvidia/PhysicalAI-SpatialIntelligence-Lyra-SDG)** | 공간 지능 연구용 합성 데이터 | CC-BY-4.0; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-spatialintelligence-lyra-sdg) |
| **[PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios)** | 월드 모델용 합성 자율주행 장면 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-worldmodel-synthetic-autonomous-driving-scenarios) |
| **[PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes)** | 월드 모델용 합성 로봇 장면 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-worldmodel-synthetic-embodied-robot-scenes) |
| **[PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes)** | 합성 디지털 휴먼 영상 장면 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-worldmodel-synthetic-digital-human-scenes) |
| **[PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes)** | 물리 시뮬레이션 기반 다중 물체 상호작용 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-worldmodel-synthetic-physical-interaction-scenes) |
| **[PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes)** | 합성 창고 운영 및 안전 이벤트 영상 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-worldmodel-synthetic-warehouse-operations-scenes) |
| **[PhysicalAI-Event-Videos](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos)** | 영상 이상 상황·안전 이벤트 및 주석 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-event-videos) |
| **[PhysicalAI-VANTAGE-Bench](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench)** | 고정 카메라 영상 이해 벤치마크 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-vantage-bench) |
| **[PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)** | 고정 카메라 영상 벤치마크의 부분집합 | 별도 약관 확인; 공개 | [상세 보기](docs/ko/datasets-driving-world-model.md#physicalai-vantage-bench-subset) |

### V2D 및 Cosmos 데이터셋

| 데이터셋 | 역할 | 라이선스 태그 · 접근 | 상세 설명 |
|---|---|---|---|
| **[video-to-data-robot-dexterity-task-library-and-dataset](https://huggingface.co/datasets/nvidia/video-to-data-robot-dexterity-task-library-and-dataset)** | V2D 사람 손 시연을 로봇 손으로 리타기팅한 데이터 | CC BY 4.0; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#video-to-data-robot-dexterity-task-library-and-dataset) |
| **[Cosmos-Reason1-RL-Dataset](https://huggingface.co/datasets/nvidia/Cosmos-Reason1-RL-Dataset)** | 추론 강화학습용 영상·텍스트 주석 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-reason1-rl-dataset) |
| **[Cosmos-Reason1-Benchmark](https://huggingface.co/datasets/nvidia/Cosmos-Reason1-Benchmark)** | 영상 추론 평가 주석 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-reason1-benchmark) |
| **[Cosmos-Reason1-SFT-Dataset](https://huggingface.co/datasets/nvidia/Cosmos-Reason1-SFT-Dataset)** | 지도 추론 학습용 영상·텍스트 주석 | CC BY 4.0; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-reason1-sft-dataset) |
| **[Cosmos-Transfer-LidarGen-Example](https://huggingface.co/datasets/nvidia/Cosmos-Transfer-LidarGen-Example)** | LiDAR 생성 예제 데이터 | 별도 약관; 접근 제한 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-transfer-lidargen-example) |
| **[Cosmos-Transfer1-7B-Sample-AV-Data-Example](https://huggingface.co/datasets/nvidia/Cosmos-Transfer1-7B-Sample-AV-Data-Example)** | Cosmos Transfer용 자율주행 입력 예제 | CC BY 4.0; 접근 제한 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-transfer1-7b-sample-av-data-example) |
| **[ALOHA-Cosmos-Policy](https://huggingface.co/datasets/nvidia/ALOHA-Cosmos-Policy)** | Cosmos Policy 학습용 실제 양손 조작 데이터 | CC 태그; 상세 약관 확인 필요 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#aloha-cosmos-policy) |
| **[LIBERO-Cosmos-Policy](https://huggingface.co/datasets/nvidia/LIBERO-Cosmos-Policy)** | Cosmos Policy용 LIBERO 시뮬레이션 데이터 | CC 태그; 상세 약관 확인 필요 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#libero-cosmos-policy) |
| **[RoboCasa-Cosmos-Policy](https://huggingface.co/datasets/nvidia/RoboCasa-Cosmos-Policy)** | Cosmos Policy용 RoboCasa 시뮬레이션 데이터 | CC 태그; 상세 약관 확인 필요 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#robocasa-cosmos-policy) |
| **[Cosmos-HumanEval-v1](https://huggingface.co/datasets/nvidia/Cosmos-HumanEval-v1)** | Cosmos 출력의 사람 평가 데이터 | 별도 약관 확인 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-humaneval-v1) |
| **[Cosmos-AnomalyGen-PCB-Dataset](https://huggingface.co/datasets/nvidia/Cosmos-AnomalyGen-PCB-Dataset)** | PCB 결함 생성 데이터 | 별도 약관 확인 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-anomalygen-pcb-dataset) |
| **[Cosmos-AnomalyGen-Glass-Masks](https://huggingface.co/datasets/nvidia/Cosmos-AnomalyGen-Glass-Masks)** | 유리 결함 생성용 마스크 | 라이선스 미확인; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos-anomalygen-glass-masks) |
| **[Cosmos3-DROID](https://huggingface.co/datasets/nvidia/Cosmos3-DROID)** | Cosmos 3용 로봇 조작 시연 | OpenMDW-1.1; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos3-droid) |
| **[Cosmos3-Driving-Simulation-Evaluation](https://huggingface.co/datasets/nvidia/Cosmos3-Driving-Simulation-Evaluation)** | 자율주행 시뮬레이션 평가용 제어 영상·설명 | OpenMDW-1.1; 공개 | [상세 보기](docs/ko/datasets-v2d-cosmos.md#cosmos3-driving-simulation-evaluation) |

**연계 예:** SimReady 자산으로 Isaac Sim·Isaac Lab 장면을 구성하고, Capture·GR00T 시연이나 기존 데이터셋으로 정책을 학습한 뒤 평가할 수 있다. 각 데이터셋의 로봇 형태·좌표계·센서와 라이선스가 호환되는지 따로 확인해야 한다.

## 로봇 파운데이션 모델과 VLA

로봇 파운데이션 모델(RFM)은 여러 작업이나 로봇 데이터로 사전 학습한 뒤, 사용할 로봇에 맞춰 적용하는 모델입니다. VLA(시각·언어·행동) 모델은 카메라 관측, 지시문, 필요에 따라 로봇 상태를 받아 행동을 출력합니다. 월드 액션 모델은 행동과 미래 관측을 함께 예측할 수 있습니다. 먼저 대상 로봇이나 벤치마크를 정한 뒤 체크포인트와 이용 조건을 확인하세요. [모델 선택과 평가](docs/ko/robot-foundation-models.md)

| 모델 | 개발팀과 역할 | 체크포인트 공개 여부 및 조건 | 공식 자료 |
|---|---|---|---|
| **GR00T N1.7** | NVIDIA · 휴머노이드·로봇팔 VLA | 3B 체크포인트 다운로드 · [NVIDIA Open Model License](https://huggingface.co/nvidia/GR00T-N1.7-3B/blob/main/LICENSE) | [모델 카드](https://huggingface.co/nvidia/GR00T-N1.7-3B) · [가이드](docs/ko/groot-model.md) |
| **GR00T 2 / Turbo** | NVIDIA · 조작용 Cosmos 기반 월드 액션 모델(WAM) | 11월 9일 발표 · 2026년 12월 코드 공개 예정 · 공개 체크포인트와 가중치 조건 미확인 | [공식 연구 페이지](https://research.nvidia.com/labs/gear/gr00t-2/) · [가이드](docs/ko/groot-model.md) |
| **GR00T-H N1.7** | NVIDIA · 의료 로봇 연구용 VLA | 다운로드 가능 · [NVIDIA Open Model License](https://huggingface.co/nvidia/GR00T-H-N1.7/blob/main/LICENSE) · 모델 카드에서 임상 용도 제외 | [모델 카드](https://huggingface.co/nvidia/GR00T-H-N1.7) · [가이드](docs/ko/gr00t-h.md) |
| **π₀ / π₀-FAST / π₀.₅** | Physical Intelligence · 로컬 추론·파인튜닝용 범용 로봇 VLA | openpi에서 다운로드 · 체크포인트와 백본별 조건 확인 · openpi 코드는 Apache-2.0 | [공식 체크포인트](https://github.com/Physical-Intelligence/openpi#model-checkpoints) · [가이드](docs/ko/physical-intelligence-pi.md) |
| **π₀.₆ / π*₀.₆ / π₀.₇** | Physical Intelligence · 실기 경험 학습과 조건에 따른 행동 조절 | 연구 결과 공개 · 다운로드 가중치 미확인 · Pi API 호스팅 베타는 대기 신청, 제공 모델 ID 미공개 | [π*₀.₆](https://www.pi.website/blog/pistar06) · [π₀.₇](https://www.pi.website/blog/pi07) · [Pi API](https://www.pi.website/blog/api-beta) |
| **Cosmos 3 Policy DROID** | NVIDIA · DROID 조작 행동 정책 · Edge 4B·Nano 16B | 다운로드 가능 · [OpenMDW-1.1](https://openmdw.ai/) | [Edge 모델 카드](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) · [Nano 모델 카드](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID) |
| **Cosmos Policy (Predict2)** | NVIDIA · 영상 월드 모델 기반 로봇 정책과 선택적 플래닝 | 다운로드 가능 · 링크한 체크포인트는 NVIDIA One-Way Noncommercial License | [LIBERO 모델 카드와 약관](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B#license) · [컬렉션](https://huggingface.co/collections/nvidia/cosmos-policy) |
| **SmolVLA** | Hugging Face · SO-100·SO-101 등에서 시작하기 좋은 경량 LeRobot VLA | 베이스 체크포인트 다운로드 · Apache-2.0 | [모델 카드](https://huggingface.co/lerobot/smolvla_base) · [LeRobot 가이드](https://huggingface.co/docs/lerobot/smolvla) |
| **OpenVLA** | OpenVLA 연구팀 · 7B 조작 VLA와 파인튜닝 기준 모델 | 다운로드 가능 · 모델 카드에는 MIT 표기 · 개발팀은 Llama 2 Community License 조건도 적용된다고 명시 | [모델 카드](https://huggingface.co/openvla/openvla-7b) · [원본 저장소 약관](https://github.com/openvla/openvla#pretrained-vlas) |
| **MolmoAct 2** | Ai2 · 깊이 정보를 활용한 행동 추론·조작 | 베이스·작업별 체크포인트 다운로드 · [Ai2가 명시한 Apache-2.0](https://github.com/allenai/molmoact2#7-license) | [모델 카드](https://huggingface.co/allenai/MolmoAct2) · [공식 프로젝트](https://allenai.org/blog/molmoact2) |
| **X-VLA** | 2toINF · 로봇 형태별 소프트 프롬프트를 쓰는 VLA | 베이스 체크포인트 다운로드 · 모델 카드에 Apache-2.0 표기 | [모델 카드](https://huggingface.co/2toINF/X-VLA-Pt) · [LeRobot 가이드](https://huggingface.co/docs/lerobot/xvla) |
| **Praxis-1** | Runway · 영상과 로봇 행동을 함께 예측하는 월드 액션 모델 | 11월 11일 공개 · 가중치 Apache-2.0 · Hugging Face 접근 절차 필요 | [베이스](https://huggingface.co/runwayml/praxis-1-base) · [DROID](https://huggingface.co/runwayml/praxis-1-droid) · [YAM](https://huggingface.co/runwayml/praxis-1-yam) · [공식 발표](https://runway.com/news/company-news/praxis-1-is-now-available) |
| **FLUX 3 Action** | Black Forest Labs · SO-101과 DROID용 변형을 제공하는 7B 월드 액션 모델 | Hugging Face 접근 절차 필요 · [FLUX Kommunity License v1.0](https://huggingface.co/black-forest-labs/flux-3-action-so101/blob/main/LICENSE.md) | [SO-101 체크포인트](https://huggingface.co/black-forest-labs/flux-3-action-so101) · [공식 프로젝트](https://bfl.ai/models/flux-3-action) |
| **Gemini Robotics 2.5** | Google DeepMind · 정밀 조작과 여러 단계 작업을 위한 VLA | 11월 10일 발표 · 파트너 제공 중 · 공개 체크포인트와 가중치 조건 미확인 | [공식 발표](https://deepmind.google/blog/gemini-robotics-2-5-accelerates-real-world-physical-intelligence/) |

차량 궤적과 주행 추론에는 [Alpamayo 가이드](docs/ko/alpamayo.md)와 [AlpaSim 평가 가이드](docs/ko/workflows/alpasim-closed-loop.md)를 참고하세요.

## 2. 플랫폼·모델·제품·표준 및 제한적 공개 항목

이 표의 ‘공개’는 접근 가능성만 뜻하며, 오픈소스 라이선스 또는 상업적 이용 허가를 뜻하지 않는다. 확인하지 못한 조건은 미확인으로 표시한다.

| 이름 | 역할·분류 | 공개·라이선스 상태 | 공식 출처 | 상세 설명 |
|---|---|---|---|---|
| **cuVSLAM** | CUDA 가속 시각 위치 추정·SLAM 라이브러리 | NVIDIA Community License; NVIDIA 플랫폼 제한이 있는 공개 코드, ROS 래퍼와 별도 | [저장소](https://github.com/nvidia-isaac/cuVSLAM) | [상세 보기](docs/ko/cuvslam.md) |
| **Microduck** | Pollen Robotics와 Hugging Face의 소형 이족보행 로봇. 시뮬레이션 학습을 실물에 적용하는 데 활용 | 하드웨어 제품. 기구·전자 설계는 오픈소스 범위에서 제외 | [제품](https://pollen-robotics.com/microduck/) · [NVIDIA 튜토리얼](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real) | [상세 보기](docs/ko/microduck.md) |
| **Microduck Sandbox와 Arena** | 브라우저 시뮬레이션 체험 및 정책 평가 서비스 | 공개 Space. Sandbox 앱 코드는 Apache-2.0, Arena 전체 소스 라이선스는 미확인 | [Sandbox](https://huggingface.co/spaces/pollen-robotics/microduck-simulator) · [Arena](https://huggingface.co/spaces/pollen-robotics/microduck-arena) | [상세 보기](docs/ko/microduck.md#hugging-face-리소스) |
| **Microduck 정책과 체크포인트** | 배포용 ONNX 정책과 mjlab 학습 재개용 체크포인트 | 공개 모델 저장소. ONNX 정책은 Apache-2.0 태그, 학습 체크포인트는 라이선스 미확인 | [ONNX 정책](https://huggingface.co/pollen-robotics/microduck-policies) · [학습 체크포인트](https://huggingface.co/pollen-robotics/microduck-training) | [상세 보기](docs/ko/microduck.md#hugging-face-리소스) |
| **NVIDIA Omniverse** | OpenUSD 기반 3D 개발 플랫폼 | 제품·SDK와 공개 구성 요소의 조건이 각각 다름 | [공식 페이지](https://developer.nvidia.com/omniverse) | [상세 보기](docs/ko/omniverse.md) |
| **Asset Validator** | Omniverse Kit와 독립 CLI에서 규칙에 따라 OpenUSD 검증 | 공식 문서 공개. 독립 라이선스 미확인, 배포판별 조건 확인 | [공식 문서](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **OVRTX** | 애플리케이션에 내장하는 RTX 렌더링과 센서 시뮬레이션 | 프리릴리스. NVIDIA Software License Agreement와 제품별 약관 적용 | [저장소](https://github.com/NVIDIA-Omniverse/ovrtx) | [관련 가이드](docs/ko/omniverse.md) |
| **ovstage** | Omniverse 라이브러리가 공유하는 GPU 지원 장면 데이터 계층 | 프리릴리스. NVIDIA Software License Agreement와 제품별 약관 적용 | [저장소](https://github.com/NVIDIA-Omniverse/ovstage) | [관련 가이드](docs/ko/omniverse.md) |
| **Mega Omniverse Blueprint** | 산업 디지털 트윈에서 다중 로봇 운영을 검증하는 참조 아키텍처 | 참조 아키텍처. 구성 요소별 공개 범위와 라이선스가 다름 | [공식 소개](https://blogs.nvidia.com/blog/mega-omniverse-blueprint/) | [관련 가이드](docs/ko/omniverse.md) |
| **SimReady** | 시뮬레이션에 필요한 속성을 갖춘 3D 자산의 규격·지침 | 자산별 라이선스 별도; 단일 소프트웨어 프로젝트 아님 | [공식 문서](https://docs.omniverse.nvidia.com/simready/latest/index.html) | [상세 보기](docs/ko/simready.md) |
| **NuRec** | 실제 환경의 신경 재구성·렌더링 플랫폼과 런타임 이미지 | SDK 소스는 위 오픈소스 표에 수록. 런타임 이미지·모델·데이터셋은 별도 조건 | [공식 안내](https://developer.nvidia.com/omniverse/nurec) · [배포 조건](https://github.com/NVIDIA/NuRec#source-containers-and-models) | [상세 보기](docs/ko/nurec.md) |
| **Cosmos 및 Cosmos 3** | 월드 모델·도구 플랫폼 및 모델 계열 | [Cosmos 저장소](https://github.com/NVIDIA/cosmos)는 코드와 모델에 OpenMDW-1.1을 명시; OSI 승인 오픈소스라고 단정하지 않음. 개별 저장소는 별도 조건 | [공식 저장소](https://github.com/NVIDIA/cosmos) | [상세 보기](docs/ko/cosmos.md) |
| **Cosmos Predict / Transfer / Reason** | 각각 세계·영상 생성, 시각 조건 변환, 장면 추론 모델 계열 | 모델 버전과 가중치별 약관 확인; 전체를 일괄 오픈소스로 취급하지 않음 | [Cosmos 공식 저장소](https://github.com/NVIDIA/cosmos) | [상세 보기](docs/ko/cosmos-models.md) |
| **Cosmos Embed / Dataset Search** | 멀티모달 임베딩 모델·서비스 및 영상 검색 마이크로서비스 | 서비스·모델의 전체 소스 및 라이선스 미확인 | [공식 문서](https://docs.nvidia.com/cosmos/cds/latest/introduction.html) | [상세 보기](docs/ko/cosmos-embed-search.md) |
| **GR00T-Mimic / GR00T-Dreams** | 로봇 시연·합성 데이터 생성 기술·워크플로 | 독립 프로젝트 여부와 각 구현·모델의 조건은 개별 확인 필요 | [GR00T 공식 저장소](https://github.com/NVIDIA/Isaac-GR00T) | [상세 보기](docs/ko/groot-mimic-dreams.md) |
| **Isaac Manipulator** | 로봇팔 인식·파지·계획용 참조 워크플로 | Isaac ROS 패키지·모델 및 구성 요소마다 조건 상이 | [Isaac ROS 문서](https://nvidia-isaac-ros.github.io/) | [상세 보기](docs/ko/isaac-manipulator.md) |
| **Isaac ROS** | ROS 2 기반 GPU 가속 로봇 패키지 모음 | 패키지별 이용 조건이 다름. Isaac ROS Common은 [NVIDIA Isaac ROS Software License](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common/blob/7bec6ae5dbb2faa11617f40226e8932a4a94e6e4/LICENSE) 적용 | [공식 문서](https://nvidia-isaac-ros.github.io/) · [공통 코드](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common) | [상세 보기](docs/ko/isaac-ros.md) |
| **Isaac ROS cuMotion** | GPU 가속 로봇 모션 플래닝용 ROS 2 패키지 | 저장소 공개. 현재 main 브랜치는 NVIDIA Isaac ROS Software License 적용 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_cumotion) | [관련 가이드](docs/ko/isaac-manipulator.md) |
| **Isaac OS** | 결정론적 센싱·제어·AI 추론을 위한 NVIDIA Edge 로보틱스 스택 | 베타 플랫폼, 문서 공개. 배포물과 구성 요소별 약관 확인 | [공식 문서](https://docs.nvidia.com/isaac-os/overview) | — |
| **Isaac RLPT** | 사전학습 정책을 강화학습으로 개선하는 워크플로 | 독립 저장소와 라이선스 미확인 | [Isaac Lab](https://github.com/isaac-sim/IsaacLab) | [상세 보기](docs/ko/isaac-rlpt.md) |
| **Replicator** | Omniverse/Isaac Sim의 합성 데이터 생성 도구 | 제품 구성 요소; 전체 코드 공개 및 독립 라이선스 미확인 | [Isaac Sim 문서](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/index.html) | [상세 보기](docs/ko/replicator.md) |
| **EgoHand / EgoPost** | Capture의 1인칭 손·카메라 동작 관련 구성 요소 | EgoPost는 OpenMDW-1.1; EgoHand의 독립 라이선스 미확인. 상위 패키지 기본 라이선스를 일괄 적용하지 않음 | [Isaac Capture](https://github.com/NVIDIA/IsaacCapture) | [상세 보기](docs/ko/egohand-egopost.md) |
| **MimicGen** | 시연으로 다양한 로봇 행동 데이터 생성 | 소스 공개; NVIDIA Source Code License 조건을 확인해야 하며 오픈소스로 단정하지 않음 | [저장소](https://github.com/NVlabs/mimicgen) | [상세 보기](docs/ko/mimicgen.md) |
| **DexMimicGen** | 양손·다중 조작 시연 데이터 생성 연구 | 코드 NVIDIA Source Code License; 데이터 CC-BY-4.0, 코드 이용 제한 확인 | [저장소](https://github.com/NVlabs/dexmimicgen) | [상세 보기](docs/ko/dexmimicgen.md) |
| **SkillGen / SkillMimicGen** | 동작계획으로 시연 구간을 연결·생성하는 방법 | Isaac Lab 구현과 cuRobo 등 의존성의 조건을 각각 확인; 논문명과 구현명은 구분 | [Isaac Lab 구현 문서](https://github.com/isaac-sim/IsaacLab/blob/main/docs/source/features/imitation-learning/skillgen.rst) | [상세 보기](docs/ko/skillgen.md) |
| **Isaac Lab Eureka** | 언어 모델을 이용한 보상 함수 생성 연구 코드 | 공개 저장소; 적용 라이선스 미확인 | [저장소](https://github.com/NVlabs/IsaacLabEureka) | [상세 보기](docs/ko/isaac-lab-eureka.md) |
| **FoundationPose** | 물체 6D 자세 추정·추적 연구 코드·모델 | 연구 저장소 코드는 비상업적 사용 제한; 별도 배포 모델은 별도 조건 | [코드](https://github.com/NVlabs/FoundationPose) · [모델 카드](https://huggingface.co/nvidia/foundationpose) | [상세 보기](docs/ko/foundationpose.md) |
| **FoundationStereo** | 스테레오 깊이 추정 연구 코드·모델 | 연구 코드 비상업적 제한; 별도 상업용 모델 제공 여부와 조건은 해당 배포물 확인 | [저장소](https://github.com/NVlabs/FoundationStereo) | [상세 보기](docs/ko/foundationstereo.md) |
| **nvblox** | 3D 공간 매핑·장애물 표현 라이브러리 | 코드 공개; 저장소의 혼합 라이선스 범위 미확인 | [저장소](https://github.com/nvidia-isaac/nvblox) | [상세 보기](docs/ko/nvblox.md) |
| **AnomalyGen** | 소수 예시를 이용한 결함 이미지 생성 워크플로 | 공개 저장소; 코드·모델·어댑터 각각의 조건 미확인 | [저장소](https://github.com/NVIDIA/cdf-anomalygen) | [상세 보기](docs/ko/anomalygen.md) |
| **Alpamayo** | 자율주행 추론·행동 모델 계열 | 2 Super·2 Edge 가중치는 OpenMDW-1.1로 공개. 사용할 체크포인트와 모델 카드 확인 | [2 Super](https://huggingface.co/nvidia/Alpamayo2-Super) · [2 Edge](https://huggingface.co/nvidia/Alpamayo2-Edge) · [AlpaSim 모델 안내](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md) | [상세 보기](docs/ko/alpamayo.md) |
| **Metropolis / VSS** | 영상 AI 플랫폼 / 영상 검색·요약 워크플로 | 플랫폼·서비스; 개별 SDK·모델의 조건 별도 | [Metropolis](https://developer.nvidia.com/metropolis) | [상세 보기](docs/ko/metropolis-vss.md) |
| **DeepStream** | 실시간 영상 분석 SDK | 제품 SDK; 공개 샘플과 바이너리의 조건 별도 | [공식 페이지](https://developer.nvidia.com/deepstream-sdk) | [상세 보기](docs/ko/deepstream.md) |
| **TAO Toolkit** | 비전 AI 모델 학습·파인튜닝 도구 | 제품·SDK; 모델과 구성 요소별 조건 확인 | [공식 페이지](https://developer.nvidia.com/tao-toolkit) | [상세 보기](docs/ko/tao-toolkit.md) |
| **Jetson / JetPack** | 엣지 AI 하드웨어 / 소프트웨어 개발 키트 | 제품·배포판; 개별 구성 요소의 조건 상이 | [Jetson](https://developer.nvidia.com/embedded/jetson-modules) · [JetPack](https://developer.nvidia.com/embedded/jetpack) | [상세 보기](docs/ko/jetson-jetpack.md) |
| **NVIDIA DRIVE** | 자율주행 하드웨어·소프트웨어 플랫폼 | 제품·플랫폼; 구성 요소별 이용 조건 확인 | [공식 페이지](https://developer.nvidia.com/drive) | [상세 보기](docs/ko/nvidia-drive.md) |
| **RTX / DGX Spark** | GPU 기술·제품군 / AI 컴퓨터 | 하드웨어·제품; 오픈소스 프로젝트 아님 | [RTX](https://www.nvidia.com/en-us/geforce/graphics-cards/) · [DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) | [상세 보기](docs/ko/rtx-dgx-spark.md) |
| **Cosmos Framework** | Cosmos 3 학습·후학습·평가·서빙 레시피 | 저장소 코드 OpenMDW-1.1 | [저장소](https://github.com/NVIDIA/cosmos-framework) | [상세 보기](docs/ko/cosmos-framework.md) |
| **NVIDIA NeMo Platform** | 모델 맞춤 학습·평가·가드레일·추론 인프라 | 플랫폼·서비스별 조건 확인 | [공식 문서](https://docs.nvidia.com/nemo/microservices/latest/about/core-concepts/platform.html) | [상세 보기](docs/ko/nemo-platform.md) |
| **NVIDIA NIM** | 에이전트와 파이프라인에서 호출하는 모델별 추론 서비스 | 플랫폼·서비스별 조건 확인 | [공식 문서](https://docs.nvidia.com/nim/) | [상세 보기](docs/ko/nvidia-nim.md) |

## 3. 대화에서 함께 언급된 외부 모델·도구

이들은 V2D 등의 구성이나 의존 기술로 언급되었으며 NVIDIA 프로젝트라는 뜻은 아니다. 공개 코드와 체크포인트의 조건은 각각 다르다.

| 이름 | 역할 | 상태 및 공식 출처 | 상세 설명 |
|---|---|---|---|
| **LangGraph** | 에이전트 워크플로 구성 | [공식 저장소](https://github.com/langchain-ai/langgraph); 라이선스·버전 확인 | [상세 보기](docs/ko/langgraph.md) |
| **SigLIP 2** | 영상·텍스트 표현 모델 | [공식 모델 카드](https://huggingface.co/google/siglip2-base-patch16-224); 모델별 조건 확인 | [상세 보기](docs/ko/siglip-2.md) |
| **Grounding DINO** | 텍스트 조건 객체 탐지 | [공식 저장소](https://github.com/IDEA-Research/GroundingDINO); 가중치 별도 | [상세 보기](docs/ko/grounding-dino.md) |
| **SAM 2 / SAM 3D** | 영상·이미지 분할 / 3D 복원 계열 | [SAM 2](https://github.com/facebookresearch/sam2) · [SAM 3D Objects](https://github.com/facebookresearch/sam-3d-objects); 모델별 약관 확인 | [상세 보기](docs/ko/sam-2-sam-3d.md) |
| **MoGe** | 단일 이미지 기반 3D 기하 추정 | [공식 저장소](https://github.com/microsoft/MoGe); 코드·가중치 조건 확인 | [상세 보기](docs/ko/moge.md) |
| **SMPL** | 인체 형상·자세 파라미터 모델 계열 | [공식 프로젝트](https://smpl.is.tue.mpg.de/); 모델 데이터 별도 이용 조건 | [상세 보기](docs/ko/smpl.md) |
| **PyTorch** | 기계학습 프레임워크 | [공식 저장소](https://github.com/pytorch/pytorch); BSD 계열, 의존성 별도 | [상세 보기](docs/ko/pytorch.md) |
| **ROS 2** | 로봇 소프트웨어 미들웨어 | [공식 문서](https://docs.ros.org/en/rolling/); 패키지별 라이선스 별도 | [상세 보기](docs/ko/ros-2.md) |
| **CUDA / TensorRT / ONNX** | GPU 컴퓨팅 플랫폼 / 추론 SDK / 모델 교환 형식 | CUDA와 TensorRT 배포물은 별도 제품 약관, [ONNX](https://github.com/onnx/onnx)는 공개 구현·표준. TensorRT 공개 코드는 위 표 참조 | [상세 보기](docs/ko/cuda-tensorrt-onnx.md) |
| **MCAP / HDF5 / URDF / CAD** | 기록 포맷 / 데이터 포맷 / 로봇 기술 형식 / 설계 일반 개념 | 형식·개념과 이를 구현하는 코드의 라이선스는 별개. [MCAP](https://mcap.dev/) · [HDF5](https://www.hdfgroup.org/solutions/hdf5/) · [URDF](https://github.com/ros/urdfdom) | [상세 보기](docs/ko/mcap-hdf5-urdf-cad.md) |

## 4. 연결 관계와 명칭 정리

- **수집:** Isaac Capture의 원격 조작과 1인칭 데이터, 또는 V2D의 영상 복원 결과를 로봇 학습 데이터로 가공할 수 있다. 실제 데이터 형식과 리타기팅 호환성은 작업별로 확인한다.
- **합성·증강:** AutoData는 주로 로봇 행동 궤적을 확장한다. CDF, Cosmos 및 Replicator는 영상·이미지 등 시각 데이터 생산과 처리에 활용된다. 서로 자동으로 연결된 단일 파이프라인은 아니다.
- **시뮬레이션·학습:** Warp 위의 Newton 또는 다른 물리 백엔드를 Isaac Lab에서 선택할 수 있다. Isaac Sim은 센서·렌더링·로봇 환경을 제공하며, 일부 Lab 워크플로는 Isaac Sim 없이도 실행된다. [Lab 릴리스 설명](https://github.com/isaac-sim/IsaacLab/releases).
- **모델·평가·배포:** GR00T 등의 정책을 데이터로 학습하고 Lab-Arena나 시뮬레이터에서 평가한 뒤, Isaac ROS·TensorRT·Jetson 등과 결합할 수 있다. OSMO와 CDF Orchestration은 해당 작업의 실행 관리를 맡는다.
- **통합한 이름:** 질문의 `issac`, `lssac`은 **Isaac**으로 정정했다. Isaac Teleop은 현재 Isaac Capture에 포함된 이전 명칭으로 통합했다. Physical AI Data Factory 저장소는 Cosmos Data Factory로 연결되며, `paidf-*`의 위 세 저장소도 현재 `cdf-*`로 연결된다. GR00T의 숫자는 영문 O가 아니라 숫자 0이다.
- **별도 워크플로 이름:** Video Data Augmentation, Event Video Generation, Defect Image Generation, Image Attribute Augmentation, Autonomous Vehicle Dataset Generation은 CDF의 워크플로이며 독립 저장소로 임의 분류하지 않았다. Ego Pipeline, Video Ingestion Agent, Reconstruction, Robotic Grounding 및 recording/replay 등은 기능·단계다.

## 검증 방법과 한계

대화 원문을 다시 읽어 이름을 수집하고 중복 표기를 통합했다. 공식 GitHub 저장소는 GitHub의 저장소 응답과 README·LICENSE 정보를 확인했으며, 저장소가 리디렉션되는 경우 현재 주소를 사용했다. 공식 문서·제품 링크도 접근 여부를 확인했다. 접속 상태는 변할 수 있고 일부 사이트는 지역·로그인·자동 접근 제한으로 확인이 어려울 수 있다. 저장소의 공개 여부, 특정 버전의 라이선스, 가중치 이용 조건 및 제3자 의존성은 각각 별개이므로 도입 전에 대상 버전의 LICENSE와 모델 카드를 재확인해야 한다. 이전 대화에 있던 구체적인 GPU 호환성이나 모델 버전 주장은 이 목록의 라이선스 검증으로 보증되지 않는다.

## 기여와 라이선스

오류 제보와 항목 추가 제안은 [GitHub Issues](https://github.com/james-joobs/awesome-nvidia-physical-ai/issues)에 남겨주세요. PR을 보내려면 [기여 가이드](CONTRIBUTING.md)를 참고하세요.

저장소의 원본 콘텐츠는 [MIT 라이선스](LICENSE)를 적용합니다. 외부 이미지, 아이콘, 상표와 자료는 [출처 및 이용 조건](NOTICE.md)에서 확인할 수 있습니다.
