# Warp로 입자 충돌 계산하기

## 동작 원리

모든 입자끼리 충돌을 검사하면 입자가 늘수록 계산이 커집니다. Warp는 공간을 작은 칸으로 나눠 가까운 입자부터 찾습니다. 닿은 입자가 서로 미는 힘을 계산하고, 그 힘을 반영해 다음 프레임의 위치를 정합니다.

## 따라 하기

**준비물** · NVIDIA GPU가 있는 머신에서 [GPU가 잡히는지](../onboarding/nvidia-linux.md) 먼저 확인합니다. 이 레포 폴더의 터미널에서 실행합니다.

### 1. 가상환경에 Warp 설치하기

아래 세 줄을 같은 터미널에서 실행합니다. `examples`는 입자 예제와 뷰어에 필요한 의존성을 함께 설치합니다.

```sh
python3 -m venv .venv-warp
source .venv-warp/bin/activate
python -m pip install "warp-lang[examples]==1.17.0"
```

### 2. 입자를 움직이고 보고서 읽기

화면을 띄울 수 있는 머신에서는 아래 명령을 실행합니다. 창 없이 접속했다면 첫 줄 끝에 `--headless`를 붙입니다. 화면 표시를 건너뛰어도 계산은 GPU에서 돌아갑니다. 끝나면 두 번째 줄로 보고서를 펼쳐 봅니다.

```sh
python labs/warp-particles/run_dem.py ./runs/warp
python -m json.tool ./runs/warp/result.json
```

`frames`는 계산한 프레임 수입니다. 입자 수와 평균 이동 거리도 같은 파일에 있습니다. [NVIDIA Warp 입자 예제](https://github.com/NVIDIA/warp/blob/main/warp/examples/core/example_dem.py)

## 테스트 결과

입자 65,536개를 200프레임, 시뮬레이션 시간 약 3.33초 동안 계산했습니다. 뷰어에는 16,384개를 그렸고 평균 이동 거리는 17.05m였습니다. 생성된 `result.json`에서 입자 수, 프레임 수, 이동 거리와 실행 시간을 확인할 수 있습니다. [촬영 당시 결과](../../../labs/warp-particles/recorded.json)
