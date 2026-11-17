# Warp로 입자 충돌 계산하기

## 동작 원리

### 가까운 입자만 찾으면 왜 계산이 줄어드나요?

입자 하나는 위치 `[x, y, z]`와 속도를 갖습니다. Warp의 DEM 예제는 입자를 공간의 격자 칸에 넣고, 각 입자에서 가까운 칸의 이웃만 검색합니다. 두 입자가 접촉하면 위치·상대 속도 등을 이용해 힘을 계산합니다. GPU 커널이 여러 입자의 힘을 병렬로 구한 뒤, 시간 간격만큼 속도와 위치를 갱신합니다. [Warp 공식 DEM 코드](https://github.com/NVIDIA/warp/blob/main/warp/examples/core/example_dem.py)

### 시뮬레이션 배열과 뷰어가 출력하는 것

GPU에서 모든 입자를 계산한 뒤 CPU로 받아 읽는 위치 배열의 모양은 `[65536, 3]`입니다. 행 하나가 입자 하나이며 열 세 개가 장면의 X·Y·Z입니다. 뷰어는 `points[::4]`만 그리므로 [기록](../../../labs/warp-particles/recorded.json)의 `particles: 65536`과 `displayed_particles: 16384`는 서로 다른 수입니다.

`mean_particle_displacement_m`은 입자마다 **시작점과 마지막 점 사이의 직선거리**를 구한 다음 평균 낸 값입니다. 전체 경로를 따라 움직인 거리의 합을 의미하지 않습니다. 뷰어를 끈 경우에도 계산 배열은 같은 방식으로 비교할 수 있습니다. [기록을 만드는 코드](../../../labs/warp-particles/run_dem.py)

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
