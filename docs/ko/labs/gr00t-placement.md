# GR00T로 큐브를 집어 그릇에 놓기

## 동작 원리

로봇에게 큐브를 그릇에 놓으라는 지시를 줍니다. **GR00T**는 다음 동작을 정하는 모델이고, **Isaac Sim**은 그 동작을 가상 로봇에 적용합니다. **Isaac Lab-Arena**는 둘을 연결하고, 큐브를 들었는지와 그릇에 놓았는지를 따로 판정합니다. 시뮬레이터가 모델에게 계속 질문할 수 있도록 터미널 두 개를 사용합니다.

## 따라 하기

**준비물** · 화면을 띄울 수 있는 RTX Linux 환경과 `uv`가 필요합니다. [Isaac Sim 환경](../onboarding/isaac-sim-tools.md)과 [Arena 공식 설치·GR00T 가이드](https://isaac-sim.github.io/IsaacLab-Arena/release/0.3.1/pages/quickstart/running_a_real_policy/gr00t.html)의 Native uv 환경을 준비하세요. 이 예제는 Arena `c7edf3a`, GR00T 서브모듈 `e29d8fc`를 기준으로 합니다. 아래에서는 두 레포를 홈 폴더에 내려받았다고 가정합니다. 다른 곳에 받았다면 `cd`와 `ARENA_DIR`의 경로를 바꾸세요.

### 1. 터미널 A에서 GR00T 켜 두기

Arena 폴더로 이동해 GR00T 코드를 받은 뒤 모델을 실행합니다. 아래 블록을 한 번에 붙여 넣어도 됩니다. 첫 실행에서는 모델 파일을 내려받습니다. 모델이 준비되면 이 터미널은 그대로 둡니다.

```sh
cd "$HOME/IsaacLab-Arena"
git submodule update --init submodules/Isaac-GR00T
cd submodules/Isaac-GR00T
uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.6-DROID \
  --embodiment-tag OXE_DROID --device cuda --host 127.0.0.1 --port 5555
```

### 2. 같은 머신의 터미널 B에서 로봇 움직이기

Arena의 Python을 활성화하되, 실행할 스크립트는 이 레포에 있으므로 `cd`로 이동합니다. 아래의 `70`은 [한 시도에 70초를 주는 설정](../../../labs/gr00t-placement/droid-70s.yaml)입니다. 실행하면 Isaac Sim 창이 열리고 팔이 움직입니다. Arena는 같은 머신의 `127.0.0.1:5555`에서 터미널 A의 모델에 동작을 요청합니다.

```sh
ARENA_DIR="$HOME/IsaacLab-Arena"
source "$ARENA_DIR/.venv/bin/activate"
cd "$HOME/awesome-nvidia-physical-ai"
bash labs/gr00t-placement/run_arena.sh "$ARENA_DIR" 70 ./runs/gr00t
```

Arena가 스테이징 에셋 주소에서 404를 반환한다면, [에셋 주소 패치](../../../labs/gr00t-placement/arena-production-assets.patch)를 Arena 폴더에서 `git apply --unidiff-zero`로 적용한 뒤 2단계를 다시 실행합니다.

### 3. 터미널 B에서 내 실행 기록 읽기

창이 닫히고 터미널 입력이 가능해지면 아래 명령을 실행합니다. 파일 이름이 다르면 `find`가 보여준 경로를 두 번째 줄에 넣으세요. `lift`는 들어 올린 때, `placed`는 그릇에 안정적으로 놓인 때를 뜻합니다. `no`는 해당 단계에 도달하지 못했다는 뜻입니다.

```sh
find ./runs/gr00t -name 'episode_results_*.jsonl'
python labs/gr00t-placement/check_result.py ./runs/gr00t/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

## 테스트 결과

24초 설정에서는 세 번 중 두 번이 들기 판정을 받았고, 그릇에 놓은 경우는 없었습니다. 70초 설정에서는 두 번 모두 성공했고, 시뮬레이션 시간으로 34.73초와 38.27초가 걸렸습니다. 시작 배치도 달랐으므로 이 기록으로 시간 제한의 효과만 따로 판단하기는 어렵습니다.

### GPU 없이 기록 다시 확인하기

레포 최상위 폴더에서 두 명령을 실행합니다. Python으로 동봉한 [24초 기록](../../../labs/gr00t-placement/recorded-24s.jsonl)과 [70초 기록](../../../labs/gr00t-placement/recorded-70s.jsonl)을 읽어 들기와 놓기 시점을 확인할 수 있습니다.

```sh
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-24s.jsonl
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-70s.jsonl
```
