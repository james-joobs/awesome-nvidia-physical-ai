<div align="center">

# Awesome NVIDIA Physical AI

**물리 AI를 위한 시뮬레이션, 데이터, 로봇 학습 생태계 안내서**

[![English](https://img.shields.io/badge/English-switch-555555?style=for-the-badge)](README.md) [![한국어](https://img.shields.io/badge/한국어-selected-76B900?style=for-the-badge)](README.ko.md)

[오픈소스 프로젝트](#1-오픈소스-코드가-확인된-프로젝트) · [플랫폼과 모델](#2-플랫폼모델제품표준-및-제한적-공개-항목) · [외부 도구](#3-대화에서-함께-언급된-외부-모델도구) · [연결 관계](#4-연결-관계와-명칭-정리)

</div>

---

확인일: 2026-11-09. 범위는 연결된 대화의 사용자 질문과 두 답변에서 이름이 나온 항목이다. NVIDIA 외부 프로젝트도 실제 언급된 경우 포함했다. 공식 저장소와 문서를 기준으로 했으며, 링크에 접속할 수 있다는 사실은 모든 코드·모델·데이터가 같은 조건으로 이용 가능하다는 의미가 아니다.

**분류 기준:** 아래 첫 표는 공개 코드에 대해 오픈소스 라이선스가 확인된 프로젝트다. 코드의 라이선스는 모델 가중치, 데이터, 바이너리, 클라우드 서비스 및 의존성에 자동으로 적용되지 않는다. 표의 라이선스는 지정한 저장소의 기본적인 코드 조건이며, 개별 파일과 버전은 직접 확인해야 한다. 두 번째 표는 플랫폼·모델·제품·표준, 제한적 공개 코드, 또는 라이선스가 불명확한 항목이다. NVIDIA 고유 모델도 소스가 공개되었다는 이유만으로 오픈소스로 분류하지 않았다.

## 1. 오픈소스 코드가 확인된 프로젝트

### 물리, 3D 및 시뮬레이션

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 |
|---|---|---|---|
| Newton | Warp 기반 GPU 물리 엔진과 로봇 시뮬레이션 솔버 | Apache-2.0 | [저장소](https://github.com/newton-physics/newton) |
| NVIDIA Warp | GPU 가속 물리·기하 계산용 Python 프레임워크 | Apache-2.0 | [저장소](https://github.com/NVIDIA/warp) |
| NVIDIA PhysX | 강체·충돌 등 물리 시뮬레이션 엔진 | BSD-3-Clause; 일부 추가 구성 요소는 별도 조건 확인 | [저장소](https://github.com/NVIDIA-Omniverse/PhysX) |
| MuJoCo Warp (MJWarp) | MuJoCo 물리 계산의 Warp 기반 가속 구현 | Apache-2.0; Google DeepMind 프로젝트 | [저장소](https://github.com/google-deepmind/mujoco_warp) |
| OpenUSD | 3D 장면과 자산 교환·구성을 위한 프레임워크 | 수정 BSD 계열; 표준 및 상표와 구현은 구분 | [저장소](https://github.com/PixarAnimationStudios/OpenUSD) |
| Isaac Sim | 로봇·센서·환경 시뮬레이션 참조 애플리케이션 | 저장소 코드 Apache-2.0; 전체 배포물·의존성은 별도 NVIDIA 약관이 적용될 수 있음 | [저장소](https://github.com/isaac-sim/IsaacSim) |
| PhysicsNeMo | 물리 기반 AI 및 대리 모델 학습 프레임워크 | Apache-2.0 | [저장소](https://github.com/NVIDIA/physicsnemo) |

### 로봇 학습, 수집 및 제어

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 |
|---|---|---|---|
| Isaac Lab | 강화·모방학습 및 로봇 학습 환경 | BSD-3-Clause; 선택한 백엔드와 의존성은 별도 조건 | [저장소](https://github.com/isaac-sim/IsaacLab) |
| Isaac Lab-Arena | 조합 가능한 로봇 작업 환경과 정책 평가 | Apache-2.0; Isaac Sim 등 의존성 별도 | [저장소](https://github.com/isaac-sim/IsaacLab-Arena) |
| Isaac Capture (이전 Isaac Teleop 포함) | 원격 조작 및 1인칭 데이터 수집·기록·리타기팅 | 기본 Apache-2.0; EgoPost는 OpenMDW-1.1, CloudXR과 일부 선택 패키지는 별도 독점 조건 | [저장소](https://github.com/NVIDIA/IsaacCapture) |
| AutoData | 소수의 시연을 다양한 작업 조건의 궤적으로 확장 | Apache-2.0; Isaac Sim 및 특정 cuRobo 구성 요소 별도 조건 | [저장소](https://github.com/isaac-sim/AutoData) |
| Video-to-Data (V2D) | 영상의 장면·동작을 복원하고 로봇 학습에 연결하는 파이프라인 | 소스 Apache-2.0, 문서·스킬 CC-BY-4.0; 의존 모델 별도 | [저장소](https://github.com/nvidia-isaac/video_to_data) |
| Isaac GR00T 코드 | GR00T 로봇 정책의 학습·추론·배포 코드 | 코드 Apache-2.0; 모델과 가중치는 별도 조건 | [저장소](https://github.com/NVIDIA/Isaac-GR00T) |
| cuRobo | GPU 기반 로봇 역기구학·동작계획 | 저장소 Apache-2.0; AutoData 배포의 특정 구성 요소는 별도 약관 확인 | [저장소](https://github.com/NVlabs/curobo) |
| LeRobot | 로봇 데이터셋과 모델 학습 도구; Capture와 연동 가능 | Apache-2.0; Hugging Face 프로젝트 | [저장소](https://github.com/huggingface/lerobot) |
| Isaac ROS | ROS 2 기반 GPU 가속 로봇 패키지 모음 | 패키지별 조건 상이; 공통 저장소와 배포물의 개별 라이선스 확인 | [공식 문서](https://nvidia-isaac-ros.github.io/) · [공통 코드](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common) |

### 데이터 생성·처리 및 실행

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 |
|---|---|---|---|
| Cosmos Data Factory (CDF; 이전 Physical AI Data Factory) | 영상·이미지 생성 및 처리 워크플로와 스킬 모음 | 코드 Apache-2.0, 문서·스킬 CC-BY-4.0; 사용 모델·서비스 별도 | [저장소](https://github.com/NVIDIA/cosmos-data-factory) |
| CDF Auto Labeling (이전 paidf-auto-labeling) | 영상·이미지 자동 주석 워크플로 | Apache-2.0; 모델·서비스 별도 | [저장소](https://github.com/NVIDIA/cdf-auto-labeling) |
| CDF Augmentation (이전 paidf-augmentation) | 영상·이미지·텍스트 증강 워크플로 | Apache-2.0; 모델 별도 | [저장소](https://github.com/NVIDIA/cdf-augmentation) |
| CDF Simulation (이전 paidf-simulation) | Isaac Sim·Replicator 기반 합성 데이터 생성 | Apache-2.0; 시뮬레이터 및 자산 별도 | [저장소](https://github.com/NVIDIA/cdf-simulation) |
| Cosmos Curator | 영상·이미지 분할, 필터링, 주석, 중복 제거 | Apache-2.0; 모델은 별도 | [저장소](https://github.com/NVIDIA/cosmos-curator) |
| Cosmos Evaluator | 생성 영상의 객체 일관성·물리적 개연성 등 평가 | Apache-2.0; 체커별 모델 조건 별도 | [저장소](https://github.com/NVIDIA/cosmos-evaluator) |
| OSMO | GPU 자원을 사용하는 시뮬레이션·학습 워크플로 실행 관리 | Apache-2.0 | [저장소](https://github.com/NVIDIA/OSMO) |
| TensorRT 공개 코드 | 추론 최적화 관련 샘플·플러그인·도구 | 저장소 Apache-2.0; TensorRT 바이너리 SDK 전체가 같은 라이선스라는 뜻은 아님 | [저장소](https://github.com/NVIDIA/TensorRT) |
| Holoscan SDK | 저지연 스트리밍·센서 AI 파이프라인 | Apache-2.0; 외부 구성 요소 별도 | [저장소](https://github.com/nvidia-holoscan/holoscan-sdk) |

### 자율주행

| 이름 | 역할 | 공개 코드 라이선스 및 유의점 | 공식 소스 |
|---|---|---|---|
| AlpaSim | 자율주행 정책의 폐루프 시뮬레이션 | Apache-2.0 코드; 모델·데이터 별도 | [저장소](https://github.com/NVlabs/alpasim) |
| AlpaGym | 자율주행 정책 강화학습 | Apache-2.0 코드; 의존성·모델 별도 | [저장소](https://github.com/NVlabs/alpagym) |

## 2. 플랫폼·모델·제품·표준 및 제한적 공개 항목

이 표의 ‘공개’는 접근 가능성만 뜻하며, 오픈소스 라이선스 또는 상업적 이용 허가를 뜻하지 않는다. 확인하지 못한 조건은 미확인으로 표시한다.

| 이름 | 역할·분류 | 공개·라이선스 상태 | 공식 출처 |
|---|---|---|---|
| NVIDIA Omniverse | OpenUSD 기반 3D 개발 플랫폼 | 제품·SDK와 공개 구성 요소의 조건이 각각 다름 | [공식 페이지](https://developer.nvidia.com/omniverse) |
| SimReady | 시뮬레이션에 필요한 속성을 갖춘 3D 자산의 규격·지침 | 자산별 라이선스 별도; 단일 소프트웨어 프로젝트 아님 | [공식 문서](https://docs.omniverse.nvidia.com/simready/latest/index.html) |
| NuRec | 실제 환경의 신경 재구성·렌더링 기술 | 제품·기술; 전체 소스 및 라이선스 범위 미확인 | [공식 안내](https://developer.nvidia.com/omniverse/nurec) |
| Cosmos 및 Cosmos 3 | 월드 모델·도구 플랫폼 및 모델 계열 | [Cosmos 저장소](https://github.com/NVIDIA/cosmos)는 코드와 모델에 OpenMDW-1.1을 명시; OSI 승인 오픈소스라고 단정하지 않음. 개별 저장소는 별도 조건 | [공식 저장소](https://github.com/NVIDIA/cosmos) |
| Cosmos Predict / Transfer / Reason | 각각 세계·영상 생성, 시각 조건 변환, 장면 추론 모델 계열 | 모델 버전과 가중치별 약관 확인; 전체를 일괄 오픈소스로 취급하지 않음 | [Cosmos 공식 저장소](https://github.com/NVIDIA/cosmos) |
| Cosmos Embed / Dataset Search | 멀티모달 임베딩 모델·서비스 및 영상 검색 마이크로서비스 | 서비스·모델의 전체 소스 및 라이선스 미확인 | [공식 문서](https://docs.nvidia.com/cosmos/cds/latest/introduction.html) |
| Isaac GR00T / GR00T N1.7 | 로봇 행동 기반 모델·플랫폼 | 코드와 가중치의 라이선스 별도; 모델 이용 조건은 버전별 확인 | [공식 저장소](https://github.com/NVIDIA/Isaac-GR00T) |
| GR00T-Mimic / GR00T-Dreams | 로봇 시연·합성 데이터 생성 기술·워크플로 | 독립 프로젝트 여부와 각 구현·모델의 조건은 개별 확인 필요 | [GR00T 공식 저장소](https://github.com/NVIDIA/Isaac-GR00T) |
| Isaac Manipulator | 로봇팔 인식·파지·계획용 참조 워크플로 | Isaac ROS 패키지·모델 및 구성 요소마다 조건 상이 | [Isaac ROS 문서](https://nvidia-isaac-ros.github.io/) |
| Isaac RLPT | 사전학습 정책을 강화학습으로 개선하는 워크플로 | 독립 저장소와 라이선스 미확인 | [Isaac Lab](https://github.com/isaac-sim/IsaacLab) |
| Replicator | Omniverse/Isaac Sim의 합성 데이터 생성 도구 | 제품 구성 요소; 전체 코드 공개 및 독립 라이선스 미확인 | [Isaac Sim 문서](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/index.html) |
| EgoHand / EgoPost | Capture의 1인칭 손·카메라 동작 관련 구성 요소 | EgoPost는 OpenMDW-1.1; EgoHand의 독립 라이선스 미확인. 상위 패키지 기본 라이선스를 일괄 적용하지 않음 | [Isaac Capture](https://github.com/NVIDIA/IsaacCapture) |
| MimicGen | 시연으로 다양한 로봇 행동 데이터 생성 | 소스 공개; NVIDIA Source Code License 조건을 확인해야 하며 오픈소스로 단정하지 않음 | [저장소](https://github.com/NVlabs/mimicgen) |
| DexMimicGen | 양손·다중 조작 시연 데이터 생성 연구 | 코드 NVIDIA Source Code License; 데이터 CC-BY-4.0, 코드 이용 제한 확인 | [저장소](https://github.com/NVlabs/dexmimicgen) |
| SkillGen / SkillMimicGen | 동작계획으로 시연 구간을 연결·생성하는 방법 | Isaac Lab 구현과 cuRobo 등 의존성의 조건을 각각 확인; 논문명과 구현명은 구분 | [Isaac Lab 구현 문서](https://github.com/isaac-sim/IsaacLab/blob/main/docs/source/features/imitation-learning/skillgen.rst) |
| Isaac Lab Eureka | 언어 모델을 이용한 보상 함수 생성 연구 코드 | 공개 저장소; 적용 라이선스 미확인 | [저장소](https://github.com/NVlabs/IsaacLabEureka) |
| FoundationPose | 물체 6D 자세 추정·추적 연구 코드·모델 | 연구 저장소 코드는 비상업적 사용 제한; 별도 배포 모델은 별도 조건 | [코드](https://github.com/NVlabs/FoundationPose) · [모델 카드](https://huggingface.co/nvidia/foundationpose) |
| FoundationStereo | 스테레오 깊이 추정 연구 코드·모델 | 연구 코드 비상업적 제한; 별도 상업용 모델 제공 여부와 조건은 해당 배포물 확인 | [저장소](https://github.com/NVlabs/FoundationStereo) |
| nvblox | 3D 공간 매핑·장애물 표현 라이브러리 | 코드 공개; 저장소의 혼합 라이선스 범위 미확인 | [저장소](https://github.com/nvidia-isaac/nvblox) |
| AnomalyGen | 소수 예시를 이용한 결함 이미지 생성 워크플로 | 공개 저장소; 코드·모델·어댑터 각각의 조건 미확인 | [저장소](https://github.com/NVIDIA/cdf-anomalygen) |
| CDF Orchestration | 데이터 팩토리 작업 실행·관리 구성 요소 | 공개 저장소; 라이선스 및 실행 서비스별 조건 미확인 | [저장소](https://github.com/NVIDIA/cdf-orchestration) |
| Alpamayo | 자율주행 추론·행동 모델 계열 | 공개 가중치의 조건과 접근 절차는 모델 버전별 상이 | [AlpaSim 모델 안내](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md) |
| Metropolis / VSS | 영상 AI 플랫폼 / 영상 검색·요약 워크플로 | 플랫폼·서비스; 개별 SDK·모델의 조건 별도 | [Metropolis](https://developer.nvidia.com/metropolis) |
| DeepStream | 실시간 영상 분석 SDK | 제품 SDK; 공개 샘플과 바이너리의 조건 별도 | [공식 페이지](https://developer.nvidia.com/deepstream-sdk) |
| TAO Toolkit | 비전 AI 모델 학습·파인튜닝 도구 | 제품·SDK; 모델과 구성 요소별 조건 확인 | [공식 페이지](https://developer.nvidia.com/tao-toolkit) |
| Jetson / JetPack | 엣지 AI 하드웨어 / 소프트웨어 개발 키트 | 제품·배포판; 개별 구성 요소의 조건 상이 | [Jetson](https://developer.nvidia.com/embedded/jetson-modules) · [JetPack](https://developer.nvidia.com/embedded/jetpack) |
| NVIDIA DRIVE | 자율주행 하드웨어·소프트웨어 플랫폼 | 제품·플랫폼; 구성 요소별 이용 조건 확인 | [공식 페이지](https://developer.nvidia.com/drive) |
| RTX / DGX Spark | GPU 기술·제품군 / AI 컴퓨터 | 하드웨어·제품; 오픈소스 프로젝트 아님 | [RTX](https://www.nvidia.com/en-us/geforce/graphics-cards/) · [DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) |

## 3. 대화에서 함께 언급된 외부 모델·도구

이들은 V2D 등의 구성이나 의존 기술로 언급되었으며 NVIDIA 프로젝트라는 뜻은 아니다. 공개 코드와 체크포인트의 조건은 각각 다르다.

| 이름 | 역할 | 상태 및 공식 출처 |
|---|---|---|
| LangGraph | 에이전트 워크플로 구성 | [공식 저장소](https://github.com/langchain-ai/langgraph); 라이선스·버전 확인 |
| SigLIP 2 | 영상·텍스트 표현 모델 | [공식 모델 카드](https://huggingface.co/google/siglip2-base-patch16-224); 모델별 조건 확인 |
| Grounding DINO | 텍스트 조건 객체 탐지 | [공식 저장소](https://github.com/IDEA-Research/GroundingDINO); 가중치 별도 |
| SAM 2 / SAM 3D | 영상·이미지 분할 / 3D 복원 계열 | [SAM 2](https://github.com/facebookresearch/sam2) · [SAM 3D Objects](https://github.com/facebookresearch/sam-3d-objects); 모델별 약관 확인 |
| MoGe | 단일 이미지 기반 3D 기하 추정 | [공식 저장소](https://github.com/microsoft/MoGe); 코드·가중치 조건 확인 |
| SMPL | 인체 형상·자세 파라미터 모델 계열 | [공식 프로젝트](https://smpl.is.tue.mpg.de/); 모델 데이터 별도 이용 조건 |
| PyTorch | 기계학습 프레임워크 | [공식 저장소](https://github.com/pytorch/pytorch); BSD 계열, 의존성 별도 |
| ROS 2 | 로봇 소프트웨어 미들웨어 | [공식 문서](https://docs.ros.org/en/rolling/); 패키지별 라이선스 별도 |
| CUDA / TensorRT / ONNX | GPU 컴퓨팅 플랫폼 / 추론 SDK / 모델 교환 형식 | CUDA와 TensorRT 배포물은 별도 제품 약관, [ONNX](https://github.com/onnx/onnx)는 공개 구현·표준. TensorRT 공개 코드는 위 표 참조 |
| MCAP / HDF5 / URDF / CAD | 기록 포맷 / 데이터 포맷 / 로봇 기술 형식 / 설계 일반 개념 | 형식·개념과 이를 구현하는 코드의 라이선스는 별개. [MCAP](https://mcap.dev/) · [HDF5](https://www.hdfgroup.org/solutions/hdf5/) · [URDF](https://docs.ros.org/en/rolling/Tutorials/Intermediate/URDF/URDF-Main.html) |

## 4. 연결 관계와 명칭 정리

- **수집:** Isaac Capture의 원격 조작과 1인칭 데이터, 또는 V2D의 영상 복원 결과를 로봇 학습 데이터로 가공할 수 있다. 실제 데이터 형식과 리타기팅 호환성은 작업별로 확인한다.
- **합성·증강:** AutoData는 주로 로봇 행동 궤적을 확장한다. CDF, Cosmos 및 Replicator는 영상·이미지 등 시각 데이터 생산과 처리에 활용된다. 서로 자동으로 연결된 단일 파이프라인은 아니다.
- **시뮬레이션·학습:** Warp 위의 Newton 또는 다른 물리 백엔드를 Isaac Lab에서 선택할 수 있다. Isaac Sim은 센서·렌더링·로봇 환경을 제공하며, 일부 Lab 워크플로는 Isaac Sim 없이도 실행된다. [Lab 릴리스 설명](https://github.com/isaac-sim/IsaacLab/releases).
- **모델·평가·배포:** GR00T 등의 정책을 데이터로 학습하고 Lab-Arena나 시뮬레이터에서 평가한 뒤, Isaac ROS·TensorRT·Jetson 등과 결합할 수 있다. OSMO와 CDF Orchestration은 해당 작업의 실행 관리를 맡는다.
- **통합한 이름:** 질문의 `issac`, `lssac`은 **Isaac**으로 정정했다. Isaac Teleop은 현재 Isaac Capture에 포함된 이전 명칭으로 통합했다. Physical AI Data Factory 저장소는 Cosmos Data Factory로 연결되며, `paidf-*`의 위 세 저장소도 현재 `cdf-*`로 연결된다. GR00T의 숫자는 영문 O가 아니라 숫자 0이다.
- **별도 워크플로 이름:** Video Data Augmentation, Event Video Generation, Defect Image Generation, Image Attribute Augmentation, Autonomous Vehicle Dataset Generation은 CDF의 워크플로이며 독립 저장소로 임의 분류하지 않았다. Ego Pipeline, Video Ingestion Agent, Reconstruction, Robotic Grounding 및 recording/replay 등은 기능·단계다.

## 검증 방법과 한계

대화 원문을 다시 읽어 이름을 수집하고 중복 표기를 통합했다. 공식 GitHub 저장소는 GitHub의 저장소 응답과 README·LICENSE 정보를 확인했으며, 저장소가 리디렉션되는 경우 현재 주소를 사용했다. 공식 문서·제품 링크도 접근 여부를 확인했다. 접속 상태는 변할 수 있고 일부 사이트는 지역·로그인·자동 접근 제한으로 확인이 어려울 수 있다. 저장소의 공개 여부, 특정 버전의 라이선스, 가중치 이용 조건 및 제3자 의존성은 각각 별개이므로 도입 전에 대상 버전의 LICENSE와 모델 카드를 재확인해야 한다. 이전 대화에 있던 구체적인 GPU 호환성이나 모델 버전 주장은 이 목록의 라이선스 검증으로 보증되지 않는다.
