# AlpaSim으로 자율주행 정책을 폐루프 평가하기

[English](../../en/workflows/alpasim-closed-loop.md) · **한국어** · [목표별 카탈로그](../../../README.ko.md#만들고-싶은-것부터-시작하세요)

AlpaSim 공식 예제로 자율주행 정책을 한 번 실행해 봅니다. 폐루프에서는 정책이 정한 궤적을 따라 차량이 움직이고, 그 위치에서 카메라의 다음 프레임을 렌더링합니다. 먼저 제공되는 NuRec USDZ 장면에서 충돌과 도로 이탈을 확인한 뒤, 직접 수집한 로그로 장면을 만드는 방법을 살펴봅니다. [AlpaSim 아키텍처](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/DESIGN.md)

## 한 프레임이 어떻게 다음 주행 결정을 바꿀까요?

### 폐루프에서는 카메라에 보이는 다음 장면이 달라집니다

렌더러는 NuRec 장면과 현재 자차 위치·방향으로 카메라 영상을 만듭니다. 정책은 관측값을 보고 앞으로 갈 **시간 순서의 궤적**을 제안합니다. AlpaSim이 자차 상태를 갱신하면 다음 영상에서 차선 위치나 다른 차량과의 거리가 달라질 수 있습니다. 그 영상이 다시 정책에 들어갑니다. [지정 AlpaSim 리비전의 설계 문서](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/DESIGN.md)

```text
재구성된 장면 + 현재 자차 상태 → 카메라 관측 → 정책의 궤적
               ↑                                  ↓
               └────────── 갱신한 자차 상태 ─────────┘
```

### 어떤 파일을 보고 정책을 비교할까요?

| 파일 | 의미 |
| --- | --- |
| 장면 `.usdz` | 선택한 NuRec 장면의 입력입니다. 비교할 때 같은 장면 ID와 렌더러를 사용합니다. |
| 에피소드의 `metrics.parquet` | 표 형태의 평가 데이터입니다. 지표 정의와 시뮬레이션 완료 여부를 확인합니다. |
| `aggregate/metrics_results.txt` | 여러 에피소드의 평가를 집계한 결과입니다. |

예를 들어 두 정책의 충돌 지표를 비교하려면 장면과 렌더러, 평가 설정을 고정하고 정책만 바꿉니다. 표는 **공식 예제의 출력 위치**를 설명합니다. [지정 리비전의 공식 실행 예제](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/TUTORIAL.md)

## 준비물

| 항목 | 시작 기준 |
| --- | --- |
| 실행 환경 | NVIDIA GPU가 있는 Linux 호스트. 지정 리비전의 설치 문서에 따라 CUDA 12.8, NVIDIA 드라이버와 Container Toolkit, Docker Compose/Buildx, Rust, `uv` 0.9.17 이상을 준비합니다. 컨테이너가 GPU를 인식하는지 확인합니다. |
| AlpaSim | 소스 리비전 `affc2ea`, 로컬 Docker Compose, `topology=1gpu`, 튜토리얼의 VaVAM 기준 정책, 기본 NuRec 렌더러. |
| 장면 접근 권한 | Hugging Face의 NVIDIA NuRec 데이터셋에 접근 권한을 요청하고, 읽기 토큰을 셸의 `HF_TOKEN`으로 설정합니다. 공유하는 명령이나 산출물에 토큰을 포함하지 않습니다. |
| 장면 | 공식 예제의 `clipgt-02eadd92-02f1-46d8-86fe-a9e338fed0b6`에서 시작합니다. 지정 리비전의 장면 목록은 이 장면을 26.01 샘플 릴리스에 연결합니다. |

[공식 설치 안내](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/ONBOARDING.md) · [NuRec 데이터셋과 이용 조건](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec) · [장면 목록](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/data/scenes/README.md)

## 1. 공식 장면 하나 실행하기

### 1. GPU 머신에서 예제 폴더 준비하기

[GPU 환경 점검](../onboarding/nvidia-linux.md)을 마친 Linux 머신의 터미널을 엽니다. NuRec 접근이 승인됐다면 이 터미널에 읽기 토큰을 `HF_TOKEN`으로 설정합니다. 아래 명령으로 공식 코드의 같은 버전을 받아 그 폴더로 이동합니다.

```bash
git clone https://github.com/NVlabs/alpasim.git
cd alpasim
git checkout affc2eab209fa43bdfa2f26c0f8d437922d78a68
```

### 2. 실행 환경과 기준 정책 받기

같은 터미널에서 아래 두 줄을 실행합니다. 첫 줄은 현재 셸에 실행 환경을 준비합니다. 두 번째 줄은 예제 차량의 기준 정책인 VaVAM 파일을 내려받습니다.

```bash
source setup_local_env.sh
bash data/download_vavam_assets.sh --model vavam-b
```

### 3. 장면 하나만 주행하기

준비가 끝나면 아래 블록을 한 번에 붙여 넣습니다. `topology=1gpu`는 GPU 한 대를 쓰고, `scenes.scene_ids`는 실행할 장면을 고릅니다. `wizard.log_dir`는 주행 결과가 생길 폴더입니다.

```bash
uv run alpasim_wizard deploy=local topology=1gpu driver=vavam \
  'scenes.scene_ids=[clipgt-02eadd92-02f1-46d8-86fe-a9e338fed0b6]' \
  "wizard.log_dir=$PWD/run-baseline"
```

첫 실행에서는 컨테이너 이미지와 모델을 내려받을 수 있습니다. `GatedRepoError`가 나오면 장면 접근 승인과 토큰 권한을 확인합니다. 기존 설치를 재사용한다면 장면 목록의 26.01·26.04 캐시 갱신 안내도 확인합니다. [공식 Docker 튜토리얼](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/TUTORIAL.md) · [장면 캐시 안내](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/data/scenes/README.md)

## 2. 실행 결과와 비교 기준 확인하기

| 확인할 것 | 확인 위치 |
| --- | --- |
| 에피소드가 끝났나요? | `run-baseline/rollouts/`의 해당 에피소드에서 `_complete`와 `metrics.parquet`를 찾습니다. 완료되지 않았다면 서비스 로그를 확인합니다. |
| 자차는 무엇을 보고 어떻게 움직였나요? | 평가 영상이 켜져 있다면 `run-baseline/eval/videos/` 또는 집계 영상 폴더에서 영상을 엽니다. 문제 장면은 같은 에피소드의 주행 로그와 대조합니다. |
| 어떤 지표부터 비교하나요? | `run-baseline/aggregate/metrics_results.txt`에서 자차 과실 충돌과 도로 이탈부터 봅니다. 한 번의 성공으로 설치와 기준 실행을 확인하고, 정책 성능을 판단할 때는 장면을 늘립니다. |

정책을 비교할 때는 새 출력 폴더를 사용하고 장면 파일의 UUID, 렌더러·카메라, 차량·교통, 평가 설정을 고정합니다. 최종 적용된 실행 설정을 저장한 뒤 같은 카메라 구성에서 동작하는 다른 정책으로 바꿉니다. 같은 장면 ID가 여러 장면 파일을 가리킬 수 있으므로, 선택된 UUID와 Hugging Face 리비전도 결과에 함께 기록합니다. [AlpaSim 결과 구조](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/TUTORIAL.md#results-structure) · [공식 평가 지표](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/OPERATIONS.md#understanding-driving-quality-metrics)

## 3. 자체 주행 로그로 확장하기

1. 시간 동기화된 카메라 프레임, 카메라 보정값, 자차 자세가 있는 짧은 구간을 준비합니다. 구간을 NCore로 변환하고 공식 NuRec 입력 요건을 확인합니다. 지도와 이동 객체 추적 정보의 필요 여부는 장면과 사용할 기능에 따라 달라집니다.
2. 복원 결과를 호환되는 USDZ로 패키징하고 NuRec 렌더러로 확인합니다. 원래 카메라 시점부터 다시 렌더링합니다. 새 시점을 보기 전에 차선 경계, 이동 객체의 타이밍, 가림 때문에 생긴 빈 영역을 점검합니다.
3. 경로·지도·시뮬레이션 메타데이터를 갖춘 AlpaSim 시나리오를 준비합니다. 공식 장면 규격과 렌더러 버전에 맞는지 확인하고 같은 평가를 실행합니다. 문제가 생기면 먼저 완료한 공식 샘플과 비교해 어느 단계에서 달라졌는지 확인합니다.

[NCore로 데이터 준비하기](https://docs.nvidia.com/nurec/basics/get-data.html) · [주행 장면 복원하기](https://docs.nvidia.com/nurec/nurec/reconstruct-av-scene.html) · [NuRec 복원 확장과 장면 레이어](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html) · [데이터셋 장면 형식](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec#dataset-format)

## 관련 도구와 검증 범위

- **후학습** · [AlpaGym](../alpagym.md)은 지원되는 AlpaSim 워크플로에 강화학습을 연결합니다. [Alpamayo Recipes](https://github.com/NVlabs/alpamayo-recipes)는 모델 후학습과 배포 예제를 제공합니다.
- **다른 렌더러** · [FlashDreams를 통한 OmniDreams](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/VIDEO_MODEL.md)는 별도 렌더러 구성입니다. 지원 장면·카메라·체크포인트·GPU 조건을 확인합니다.
- **라이선스** · AlpaSim 코드는 Apache-2.0입니다. VaVAM 자산, 접근 제한이 있는 NuRec 데이터·아티팩트, 컨테이너 구성 요소에는 별도 조건이 적용됩니다. [AlpaSim 라이선스](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/LICENSE) · [NuRec 데이터셋 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec)
- **검증 상태** · 지정 리비전의 공식 튜토리얼, 장면 항목, 출력 경로를 대조했습니다. 준비된 NuRec 장면을 사용한 GPU 폐루프 실행은 2026년 11월 15일 AlpaSim `96a33bc`에서 완료했습니다. 이 문서가 안내하는 고정 리비전 `affc2ea`와는 구분합니다. 실행 완료만으로 정책의 주행 성능을 판단할 수는 없습니다. 데이터셋에서 파생된 영상과 지표는 해당 데이터의 접근·공개 조건에 따라 로컬에 보관합니다. 직접 수집한 주행 로그의 장면 복원은 아직 검증하지 않았습니다.
