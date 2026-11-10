# AlpaSim으로 자율주행 정책을 폐루프 평가하기

[English](../../en/workflows/alpasim-closed-loop.md) · **한국어** · [목표별 카탈로그](../../../README.ko.md#만들고-싶은-것부터-시작하세요)

공식 AlpaSim 예제로 복원된 주행 장면 하나를 실행하고 결과를 살펴봅니다. 폐루프에서는 정책이 낸 궤적에 따라 시뮬레이션 속 자차 상태가 바뀌고, 그 상태에서 다음 관측을 렌더링합니다. 녹화 영상 재생은 기록된 시점을 그대로 사용합니다. 먼저 준비된 NuRec USDZ로 시뮬레이터를 확인한 뒤 자체 로그 복원으로 확장합니다. [AlpaSim 아키텍처](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/DESIGN.md)

## 준비물

| 항목 | 시작 기준 |
| --- | --- |
| 실행 환경 | NVIDIA GPU가 있는 Linux 호스트. 지정 리비전의 설치 문서에 따라 CUDA 12.8, NVIDIA 드라이버와 Container Toolkit, Docker Compose/Buildx, Rust, `uv` 0.9.17 이상을 준비합니다. 컨테이너가 GPU를 인식하는지 확인합니다. |
| AlpaSim | 소스 리비전 `affc2ea`, 로컬 Docker Compose, `topology=1gpu`, 튜토리얼의 VaVAM 기준 정책, 기본 NuRec 렌더러. |
| 장면 접근 권한 | Hugging Face의 NVIDIA NuRec 데이터셋에 접근 권한을 요청하고, 읽기 토큰을 셸의 `HF_TOKEN`으로 설정합니다. 공유하는 명령이나 산출물에 토큰을 포함하지 않습니다. |
| 장면 | 공식 예제의 `clipgt-02eadd92-02f1-46d8-86fe-a9e338fed0b6`에서 시작합니다. 지정 리비전의 장면 목록은 이 장면을 26.01 샘플 릴리스에 연결합니다. |

[공식 설치 안내](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/ONBOARDING.md) · [NuRec 데이터셋과 이용 조건](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec) · [장면 목록](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/data/scenes/README.md)

## 1. 공식 장면 하나 실행하기

호스트를 준비하고 `HF_TOKEN`을 설정한 뒤, 공식 튜토리얼의 지정 리비전을 새로 받습니다. 초기 설정 스크립트는 추가 도구 설치를 요청할 수 있습니다. 다운로드 명령은 VaVAM 자산을 받고, 실행 도구는 필요할 때 장면을 내려받습니다.

```bash
git clone https://github.com/NVlabs/alpasim.git
cd alpasim
git checkout affc2eab209fa43bdfa2f26c0f8d437922d78a68
source setup_local_env.sh
bash data/download_vavam_assets.sh --model vavam-b
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

정책을 비교할 때는 새 출력 폴더를 사용하고 장면 아티팩트 UUID, 렌더러·카메라, 차량·교통, 평가 설정을 고정합니다. 최종 적용된 실행 설정을 저장한 뒤 같은 카메라 구성에서 동작하는 다른 정책으로 바꿉니다. 같은 장면 ID가 여러 아티팩트를 가리킬 수 있으므로, 선택된 UUID와 Hugging Face 리비전도 결과에 함께 기록합니다. [AlpaSim 결과 구조](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/TUTORIAL.md#results-structure) · [공식 평가 지표](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/OPERATIONS.md#understanding-driving-quality-metrics)

## 3. 자체 주행 로그로 확장하기

1. 시간 동기화된 카메라 프레임, 카메라 보정값, 자차 자세가 있는 짧은 구간을 준비합니다. 구간을 NCore로 변환하고 공식 NuRec 입력 요건을 확인합니다. 지도와 이동 객체 추적 정보의 필요 여부는 장면과 사용할 기능에 따라 달라집니다.
2. 복원 결과를 호환되는 USDZ로 패키징하고 NuRec 렌더러로 확인합니다. 원래 카메라 시점부터 다시 렌더링합니다. 새 시점을 보기 전에 차선 경계, 이동 객체의 타이밍, 가림 때문에 생긴 빈 영역을 점검합니다.
3. 경로·지도·시뮬레이션 메타데이터를 갖춘 AlpaSim 시나리오를 준비합니다. 공식 장면 규격과 렌더러 버전에 맞는지 확인하고 같은 평가를 실행합니다. 문제가 생기면 먼저 완료한 공식 샘플과 비교해 어느 단계에서 달라졌는지 확인합니다.

[NCore로 데이터 준비하기](https://docs.nvidia.com/nurec/basics/get-data.html) · [주행 장면 복원하기](https://docs.nvidia.com/nurec/nurec/reconstruct-av-scene.html) · [NuRec 복원 확장과 장면 레이어](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html) · [데이터셋 장면 형식](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec#dataset-format)

## 관련 도구와 검증 범위

- **후학습** · [AlpaGym](../alpagym.md)은 지원되는 AlpaSim 워크플로에 강화학습을 연결합니다. [Alpamayo Recipes](https://github.com/NVlabs/alpamayo-recipes)는 모델 후학습과 배포 예제를 제공합니다.
- **다른 렌더러** · [FlashDreams를 통한 OmniDreams](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/VIDEO_MODEL.md)는 별도 렌더러 구성입니다. 지원 장면·카메라·체크포인트·GPU 조건을 확인합니다.
- **라이선스** · AlpaSim 코드는 Apache-2.0입니다. VaVAM 자산, 접근 제한이 있는 NuRec 데이터·아티팩트, 컨테이너 구성 요소에는 별도 조건이 적용됩니다. [AlpaSim 라이선스](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/LICENSE) · [NuRec 데이터셋 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec)
- **검증 상태** · 지정 리비전의 공식 튜토리얼, 장면 항목, 출력 경로를 대조했습니다. 이 가이드를 작성하면서 GPU 롤아웃과 자체 로그 확장을 실행하지는 않았습니다.
