# CAD 작업대에서 센서 데이터까지

## 동작 원리

### 픽셀 하나를 장면 속 점으로 옮기기

첫 단계는 깊이 배열에서 쓸 픽셀을 고르는 것입니다. 라벨 JSON에서 `part` 번호를 찾고 같은 위치의 깊이가 유한한 양수일 때만 남깁니다. 각 픽셀은 카메라에서 뻗어 나가는 한 방향을 나타냅니다. USD 카메라의 초점거리와 센서 폭으로 그 방향을 구하고, 깊이를 더하면 해당 표면의 3D 위치를 계산할 수 있습니다. 코드에서는 이미지 중심이 광축과 일치하고 픽셀이 정사각형이라고 가정합니다.

```text
마스크에서 part 선택 → (열 u, 행 v)와 깊이 읽기
                                  ↓
                     카메라 기준 3D 점
                                  ↓ USD의 카메라 위치·회전
                         월드 좌표 (x, y, z)
```

예를 들어 저장된 첫 프레임에서 `(u=613, v=231)`을 읽으면 깊이는 약 `3.164 m`, 라벨 번호는 `2`입니다. 같은 프레임의 JSON에서 `2`가 `part`이므로 이 픽셀을 점군에 포함합니다. 배경 또는 작업대 라벨이면 같은 깊이가 있어도 큐브 점군에는 넣지 않습니다. [역투영 코드](../../../labs/scene-to-data/backproject.py) · [원본 RGB-D 기록](../../../labs/scene-to-data/replicator-data.zip)

### 왜 첫 프레임과 뺄까요?

각 점군은 카메라에서 보인 표면만 담습니다. 큐브 중심을 바로 읽으려 하면 카메라 방향이나 가려진 면 때문에 오차가 납니다. 그 대신 보이는 점들의 X 중앙값을 구하고 프레임 0의 값과 차이를 냅니다. 프레임 1의 [저장된 결과](../../../labs/scene-to-data/recorded.json)는 `estimated_relative_x_m ≈ -0.300`, `authored_relative_x_m = -0.305`입니다. 음수는 시뮬레이터 월드의 X가 줄었다는 뜻이며, 약 5.27mm는 두 이동량의 차이입니다.

## 따라 하기

**준비물** · 일반 컴퓨터에서 Python 3.12와 터미널을 엽니다. 이 단계는 저장된 카메라 데이터로 계산하므로 GPU 없이 할 수 있습니다.

### 1. 점군을 계산할 Python 준비하기

이 레포의 폴더에서 아래를 실행합니다. 가상환경을 따로 만들면 다른 Python 프로젝트의 패키지와 섞이지 않습니다.

```sh
python3.12 -m venv .venv-workbench
source .venv-workbench/bin/activate
python -m pip install -r labs/scene-to-data/requirements-check.txt
```

### 2. 카메라 데이터 네 세트를 읽기

같은 터미널에서 아래 명령을 실행합니다. `--recorded`는 동봉한 USD와 [카메라 데이터](../../../labs/scene-to-data/replicator-data.zip)를 읽으라는 뜻입니다. `runs/workbench-replay`에 파일과 결과를 저장합니다.

```sh
python labs/scene-to-data/check_workbench.py runs/workbench-replay --recorded
```

`check/frame-00.png`에서 사진과 깊이, 큐브 마스크를 나란히 봅니다. 이동량은 `check/point-cloud/result.json`의 `estimated_relative_x_m`에 미터 단위로 나옵니다. 새 카메라 데이터를 만들고 싶다면 [작업대 완주 과제](workbench-capstone.md)로 이어가세요. [작업대 USD](../../../labs/scene-to-data/workbench_scene.usda) · [점군 재생 장면](../../../labs/scene-to-data/rgbd-surface.usda) · [12프레임 Replicator 실습](replicator-outputs.md)

## 테스트 결과

STEP을 다시 읽어 상판의 가로·세로·두께가 1,200 × 600 × 40mm인지 검사했습니다. 큐브 중심은 0.8615m에서 멈췄습니다. 네 장의 점군에서 계산한 X축 이동량의 최대 오차는 약 5.3mm였습니다. 첫 프레임에서 보이는 표면을 기준으로 이동량을 비교한 값입니다. [촬영 당시 측정값](../../../labs/scene-to-data/recorded.json)
