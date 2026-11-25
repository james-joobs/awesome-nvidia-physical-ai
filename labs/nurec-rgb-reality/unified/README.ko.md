# RGB·깊이·카메라를 함께 복원하는 Reality View 실습

[English](README.md) · [기존 실습](../README.md) · [GPU 없이 결과 검사](check.py)

공개 모델로 **RGB 영상에서 깊이와 카메라를 함께 추정**하고, 시간에 따라 바뀌는 3D 표면을 살펴봅니다. 실행한 모델 중 WorldLatent의 생성·복원 구조에 가장 가까운 것은 Aether입니다. 이번 도로에서는 DA3-BASE가 복원용으로 더 실용적이어서, 두 모델의 출력을 나란히 확인할 수 있게 했습니다. 서로 다른 모델이며 WorldLatent나 WorldVAE를 실행한 결과로 표시하지 않습니다.

기존 NuRec Gaussian 장면, Harmonizer 보정, 원본 RGB 객체 인식과 Alpamayo 경로는 유지합니다. 여기에 프레임별 RGB-D 장면을 추가합니다.

## 실제로 실행한 구성

RTX 5090 한 장에서 순서대로 실행했습니다. Aether는 BF16, DA3는 기존에 분리해 둔 Torch 2.8/CUDA 12.8 환경입니다. LiDAR, 데이터셋에서 제공한 센서 보정값·자세·타임스탬프·깊이는 사용하지 않았습니다.

| 실험 | 입력 → 출력 | 추론 시간 | 최대 GPU 메모리 할당량 |
|---|---|---:|---:|
| Aether 복원 | 전방 RGB 17장, 720×480 → RGB·disparity·카메라 ray map | 21.40초 | 14.58GiB |
| Aether 생성 | 첫 RGB + 앞선 복원에서 추정한 카메라 → RGB·깊이·카메라 17프레임, 50 step | 80.24초 | 14.57GiB |
| DA3-BASE 동시 추정 | 같은 전방 RGB 17장, 756×504로 처리 → 깊이·신뢰도·카메라 | 4.50초 | 4.78GiB |
| DA3-BASE 주변 복원 | RGB 6개 카메라 × 17시점, 504×280, 카메라 보조 입력 없음 | 3.41초 | 5.96GiB |
| DA3-BASE + RGB 카메라 보조 입력 | 같은 RGB 102장, 756×420, RGB/SfM으로 추정한 카메라 사용 | 6.33초 | 11.29GiB |

한 번씩 실행한 오프라인 수치입니다. 실시간 카메라 입력부터 화면 표시까지 걸리는 시간은 아닙니다. 102장은 **17시점 × 카메라 6개**이며, 시간상 102프레임을 새로 생성했다는 뜻이 아닙니다. 모델 로딩, 설치·컴파일, 카메라 복원, 결과 저장, 전송과 브라우저 렌더링은 제외했습니다. DA3 시간에는 이미지 전처리와 출력 변환이 포함됩니다. 행마다 해상도·실행 환경·보조 입력이 달라 이 표만으로 속도나 화질의 우열을 판단할 수 없습니다.

공개한 Aether Dockerfile도 별도로 빌드해 다시 실행했습니다. 22.74초, 14.58GiB였으며 RGB·disparity·ray map 배열은 첫 실행과 원소 단위로 같았습니다. 앞선 결과와 전체 정밀도의 출력은 Git 외부 실행 폴더에 보존합니다.

## 브라우저에서 먼저 확인하기

상위 실습의 **실사 도로를 3D로 둘러보기**에서 **3D 시작**을 누릅니다. 기본 화면은 3DGS 배경과 시간별 차량을 함께 보여줍니다. [배경·차량 분리 방식은 별도 문서](../dense/README.ko.md)에 정리했습니다. 기존 RGB-D 실험은 **비교 모드 → 깊이 복원 비교**에서 선택합니다.

1. **DA3-BASE · RGB/SfM camera priors**: 같은 시점의 RGB-D 표면 6개를 배치합니다. 기존 RGB 카메라에 맞춰 볼 수 있지만 카메라 추정 정확도를 독립적으로 검증하는 모드는 아닙니다.
2. **DA3-BASE · 6 RGB cameras**: 카메라 정보 없이 깊이와 카메라를 함께 추정합니다. 관측 범위는 넓어지지만 이번 영상에서는 카메라 정렬 오차가 커졌습니다.
3. **DA3-BASE · front RGB / AetherV1 · front RGB**: 같은 전방 RGB 17장으로 두 모델을 비교합니다.
4. **NuRec**: 더 긴 다중 카메라 영상으로 학습한 기존 정적 Gaussian 장면입니다. 지속적인 외형 표현에 강점이 있지만 움직이는 차량의 잔상이 남을 수 있습니다.

카메라를 바꾸고 마우스로 회전하거나 시간을 움직여 보세요. 왼쪽 RGB의 한 픽셀을 누르면 그 픽셀의 깊이와 3D 좌표를 표시합니다. 실제 모델이 출력한 깊이에 관측 RGB를 입힌 메시입니다. **현재 시점의 카메라 6개를 함께 표시하며, 움직이는 차량을 여러 시간에 걸쳐 쌓지 않습니다.** 관측하지 못한 면은 비어 있고 경계가 불안정한 곳도 있습니다. 기존 NuRec은 학습 데이터와 시간이 달라 동일 조건의 모델 성능 비교는 아닙니다.

각 시퀀스는 첫 카메라 방향과 전역 스케일 하나로 기존 RGB/SfM 화면 좌표에 맞춥니다. 프레임별로 카메라를 고치거나 깊이를 맞추지는 않습니다. 전방 DA3와 Aether의 위치 편차는 기준 경로 길이 대비 각각 0.685%, 2.290%였고, 회전 차이 중앙값은 1.06°, 5.31°였습니다. 기준도 RGB 추정치이므로 **정답에 대한 정확도가 아니라 두 추정치의 일치 정도**입니다. 카메라 보조 입력을 쓰는 모드는 그 자세를 물려받으므로 0에 가까운 편차를 독립적인 성능 향상으로 해석하면 안 됩니다.

## 이미지 한 픽셀이 3D 표면이 되는 과정

```text
RGB uint8[N,H,W,3]
    ├─ Aether: 공유 diffusion transformer
    │    ├─ 복원/생성 RGB [N,H,W,3]
    │    ├─ disparity [N,H,W] → depth = 1/disparity
    │    └─ ray map [N,6,H/8,W/8] → 카메라 자세와 내부 파라미터
    └─ DA3: depth-ray transformer
         ├─ Z-depth float[N,H,W]
         ├─ confidence float[N,H,W]
         └─ world-to-camera [N,3,4] + K [N,3,3]
                    ↓ 자세 역변환, 깊이 역투영
              프레임별 3D 점 / RGB 텍스처 메시
```

카메라 보조 입력 실험의 `N=102`, `H=420`, `W=756`입니다. 여기서 N은 시점 17개 × 카메라 6개이며 학습된 latent의 채널 수가 아닙니다. Aether의 ray map은 방향과 signed-log 변환된 카메라 원점입니다. **Plücker 좌표의 방향·moment를 그대로 넣는 형식이 아니므로** 공식 후처리를 사용합니다. 공개되지 않은 WorldLatent 디코더와 같은 규약이라고 가정하지 않습니다.

실제 저장된 2.4초 전방 카메라의 한 픽셀입니다.

```json
{
  "view_index": 49,
  "pixel_xy": [378, 350],
  "rgb_uint8": [70, 73, 80],
  "z_depth_relative": 3.82502,
  "focal_pixels": [779.25244, 779.70190],
  "camera_xyz_relative": [0.00000, 0.68680, 3.82502],
  "world_xyz_relative": [-4.29220, 0.03739, 0.22340]
}
```

Z-depth는 카메라 정면 축을 따라 잰 깊이입니다. 화면 가장자리로 기울어진 광선의 길이와 다릅니다. 초점거리 `fx, fy`, 이미지 중심 `cx, cy`를 알면 `X=(u-cx)Z/fx`, `Y=(v-cy)Z/fy`로 카메라 좌표를 얻습니다. 여기에 카메라의 회전과 위치를 적용하면 장면 안의 3D 좌표가 됩니다. 단위는 상대 단위이며 실제 미터를 측정한 값이 아닙니다. confidence도 모델 점수이지 확률로 보정된 정확도가 아닙니다.

브라우저에서는 깊이를 2~3픽셀 간격으로 줄이고, 표시 범위 0.1~80 상대 단위 안에서 uint16으로 저장합니다. DA3는 각 이미지의 신뢰도 하위 15%를 숨기고, 이웃 깊이가 10% 이상 갑자기 달라지는 삼각형을 제외합니다. 전체 정밀도의 원본은 실행 폴더에 남습니다. 화면이 부드럽게 회전하는 속도와 저장된 관측 시점 약 3.33Hz는 별개입니다.

## Linux와 NVIDIA GPU에서 따라 하기

먼저 [기존 RGB 복원 실습](../README.md)에 따라 RGB를 준비합니다. 설치 명령, 고정한 버전, Aether·DA3 실행 명령은 [영문 실행 절차](README.md#reproduce-on-linux-with-one-nvidia-gpu)에 순서대로 제공합니다. 소스 이미지, 체크포인트와 원본 로그는 Git 밖에 저장하세요.

1. **입력을 고릅니다.** `prepare_inputs.py`의 `--images`에 카메라별 RGB 폴더를 지정합니다. 00/03/…/48 이미지에서 전방 원본 17장, 같은 영역을 자른 17장, 주변 RGB 102장을 만듭니다. 센서 타임스탬프는 읽지 않습니다.
2. **Aether를 실행합니다.** 고정한 공식 소스와 가중치로 RGB·disparity·ray map을 얻습니다. 실제 T5 빈 프롬프트 임베딩을 계산한 다음 인코더를 메모리에서 내려 GPU 여유를 확보합니다. 0으로 대체하거나 가중치를 바꾸지 않습니다.
3. **DA3를 실행합니다.** `run_da3.py`를 전방 17장, 주변 102장에 각각 실행합니다. 기본적으로 카메라 보조 입력은 없습니다.
4. **필요하면 RGB 카메라를 연결합니다.** 기존 [카메라·학습 입력 준비](../guidance/make_inputs.py)에서 나온 `all-cameras.json`을 `--camera-priors`로 지정합니다. 이 파일도 RGB로 추정한 것이어야 합니다. LiDAR나 제공된 센서 보정값을 썼다는 메타데이터가 있으면 실행기가 거부합니다.
5. **새 폴더에 내보내고 검사합니다.** `export_viewer.py`는 깊이·카메라·RGB를 브라우저용으로 정리합니다. 아래 검사는 GPU 없이 저장된 배열, 좌표와 체크섬을 확인합니다.

```bash
python3 labs/nurec-rgb-reality/unified/check.py
python3 -m unittest discover -s labs/nurec-rgb-reality/unified -p 'test_*.py'
```

Aether의 생성 실험은 첫 이미지와 앞선 복원에서 얻은 카메라만 넣고 50 step으로 실행했습니다. 카메라를 추정할 때는 17장 전체를 봤으므로 아무 정보 없는 미래 예측은 아닙니다. 생성 중 실제 차량이나 신호등이 바뀌거나 사라질 수 있습니다. 이 픽셀을 인식·주행 모델의 사실 확인 자료로 쓰지 않습니다.

새 영상에는 그 영상의 시간·카메라 기준과 차량 위치가 필요합니다. 이 실습의 `cameras.json` 정렬을 다른 도로에 재사용하거나 실제 거리라고 표시하면 안 됩니다. GPU 없는 결과 검사는 저장된 산출물의 무결성 검사이며 새 모델의 정확도 평가가 아닙니다.

## 공식 출처와 사용 조건

- [Aether 코드 / MIT](https://github.com/Sage-PhysicalAI/Aether), [AetherV1 가중치 / MIT 표기](https://huggingface.co/AetherWorldModel/AetherV1). VAE·텍스트 인코더는 [별도 CogVideoX 약관](https://huggingface.co/zai-org/CogVideoX-5b-I2V/blob/main/LICENSE)을 따릅니다. 연구 용도로 사용할 수 있으며 상업적 사용에는 별도 등록·허가가 필요합니다.
- [DA3 코드](https://github.com/ByteDance-Seed/Depth-Anything-3), [DA3-BASE 가중치](https://huggingface.co/depth-anything/DA3-BASE): 이 체크포인트는 Apache-2.0입니다. 크기가 큰 다른 DA3 모델의 조건과 구분해야 합니다.
- [DeepVerse 코드](https://github.com/SOTAMak1r/DeepVerse), [DeepVerse1.1 가중치](https://huggingface.co/SOTAMak1r/DeepVerse1.1): RGB·깊이·행동을 다루는 공개 자기회귀 월드 모델 후보입니다. 가중치 카드는 MIT로 표기하지만 확인한 코드 트리에는 별도 라이선스 파일이 없고, 기반 SD3·Pyramid-Flow 조건도 따로 검토해야 합니다. 공식 실행 설명은 게임 외 이미지의 행동 제어에서 깊이 생성을 끄는 방식을 권장합니다. 이번 실제 도로의 기하 복원에는 선택하지 않았으며 조사만 했습니다.
- [Pi3X](https://huggingface.co/yyfz233/Pi3X): 카메라·깊이를 함께 다루는 공개 대안입니다. 코드는 BSD-3-Clause, 가중치는 CC BY-NC 4.0입니다. 이번에는 조사만 했으며 실행하거나 RGB 생성 월드 모델로 분류하지 않았습니다.
- [WorldMirror 라이선스](https://github.com/Tencent-Hunyuan/HunyuanWorld-Mirror/blob/main/License.txt)는 한국·EU·영국을 사용 허용 지역에서 제외하므로 이번 환경에서는 실행하지 않았습니다.
- [WorldLatent 공식 프로젝트](https://worldlatent.github.io/): 별도의 연구 참고 자료입니다. 앞선 공식 자료 확인에서는 실행 코드·14B/WorldVAE 가중치를 구하지 못했으며, 이 실습에서 대신 실행했다고 표시하지 않습니다.
- [PandaSet·NuRec·Harmonizer·Alpamayo·Volvo 출처](../SOURCES.md). 객체 인식과 Alpamayo 결과는 기존 뷰어에서 원본 RGB 기반으로 확인합니다. 모델 가중치는 재배포하지 않습니다.

직접 작성한 연결 코드는 MIT입니다. RGB 파생 자료와 영상에는 기존 PandaSet의 **CC BY-SA 4.0 + 원본 데이터 약관**을 유지합니다. [표시 자료의 출처](../../../site/public/showcase/reality-joint-geometry/ATTRIBUTION.txt).
