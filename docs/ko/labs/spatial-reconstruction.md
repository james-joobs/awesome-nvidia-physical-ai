# 직접 둘러볼 수 있는 3DGS 광장 복원하기

[English](../../en/labs/spatial-reconstruction.md) · [실습 코드](../../../labs/spatial-reconstruction/)

## 카메라 사진이 어떻게 탐색할 수 있는 공간이 될까요?

CARLA 분수 광장을 **fVDB Gaussian Splatting**으로 복원했습니다. 3D 화면에서 회전·이동·확대를 해 보거나 저장된 시연 영상을 살펴보세요.

![입력과 출력의 흐름](../../../assets/lessons/spatial-worlds/reconstruction.ko.svg)

### 사진, 카메라 정보, 깊이의 역할

`640 × 360` RGB 이미지 72장과 카메라 내부 파라미터 `K`, 월드→카메라 변환 행렬, 미터 단위 깊이를 촬영했습니다. 수평 화각은 80°이며 `fx = fy ≈ 381.36px`입니다. 픽셀의 `(u-cx)/fx`, `(v-cy)/fy`와 깊이로 카메라 기준의 3D 점을 구합니다. 여기에 카메라→월드 행렬을 적용하면 서로 다른 사진의 점들을 같은 공간에 놓을 수 있습니다. 시뮬레이터에서 **정확한 카메라 자세를 알고 있으므로** COLMAP으로 자세를 추정하는 단계는 없습니다.

```json
{
  "image_path": "view_000.png",
  "width": 640,
  "height": 360,
  "camera_intrinsics": [[381.361, 0, 320], [0, 381.361, 180], [0, 0, 1]],
  "world_to_camera": "4 x 4 matrix; see evidence/cameras.json"
}
```

읽기 쉽게 반올림한 예시입니다. [실제 카메라 파일](../../../labs/spatial-reconstruction/evidence/cameras.json)에는 전체 값이 들어 있습니다. CARLA의 왼손 좌표계를 오른손 좌표계로 바꾸기 위해 월드 Y축을 반전하고, 카메라 축을 OpenCV의 오른쪽·아래쪽·전방 기준으로 맞췄습니다. 이 부호를 잘못 바꾸면 공간이 거울처럼 뒤집힙니다.

`view_000.png`의 중앙 픽셀 `(320,180)`을 직접 읽으면 깊이는 **21.237m**입니다. 카메라 기준으로 약 `[0,0,21.237]m`이고, 저장한 카메라 자세를 적용하면 월드 좌표 `[0.958,0,2.131]m`가 됩니다. [실제 샘플](../../../labs/spatial-reconstruction/evidence/point-sample.json)에 전체 값을 넣었으며 `check.py`가 이 변환을 다시 계산합니다.

### Gaussian 하나에는 무엇이 들어 있을까요?

중심 좌표 `[x,y,z]`, 세 축의 크기, 회전 쿼터니언, 불투명도, 색 계수를 저장합니다. 공간에 놓인 부드러운 타원체라고 생각하면 됩니다. fVDB가 이 타원체들을 화면에 투영하고 겹쳐 그린 뒤 학습 사진과 비교합니다. 오차가 줄어드는 방향으로 값을 조정하고, 필요한 곳에는 Gaussian을 늘리거나 지웁니다. 이번 전체 모델에는 **345,318개**가 들어 있습니다. [fVDB Reality Capture](https://github.com/openvdb/fvdb-reality-capture)

브라우저에서는 전체 Gaussian 장면을 압축한 미리보기를 사용합니다. 로봇 시뮬레이션에 연결하려면 충돌체와 제어기를 별도로 구성합니다.

### 새로운 세계를 생성한 것과는 무엇이 다를까요?

이 실습은 **주어진 장면을 복원**합니다. 프롬프트로 보이지 않던 골목을 만들어 내지는 않습니다. World Labs Marble과 NVIDIA Lyra는 생성형 3D 세계를, Infinigen은 규칙으로 조합한 실제 기하 구조를 다룹니다. [3D 세계 도구 비교](../spatial-worlds.md)에서 출력 형식과 실행 조건을 나누어 볼 수 있습니다.

사진 한 장으로 복원하는 비교 영상은 **Apple SHARP**를 사용합니다. 가까운 시점으로 움직여 보고 여러 사진으로 복원한 장면과 관측 범위를 비교하세요.

## 새로운 장면을 촬영하고 복원하기

### 1. 여러 시점 촬영하기

[CARLA 실습의 설치 순서](carla-ego.md)를 따라 터미널 A에 0.9.16 서버를 띄웁니다. 터미널 B에서는 CARLA용 Python 환경을 활성화하고 저장소 폴더에서 실행하세요.

```bash
python labs/spatial-reconstruction/capture.py --output runs/plaza-input
```

RGB와 깊이 센서가 Town03 광장 주변을 이동합니다. `Saved view 72/72`가 나오면 촬영이 끝납니다. `images/`에는 색 PNG, `depth/`에는 미터 단위 NumPy 배열, `cameras.json`에는 촬영 당시의 정확한 카메라 자세가 저장됩니다. `prepare_seed.py`는 초기 점군을 만들 때 **검사용으로 남겨 둔 이미지와 그 깊이·색을 사용하지 않습니다.** `0,8,16,…`번이 검사 대상입니다.

다음 GPU 작업을 시작하기 전에 직접 띄운 CARLA 컨테이너를 종료하세요. CARLA와 fVDB의 Python 환경은 별도로 준비합니다.

### 2. Gaussian 학습하기

GPU에 맞는 PyTorch·CUDA 조합으로 [공식 설치 가이드](https://fvdb-reality-capture.readthedocs.io/stable/installation.html)를 따라 fVDB와 fVDB Reality Capture를 설치합니다. 해당 환경에서 `plyfile`, Pillow, SciPy도 준비하세요. 검증한 환경은 RTX 5090, fVDB 0.6.0, PyTorch 2.13.0+cu130입니다. 정확한 실행 정보는 `recorded.json`에 남겼습니다.

```bash
python labs/spatial-reconstruction/reconstruct.py \
  --input runs/plaza-input --output runs/plaza-3dgs --ffmpeg ffmpeg
```

RGB 63장으로 40에포크를 학습하고, 전체 PLY와 가벼운 `.splat`, 새 카메라 경로의 영상을 저장합니다.

브라우저용 모델은 Gaussian을 버리지 않고 전체 PLY를 PlayCanvas CLI로 압축합니다.

```bash
python3 labs/spatial-reconstruction/compress_web.py runs/plaza-3dgs/town03.ply runs/plaza-3dgs/town03.spz
```

### 3. 사진 한 장으로도 비교하기

선택 실습입니다. [SHARP](https://github.com/apple-aiml-research/ml-sharp)와 의존성을 fVDB도 불러올 수 있는 환경에 설치합니다. 연구용 모델 라이선스를 확인한 뒤 [공식 체크포인트](https://ml-site.cdn-apple.com/models/sharp/sharp_2572gikvuh.pt)를 받으세요. 앞서 찍은 CARLA 운전자 JPEG들을 `runs/sharp-input/`에 넣고 실행합니다.

```bash
python labs/spatial-reconstruction/reconstruct_single.py \
  --input runs/sharp-input --output runs/sharp-output \
  --checkpoint /path/to/sharp_2572gikvuh.pt --ffmpeg ffmpeg
```

이 코드는 이번 CARLA의 90° 카메라를 가정합니다. 다른 사진에는 해당 초점거리를 사용해야 합니다. 좌우 ±0.35m 범위로 시점을 움직입니다. 크게 이동하면 입력에서 보지 못한 빈 공간이 드러납니다.

## GPU 없이 결과 검사하기

![CARLA RGB / fVDB 3DGS](../../../assets/lessons/spatial-worlds/reference-vs-render.webp)

```bash
python3 labs/spatial-reconstruction/check.py
```

저장한 카메라·모델·영상의 유효성을 검사합니다. 원본과 복원 화면에서 물결·먼 건물·촬영 범위 바깥을 비교하세요. [실행 상세](../../../labs/spatial-reconstruction/recorded.json).

저장소에는 코드·카메라 정보·지표·압축 영상·브라우저용 모델을 넣었습니다. [미디어 출처와 이용 조건](../../../site/public/showcase/SPATIAL-CREDITS.md) · [실내 장면 생성하기](scene-generation.md) · [fVDB 동작 원리](../fvdb-reality-capture.md).
