# Alpamayo

[← 프로젝트 홈](../../README.ko.md) · [English](../en/alpamayo.md)

Alpamayo는 자율주행용 추론·행동 모델 계열입니다. R1 연구 아키텍처를 구체적인 예로 볼 수 있습니다. 다른 버전에 적용할 때는 모델 카드에서 구성과 입력 규약을 확인합니다.

![Alpamayo-R1 모델 아키텍처](https://arxiv.org/html/2511.00088v2/main_arch_1.png)

*다중 카메라와 자차 움직임이 VLM에 들어가는 경로를 따라가고 추론 토큰과 궤적 디코더의 웨이포인트를 구분해 보세요.* [공식 그림 출처](https://arxiv.org/html/2511.00088v2#S3)

![Alpamayo-R1 인과 추론 데이터 라벨링 파이프라인](https://arxiv.org/html/2511.00088v2/labeling_overview_new_2.png)

*주행 클립이 구체적인 판단과 연결된 라벨 데이터가 되는 과정을 보여줍니다. 추론과는 별도인 학습 데이터 흐름입니다.* [공식 그림 출처](https://arxiv.org/html/2511.00088v2#S3)

## 카메라 영상과 자차 기록이 어떻게 주행 궤적으로 바뀔까요?

### 실제 검증 목록에서 기준 시점 읽기

아래는 NVIDIA가 제공하는 **Alpamayo 2 Super** 검증 목록 첫 항목에서 두 필드를 발췌한 것입니다.

```json
{
  "clip_id": "003e17f1-7c44-4d82-9f32-d4cd82f6a8e8",
  "t0_us": 2000000
}
```

`clip_id`는 PhysicalAI-AV의 영상 구간, `t0_us`는 그 구간 시작 후 **2초**를 뜻합니다. 로더는 이 시점에 맞춰 영상과 자차 위치·회전을 읽습니다. 공식 궤적 예제는 6대 카메라에서 각 4프레임을 사용합니다. 10Hz에서 요청하는 카메라 시점은 1.7, 1.8, 1.9, 2.0초입니다. 디코딩된 실제 타임스탬프는 따로 보관합니다. [고정 리비전의 검증 목록](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/examples/public_golden_validation_samples.json) · [데이터 로더](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/src/alpamayo2_super/load_physical_aiavdataset.py)

### 입력 배열과 예측 결과 구분하기

| 데이터 | 공식 궤적 예제의 형식 | 무엇을 담나요? |
|---|---|---|
| `image_frames` | `[6, 4, 3, H, W]` | 궤적 프로파일이 고른 카메라·프레임·RGB 채널·세로·가로입니다. |
| `ego_history_xyz` | `[1, 1, 16, 3]` | 기준 시점까지의 자차 위치를 자차 좌표계의 XYZ로 나타냅니다. 회전 배열도 따로 읽습니다. |
| 예측 궤적 한 개 | 위치 `[64, 3]`, 회전 `[64, 3, 3]` | 기준 시점 후 0.1~6.4초에 해당하는 경유점의 위치와 회전입니다. |

시각·언어 모델이 영상과 문맥을 표현하고, 궤적 생성 모듈이 조건에 맞는 미래 움직임을 샘플링합니다. 공식 실행 예제는 판단의 근거를 설명하는 텍스트와 궤적을 각각 출력합니다. `minADE`는 각 후보의 XY 경로와 실제 주행 경로 사이의 평균 거리를 구한 뒤 가장 작은 값을 고른 지표입니다. 폐루프 주행에서 충돌·도로 이탈을 보는 방법은 [AlpaSim 평가 실습](workflows/alpasim-closed-loop.md)으로 이어집니다. 이 예시의 수치는 공식 데이터 계약과 검증 목록에 근거합니다. [2 Super 모델 카드](https://huggingface.co/nvidia/Alpamayo2-Super) · [공식 추론 스크립트](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/src/alpamayo2_super/inference_smoke.py)

## 공개 체크포인트

| 모델 | 주요 기능 | 모델과 추론 코드 |
|---|---|---|
| **Alpamayo 2 Edge** · 2026-11-10 | DRIVE AGX Thor를 대상으로 하는 경량 적응형 추론 VLA입니다. Cosmos 3 Edge 백본이 차량 주변 카메라 관측, 자차 움직임 이력, 내비게이션 지시를 받아 미래 궤적을 생성하고 필요할 때 추론합니다. 모델 카드에는 백본 24.5억, 행동 모듈 2억 파라미터로 표기돼 있습니다. | [모델 카드](https://huggingface.co/nvidia/Alpamayo2-Edge) · [GitHub](https://github.com/NVlabs/alpamayo2-edge) |
| **Alpamayo 2 Super** · 2026-08-04 | Cosmos 3 Super Reasoner 320억 파라미터 백본과 확산 기반 행동 모듈을 결합한 340억 파라미터급 주행 파운데이션 모델입니다. 궤적 예측, 인과 추론, 시각 질의응답, 2D 그라운딩, 자동 라벨링을 지원합니다. | [모델 카드](https://huggingface.co/nvidia/Alpamayo2-Super) · [GitHub](https://github.com/NVlabs/alpamayo2) |
| **Alpamayo 1.5** · 2026-03-19 | Cosmos-Reason2 기반의 100억 파라미터급 VLA입니다. 내비게이션 안내, 가변 카메라 수, 시각 질의응답을 지원합니다. | [모델 카드](https://huggingface.co/nvidia/Alpamayo-1.5-10B) · [GitHub](https://github.com/NVlabs/alpamayo1.5) |
| **Alpamayo 1 (R1)** | 인과 추론과 궤적을 함께 출력하는 초기 100억 파라미터급 모델입니다. 위의 아키텍처 그림은 이 버전을 보여줍니다. | [모델 카드](https://huggingface.co/nvidia/Alpamayo-R1-10B) · [GitHub](https://github.com/NVlabs/alpamayo) |

## 작동 방식

R1은 카메라 프레임과 자차 움직임 이력 등 관측을 바탕으로 추론과 궤적을 예측합니다. 비전 언어 백본에서 주행 근거를 생성하고 궤적 생성 구성 요소가 연속 웨이포인트를 출력합니다. 시뮬레이터 드라이버는 궤적을 받아 자차 상태를 진행할 수 있습니다. 추론 텍스트와 실제 움직임은 별도로 확인합니다.

## 사용 순서

부분적으로 가려진 장애물이나 복잡한 합류가 있는 AlpaSim 장면에 Alpamayo 드라이버를 실행합니다. AlpaSim 변경 기록의 `driver=alpamayo2`는 **2 Super**용입니다. Edge는 별도 추론 저장소를 제공하며, NVIDIA 기술 문서는 AlpaGym에서 진행한 Edge의 폐루프 강화학습 후학습을 설명합니다. 추론 근거, 궤적, 롤아웃 지표를 같은 장면·경로의 기준 정책과 비교합니다. [AlpaSim 변경 기록](https://github.com/NVlabs/alpasim/blob/main/CHANGELOG.md) · [Edge 기술 개요](https://developer.nvidia.com/blog/running-av-reasoning-models-within-onboard-compute-and-latency-limits/)

## 검증할 항목

체크포인트가 받는 카메라, 문맥과 좌표계, 요구 메모리 및 접근 조건을 확인합니다. 설명의 그럴듯함과 궤적 품질·주행 동작을 독립적으로 평가합니다.

## 공개 범위와 라이선스

Edge와 Super의 가중치는 Hugging Face에서 공개 다운로드할 수 있으며 OpenMDW-1.1이 적용됩니다. 두 추론 저장소는 Apache-2.0을 사용합니다. Alpamayo 1과 1.5 모델 카드도 OpenMDW-1.1을 연결하며, 비상업적 용도와 별도 문의를 통한 상업 라이선스를 안내합니다. 사용할 체크포인트와 데이터셋의 용도 및 조건을 확인합니다. [Edge 가중치 원문](https://huggingface.co/nvidia/Alpamayo2-Edge/blob/main/LICENSE) · [Super 가중치 원문](https://huggingface.co/nvidia/Alpamayo2-Super/blob/main/LICENSE) · [Edge 코드 원문](https://github.com/NVlabs/alpamayo2-edge/blob/main/LICENSE) · [Super 코드 원문](https://github.com/NVlabs/alpamayo2/blob/main/LICENSE)

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://research.nvidia.com/labs/avg/publication/2025/12/alpamayo-r1/)
- [R1 모델 카드](https://huggingface.co/nvidia/Alpamayo-R1-10B)
- [AlpaSim 드라이버 튜토리얼](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md)
- [튜닝·배포용 Alpamayo Recipes](https://github.com/NVlabs/alpamayo-recipes)
- 주행 추론을 평가하고 학습 보상을 제공하는 AlpaJudge의 [모델 카드](https://huggingface.co/nvidia/alpajudge)와 [소스](https://github.com/NVlabs/alpajudge)

[직접 만든 도로 실습: NuRec 새 시점, Harmonizer 전후 비교, Alpamayo 예측 경로](labs/reality-view.md).
