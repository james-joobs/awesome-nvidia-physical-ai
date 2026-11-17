# CAD 작업대에서 센서 데이터까지

## 동작 원리

사진 속 큐브가 왼쪽으로 움직여도 몇 미터 움직였는지는 사진만으로 알기 어렵습니다. **분할 마스크**로 큐브 픽셀만 고르고, **깊이**와 **카메라 위치**로 그 픽셀을 장면 속 3D 점으로 바꿉니다. 이렇게 모은 점을 **점군**이라고 부릅니다.

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
