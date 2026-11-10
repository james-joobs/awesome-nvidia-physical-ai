<div align="center">

# Awesome NVIDIA Physical AI

[English](README.md) · **한국어**

**만들고 싶은 결과를 고르고, 필요한 NVIDIA Physical AI 도구와 첫 실행을 위한 공식 예제를 찾으세요.**

시뮬레이션, 로보틱스, 자율주행과 이들이 함께 사용하는 데이터·3D 자산을 연결하는 비공식 커뮤니티 가이드입니다.

[목표별로 시작](#만들고-싶은-것부터-시작하세요) · [생태계 지도](#생태계-한눈에-보기) · [데이터와 자산](#데이터와-시뮬레이션-자산) · [NeMo](#nemo와-물리-ai-도구) · [전체 목록](#1-오픈소스-코드가-확인된-프로젝트) · [최신 릴리스](https://github.com/james-joobs/awesome-nvidia-physical-ai/releases/latest)

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

## 1. 오픈소스 코드가 확인된 프로젝트

### 물리, 3D 및 시뮬레이션

![두 시뮬레이션 경로. OpenUSD 장면은 Isaac Sim과 PhysX에서 실행할 수 있고, Warp 기반 Newton은 Isaac Lab 학습 환경을 독립 실행할 수 있습니다.](assets/section-diagrams/physics-simulation.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|
| **Newton** | Warp 기반 GPU 물리 엔진과 로봇 시뮬레이션 솔버 | Apache-2.0 | [저장소](https://github.com/newton-physics/newton) | [상세 보기](docs/ko/newton.md) |
| **NVIDIA Warp** | GPU 가속 물리·기하 계산용 Python 프레임워크 | Apache-2.0 | [저장소](https://github.com/NVIDIA/warp) | [상세 보기](docs/ko/nvidia-warp.md) |
| **NVIDIA PhysX** | 강체·충돌 등 물리 시뮬레이션 엔진 | BSD-3-Clause; 일부 추가 구성 요소는 별도 조건 확인 | [저장소](https://github.com/NVIDIA-Omniverse/PhysX) | [상세 보기](docs/ko/nvidia-physx.md) |
| **MuJoCo Warp (MJWarp)** | MuJoCo 물리 계산의 Warp 기반 가속 구현 | Apache-2.0; Google DeepMind 프로젝트 | [저장소](https://github.com/google-deepmind/mujoco_warp) | [상세 보기](docs/ko/mujoco-warp.md) |
| **OpenUSD** | 3D 장면과 자산 교환·구성을 위한 프레임워크 | 수정 BSD 계열; 표준 및 상표와 구현은 구분 | [저장소](https://github.com/PixarAnimationStudios/OpenUSD) | [상세 보기](docs/ko/openusd.md) |
| **Isaac Sim** | 로봇·센서·환경 시뮬레이션 참조 애플리케이션 | 저장소 코드 Apache-2.0; 전체 배포물·의존성은 별도 NVIDIA 약관이 적용될 수 있음 | [저장소](https://github.com/isaac-sim/IsaacSim) | [상세 보기](docs/ko/isaac-sim.md) |
| **PhysicsNeMo** | 물리 기반 AI 및 대리 모델 학습 프레임워크 | Apache-2.0 | [저장소](https://github.com/NVIDIA/physicsnemo) | [상세 보기](docs/ko/physicsnemo.md) |
| **OpenUSD Exchange SDK** | OpenUSD 장면 작성과 교환을 돕는 SDK | Apache-2.0 | [저장소](https://github.com/NVIDIA-Omniverse/usd-exchange) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **AIF Pipeline Samples** | CAD 변환·USD 검증·최적화·메타데이터 설정 예제 | 샘플 코드 MIT. Kit와 변환기는 별도 조건 | [저장소](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **SimFoundry** | 작업대 영상에서 객체와 물리 속성이 있는 편집 가능한 시뮬레이션 장면 생성 | 코드 Apache-2.0. 외부 모델과 자산은 별도 조건 | [저장소](https://github.com/NVlabs/SimFoundry) | [관련 가이드](docs/ko/workflows/workbench-cad-to-isaac-sim.md) |
| **fVDB Core** | GPU 가속 희소 볼륨 자료구조와 3D 연산 | Apache-2.0 | [저장소](https://github.com/openvdb/fvdb-core) | — |
| **fVDB Reality Capture** | fVDB 기반 3D Gaussian Splatting 복원·처리 도구 | 코드 Apache-2.0. 샘플과 의존성은 별도 확인 | [저장소](https://github.com/openvdb/fvdb-reality-capture) | — |
| **gsplat** | NuRec이 사용하는 CUDA 가속 Gaussian Splatting 라이브러리 | 코드 Apache-2.0. NVIDIA가 기여하는 Nerfstudio 독립 프로젝트 | [저장소](https://github.com/nerfstudio-project/gsplat) | — |
| **3DGRUT** | Gaussian 레이 트레이싱과 하이브리드 래스터화 연구 코드 | 코드 Apache-2.0. 의존성 조건은 별도 확인 | [저장소](https://github.com/nv-tlabs/3dgrut) | — |
| **OvPhysX** | Kit 설치 없이 PhysX SDK로 USD 장면의 물리 계산 | 소스 Apache-2.0. 배포 wheel과 SDK는 NVIDIA Omniverse License | [소스·라이선스](https://github.com/NVIDIA-Omniverse/PhysX/blob/main/ovphysx/README.md#5-licensing) | [관련 가이드](docs/ko/nvidia-physx.md) |

### 로봇 학습, 수집 및 제어

![Isaac Capture나 V2D로 시연을 확보하고, 데이터를 준비해 정책을 학습한 뒤 Lab-Arena에서 평가합니다. LEAPP나 Isaac ROS로 배포하고 운영 결과를 다음 수집에 반영합니다.](assets/section-diagrams/robot-learning.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|
| **Isaac Lab** | 강화·모방학습 및 로봇 학습 환경 | BSD-3-Clause; 선택한 백엔드와 의존성은 별도 조건 | [저장소](https://github.com/isaac-sim/IsaacLab) | [상세 보기](docs/ko/isaac-lab.md) |
| **Isaac Lab-Arena** | 조합 가능한 로봇 작업 환경과 정책 평가 | Apache-2.0; Isaac Sim 등 의존성 별도 | [저장소](https://github.com/isaac-sim/IsaacLab-Arena) | [상세 보기](docs/ko/isaac-lab-arena.md) |
| **RoboLab** | Isaac Lab 기반 로봇팔 조작 정책 평가 벤치마크 | 코드 Apache-2.0. 작업 자산과 정책 이용 조건은 별도 확인 | [저장소](https://github.com/NVlabs/RoboLab) | [관련 가이드](docs/ko/isaac-lab.md) |
| **Microduck 로봇 소프트웨어** | ONNX 정책 실행, 서보 제어, 장치 서비스를 담당하는 온보드 Rust 런타임 | 코드 Apache-2.0 | [저장소](https://github.com/pollen-robotics/microduck) | [상세 보기](docs/ko/microduck.md) |
| **Microduck RL** | Pollen Robotics의 mjlab·PPO 기반 Microduck 학습 환경 | 코드 Apache-2.0, 지정된 STL 메시는 CC BY-NC-SA 4.0 | [저장소](https://github.com/pollen-robotics/microduck_rl) | [상세 보기](docs/ko/microduck.md) |
| **Isaac Capture (이전 Isaac Teleop 포함)** | 원격 조작 및 1인칭 데이터 수집·기록·리타기팅 | 기본 Apache-2.0; EgoPost는 OpenMDW-1.1, CloudXR과 일부 선택 패키지는 별도 독점 조건 | [저장소](https://github.com/NVIDIA/IsaacCapture) | [상세 보기](docs/ko/isaac-capture.md) |
| **AutoData** | 소수의 시연을 다양한 작업 조건의 궤적으로 확장 | Apache-2.0; Isaac Sim 및 특정 cuRobo 구성 요소 별도 조건 | [저장소](https://github.com/isaac-sim/AutoData) | [상세 보기](docs/ko/autodata.md) |
| **Video-to-Data (V2D)** | 영상의 장면·동작을 복원하고 로봇 학습에 연결하는 파이프라인 | 소스 Apache-2.0, 문서·스킬 CC-BY-4.0; 의존 모델 별도 | [저장소](https://github.com/nvidia-isaac/video_to_data) | [상세 보기](docs/ko/video-to-data.md) |
| **Isaac GR00T 코드** | GR00T 로봇 정책의 학습·추론·배포 코드 | 코드 Apache-2.0; 모델과 가중치는 별도 조건 | [저장소](https://github.com/NVIDIA/Isaac-GR00T) | [상세 보기](docs/ko/isaac-gr00t.md) |
| **cuRobo** | GPU 기반 로봇 역기구학·동작계획 | 저장소 Apache-2.0; AutoData 배포의 특정 구성 요소는 별도 약관 확인 | [저장소](https://github.com/NVlabs/curobo) | [상세 보기](docs/ko/curobo.md) |
| **LeRobot** | 로봇 데이터셋과 모델 학습 도구; Capture와 연동 가능 | Apache-2.0; Hugging Face 프로젝트 | [저장소](https://github.com/huggingface/lerobot) | [상세 보기](docs/ko/lerobot.md) |
| **Isaac ROS** | ROS 2 기반 GPU 가속 로봇 패키지 모음 | 패키지별 조건 상이; 공통 저장소와 배포물의 개별 라이선스 확인 | [공식 문서](https://nvidia-isaac-ros.github.io/) · [공통 코드](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common) | [상세 보기](docs/ko/isaac-ros.md) |
| **Isaac ROS Visual SLAM** | ROS 2 기반 시각 주행거리 추정·SLAM 연동 | Apache-2.0; cuVSLAM은 별도 약관 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam) | [상세 보기](docs/ko/isaac-ros-visual-slam.md) |
| **Isaac ROS Nvblox** | ROS 2 3D 지도 및 Nav2 장애물 비용 지도 | Apache-2.0; 의존성 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox) | [상세 보기](docs/ko/isaac-ros-nvblox.md) |
| **Isaac ROS Pose Estimation** | GPU 가속 물체 자세 추정 패키지 | 코드 Apache-2.0; 모델 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation) | [상세 보기](docs/ko/isaac-ros-pose-estimation.md) |
| **Isaac ROS Manipulation** | ROS 2 기반 로봇팔 조작 워크플로 | 코드 Apache-2.0; 모델·의존성 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_manipulation) | [상세 보기](docs/ko/isaac-ros-manipulation.md) |
| **Isaac ROS DNN Stereo Depth** | ROS 2 신경망 스테레오 깊이 추정 | 코드 Apache-2.0; 모델 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth) | [상세 보기](docs/ko/isaac-ros-dnn-stereo-depth.md) |
| **Isaac ROS DNN Inference** | ROS 2용 TensorRT·Triton 추론 연동 | 코드 Apache-2.0; 런타임·모델 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference) | [상세 보기](docs/ko/isaac-ros-dnn-inference.md) |
| **LEAPP** | 로봇 정책의 전체 추론 파이프라인 내보내기·배포 | Apache-2.0; 모델·런타임 의존성 별도 | [저장소](https://github.com/nvidia-isaac/leapp) | [상세 보기](docs/ko/leapp.md) |
| **WBC-AGILE** | Isaac Lab 기반 휴머노이드 전신 이동·조작 학습 | 대부분 Apache-2.0, RSL-RL 패치는 BSD-3-Clause | [저장소](https://github.com/nvidia-isaac/WBC-AGILE) | [상세 보기](docs/ko/wbc-agile.md) |
| **FoundationPose Inference Library** | 배포용 물체 자세 추정 라이브러리 | 코드 Apache-2.0; 모델 가중치 별도 | [저장소](https://github.com/nvidia-isaac/foundation-pose-inference-library) | [상세 보기](docs/ko/foundationpose-inference-library.md) |
| **Isaac Automator** | Isaac 시뮬레이션 워크플로 설치·배포 자동화 | Apache-2.0; 설치되는 구성 요소는 별도 약관 | [저장소](https://github.com/isaac-sim/IsaacAutomator) | [상세 보기](docs/ko/isaac-automator.md) |
| **Isaac ROS Object Detection** | ROS 2 물체 탐지 패키지 | Apache-2.0; 모델 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection) | [상세 보기](docs/ko/isaac-ros-object-detection.md) |
| **Isaac ROS Image Segmentation** | ROS 2 이미지 의미 분할 | Apache-2.0; 모델 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation) | [상세 보기](docs/ko/isaac-ros-image-segmentation.md) |
| **Isaac ROS Deploy** | 학습된 로봇 정책을 시뮬레이션 및 실제 하드웨어에 배포 | Apache-2.0; 런타임·모델 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_deploy) | [상세 보기](docs/ko/isaac-ros-deploy.md) |
| **Isaac ROS Teleop** | ROS 2 기반 XR 로봇 원격 조작 | Apache-2.0; 장치 소프트웨어 별도 | [저장소](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_teleop) | [상세 보기](docs/ko/isaac-ros-teleop.md) |
| **GR00T-VisualSim2Real** | 휴머노이드 시각 기반 이동·조작의 시뮬레이션-현실 전이 | Apache-2.0; 모델·로봇 자산 별도 | [저장소](https://github.com/NVlabs/GR00T-VisualSim2Real) | [상세 보기](docs/ko/gr00t-visualsim2real.md) |
| **GR00T-H 코드** | 의료·수술 로봇 정책 학습 및 추론 코드 | 코드 Apache-2.0; 의료 모델 가중치·데이터 별도 약관 | [저장소](https://github.com/NVIDIA-Medtech/GR00T-H) | [상세 보기](docs/ko/gr00t-h.md) |
| **Cosmos Reason2 코드** | 월드 추론 모델의 추론·학습 코드 | 코드 Apache-2.0; 모델 가중치 별도 약관 | [저장소](https://github.com/nvidia-cosmos/cosmos-reason2) | [상세 보기](docs/ko/cosmos-reason2.md) |
| **Cosmos Predict2 코드** | 월드·영상 생성 모델 코드 | 코드 Apache-2.0; 모델 가중치 별도 약관 | [저장소](https://github.com/nvidia-cosmos/cosmos-predict2) | [상세 보기](docs/ko/cosmos-predict2.md) |

### 데이터 생성·처리 및 실행

![Cosmos Data Factory의 예시 흐름. 시뮬레이션 장면이나 기존 영상을 정제·증강하고 라벨과 품질을 확인해 데이터셋으로 내보냅니다.](assets/section-diagrams/data-generation.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|
| **Cosmos Data Factory (CDF; 이전 Physical AI Data Factory)** | 영상·이미지 생성 및 처리 워크플로와 스킬 모음 | 코드 Apache-2.0, 문서·스킬 CC-BY-4.0; 사용 모델·서비스 별도 | [저장소](https://github.com/NVIDIA/cosmos-data-factory) | [상세 보기](docs/ko/cosmos-data-factory.md) |
| **CDF Auto Labeling (이전 paidf-auto-labeling)** | 영상·이미지 자동 주석 워크플로 | Apache-2.0; 모델·서비스 별도 | [저장소](https://github.com/NVIDIA/cdf-auto-labeling) | [상세 보기](docs/ko/cdf-auto-labeling.md) |
| **CDF Augmentation (이전 paidf-augmentation)** | 영상·이미지·텍스트 증강 워크플로 | Apache-2.0; 모델 별도 | [저장소](https://github.com/NVIDIA/cdf-augmentation) | [상세 보기](docs/ko/cdf-augmentation.md) |
| **CDF Simulation (이전 paidf-simulation)** | Isaac Sim·Replicator 기반 합성 데이터 생성 | Apache-2.0; 시뮬레이터 및 자산 별도 | [저장소](https://github.com/NVIDIA/cdf-simulation) | [상세 보기](docs/ko/cdf-simulation.md) |
| **Cosmos Curator** | 영상·이미지 분할, 필터링, 주석, 중복 제거 | Apache-2.0; 모델은 별도 | [저장소](https://github.com/NVIDIA/cosmos-curator) | [상세 보기](docs/ko/cosmos-curator.md) |
| **Cosmos Evaluator** | 생성 영상의 객체 일관성·물리적 개연성 등 평가 | Apache-2.0; 체커별 모델 조건 별도 | [저장소](https://github.com/NVIDIA/cosmos-evaluator) | [상세 보기](docs/ko/cosmos-evaluator.md) |
| **CDF Orchestration** | 데이터 팩토리 작업 실행·관리 구성 요소 | 코드 Apache-2.0; 실행 서비스와 의존성은 별도 조건 | [저장소](https://github.com/NVIDIA/cdf-orchestration) | [상세 보기](docs/ko/cdf-orchestration.md) |
| **OSMO** | GPU 자원을 사용하는 시뮬레이션·학습 워크플로 실행 관리 | Apache-2.0 | [저장소](https://github.com/NVIDIA/OSMO) | [상세 보기](docs/ko/osmo.md) |
| **TensorRT 공개 코드** | 추론 최적화 관련 샘플·플러그인·도구 | 저장소 Apache-2.0; TensorRT 바이너리 SDK 전체가 같은 라이선스라는 뜻은 아님 | [저장소](https://github.com/NVIDIA/TensorRT) | [상세 보기](docs/ko/tensorrt.md) |
| **Holoscan SDK** | 저지연 스트리밍·센서 AI 파이프라인 | Apache-2.0; 외부 구성 요소 별도 | [저장소](https://github.com/nvidia-holoscan/holoscan-sdk) | [상세 보기](docs/ko/holoscan-sdk.md) |

### NeMo와 물리 AI 도구

![NeMo의 데이터셋 준비·학습·평가 경로와, 앱에서 Switchyard를 거쳐 모델 엔드포인트로 보내는 선택적 요청 경로.](assets/section-diagrams/nemo-tooling.ko.svg)

NeMo 도구는 데이터 준비, 모델 후학습과 에이전트 운영에 쓰입니다. AlpaGym과 Curator에 연결되는 Cosmos RL과 Xenna도 이 표에서 함께 볼 수 있습니다. 상세 문서에서는 공식 연동 사례와 설명용 워크플로를 구분합니다.

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|
| **NeMo Switchyard** | LLM 에이전트와 애플리케이션의 모델 요청 라우팅 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Switchyard) | [상세 보기](docs/ko/nemo-switchyard.md) |
| **NeMo Curator** | 텍스트·이미지·영상·오디오 데이터셋 분산 정제 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Curator) | [상세 보기](docs/ko/nemo-curator.md) |
| **NeMo Data Designer** | 스키마와 시드 데이터를 이용한 합성 데이터 생성 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/DataDesigner) | [상세 보기](docs/ko/nemo-data-designer.md) |
| **NeMo AutoModel** | 지원 언어·멀티모달 모델의 PyTorch 기반 분산 학습 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Automodel) | [상세 보기](docs/ko/nemo-automodel.md) |
| **NeMo Megatron Bridge** | Megatron Core 학습 레시피와 Hugging Face 체크포인트 양방향 변환 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Megatron-Bridge) | [상세 보기](docs/ko/nemo-megatron-bridge.md) |
| **NeMo RL** | 지원 LLM·VLM의 분산 지도 미세조정과 강화학습 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/RL) | [상세 보기](docs/ko/nemo-rl.md) |
| **NeMo Gym** | 도구를 사용하는 에이전트의 롤아웃 환경과 검증기 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Gym) | [상세 보기](docs/ko/nemo-gym.md) |
| **NeMo Evaluator** | 모델 엔드포인트를 대상으로 재현 가능한 모델·에이전트 평가 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Evaluator) | [상세 보기](docs/ko/nemo-evaluator.md) |
| **NeMo Guardrails** | 모델 입력·검색 문맥·도구 실행·출력의 정책 검사 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/Guardrails) | [상세 보기](docs/ko/nemo-guardrails.md) |
| **NeMo Retriever Library** | 멀티모달 문서 추출·색인과 근거 검색 | Apache-2.0 | [저장소](https://github.com/NVIDIA/NeMo-Retriever) | [상세 보기](docs/ko/nemo-retriever.md) |
| **NeMo Agent Toolkit** | 에이전트 연결·프로파일링 도구와 공식 로봇 합성 데이터 사례 | Apache-2.0 (사용 중단 안내, 2026년 말 지원 종료 예정) | [저장소](https://github.com/NVIDIA/NeMo-Agent-Toolkit) | [상세 보기](docs/ko/nemo-agent-toolkit.md) |
| **NeMo Relay** | 에이전트 모델·도구 호출 추적, 미들웨어와 정책 관리 | Apache-2.0 | [저장소](https://github.com/NVIDIA/NeMo-Relay) | [상세 보기](docs/ko/nemo-relay.md) |
| **NeMo Fabric** | 지원 에이전트 하네스의 어댑터 기반 실행 | Apache-2.0 | [저장소](https://github.com/NVIDIA/NeMo-Fabric) | [상세 보기](docs/ko/nemo-fabric.md) |
| **NeMo Helix** | 에이전트 평가·최적화·보안 테스트를 위한 제어 계층 | Apache-2.0 | [저장소](https://github.com/NVIDIA-NeMo/nemo-helix) | [상세 보기](docs/ko/nemo-helix.md) |
| **NemoClaw** | 지원 에이전트를 실행하는 OpenShell 기반 참조 스택 | Apache-2.0 | [저장소](https://github.com/NVIDIA/NemoClaw) | [상세 보기](docs/ko/nemoclaw.md) |
| **NeMo Speech** | 음성 인식·합성 등 음성 모델 학습과 추론 | Apache-2.0 | [저장소](https://github.com/NVIDIA/NeMo) | [상세 보기](docs/ko/nemo-speech.md) |
| **Cosmos RL** | AlpaGym에서 사용하는 분산 강화학습 인프라 | Apache-2.0 (제한적 유지보수) | [저장소](https://github.com/nvidia-cosmos/cosmos-rl) | [상세 보기](docs/ko/cosmos-rl.md) |
| **Cosmos Xenna** | 데이터 정제 파이프라인에서 사용하는 Ray 기반 분산 단계 실행 | Apache-2.0 (제한적 유지보수) | [저장소](https://github.com/nvidia-cosmos/cosmos-xenna) | [상세 보기](docs/ko/cosmos-xenna.md) |

### 자율주행

![AlpaSim에서 관측과 행동을 반복해 차량 상태를 갱신합니다. 선택적 후학습 경로에서는 AlpaGym이 에피소드를 채점하고 Cosmos RL이 정책을 업데이트합니다.](assets/section-diagrams/autonomous-driving.ko.svg)

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 | 상세 설명 |
|---|---|---|---|---|
| **AlpaSim** | 자율주행 정책의 폐루프 시뮬레이션 | Apache-2.0 코드; 모델·데이터 별도 | [저장소](https://github.com/NVlabs/alpasim) | [상세 보기](docs/ko/alpasim.md) |
| **AlpaGym** | 자율주행 정책 강화학습 | Apache-2.0 코드; 의존성·모델 별도 | [저장소](https://github.com/NVlabs/alpagym) | [상세 보기](docs/ko/alpagym.md) |
| **NuRec SDK source** | 신경 장면 복원과 센서 렌더링용 GPU 라이브러리·앱·API | 저장소 Apache-2.0. 런타임 이미지·가중치·데이터는 별도 배포 | [저장소](https://github.com/NVIDIA/NuRec) · [라이선스](https://github.com/NVIDIA/NuRec/blob/main/LICENSE.md) | [상세 보기](docs/ko/nurec.md) |
| **NCore** | 센서 기록과 보정값·자세를 담는 공통 형식 및 변환용 Python 도구 | 코드 Apache-2.0. 주행 데이터셋과 변환 플러그인은 별도 조건 | [저장소](https://github.com/NVIDIA/ncore) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **Asset Harvester** | 주행 로그에서 NuRec 장면에 삽입할 Gaussian 객체 자산 추출 | 코드 Apache-2.0. 체크포인트 접근·이용 조건은 별도 | [저장소](https://github.com/NVIDIA/asset-harvester) · [모델 카드](https://huggingface.co/nvidia/asset-harvester) | [관련 가이드](docs/ko/nurec.md) |
| **NuRec Skills** | 복원 및 객체 자산 처리를 포함한 NuRec 작업용 에이전트 스킬 | 저장소 Apache-2.0. NuRec 실행 환경과 내려받는 자산은 별도 조건 | [저장소](https://github.com/NVIDIA/nurec-skills) | [관련 가이드](docs/ko/nurec.md) |
| **Alpamayo Recipes** | Alpamayo 모델 튜닝·양자화·배포 예제 | 코드 Apache-2.0. 모델과 데이터는 별도 조건 | [저장소](https://github.com/NVlabs/alpamayo-recipes) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **OmniDreams** | 자율주행 시뮬레이션용 자기회귀 영상 모델 코드와 선택형 AlpaSim 렌더러 경로 | 저장소 Apache-2.0. 가중치와 접근 조건은 별도 | [저장소](https://github.com/nv-tlabs/omni-dreams) · [모델 카드](https://huggingface.co/nvidia/omni-dreams-models) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |
| **FlashDreams** | 자기회귀 영상·월드 모델 추론 가속 및 서비스 연동 | 소스 대부분 Apache-2.0. 파일별 예외와 외부 모델 조건은 별도 확인 | [저장소](https://github.com/NVIDIA/flashdreams) | [관련 가이드](docs/ko/workflows/alpasim-closed-loop.md) |

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
| **Isaac GR00T / GR00T N1.7** | 로봇 행동 기반 모델·플랫폼 | 코드와 가중치의 라이선스 별도; 모델 이용 조건은 버전별 확인 | [공식 저장소](https://github.com/NVIDIA/Isaac-GR00T) | [상세 보기](docs/ko/groot-model.md) |
| **GR00T-Mimic / GR00T-Dreams** | 로봇 시연·합성 데이터 생성 기술·워크플로 | 독립 프로젝트 여부와 각 구현·모델의 조건은 개별 확인 필요 | [GR00T 공식 저장소](https://github.com/NVIDIA/Isaac-GR00T) | [상세 보기](docs/ko/groot-mimic-dreams.md) |
| **Isaac Manipulator** | 로봇팔 인식·파지·계획용 참조 워크플로 | Isaac ROS 패키지·모델 및 구성 요소마다 조건 상이 | [Isaac ROS 문서](https://nvidia-isaac-ros.github.io/) | [상세 보기](docs/ko/isaac-manipulator.md) |
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
| **Alpamayo** | 자율주행 추론·행동 모델 계열 | 공개 가중치의 조건과 접근 절차는 모델 버전별 상이 | [AlpaSim 모델 안내](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md) | [상세 보기](docs/ko/alpamayo.md) |
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
