# GR00T로 큐브를 집어 그릇에 놓기

## 동작 원리

### 카메라 영상이 어떻게 로봇 동작으로 바뀔까요?

Isaac Sim이 가상 카메라 영상과 로봇 상태를 만들고, Arena가 GR00T N1.6-DROID가 받는 형식으로 관측값을 묶습니다. 여기에 “큐브를 집어 그릇에 놓아라”라는 작업 지시를 더합니다. 담당하는 역할을 나눠 보면 흐름이 보입니다.

| 전달하는 데이터 | 하는 일 | 다음 단계에서 쓰는 곳 |
| --- | --- | --- |
| 카메라 영상 | 손, 큐브, 그릇의 상대 위치를 파악할 단서를 제공합니다. | GR00T의 시각 입력 |
| 로봇 상태와 작업 지시 | 팔의 현재 자세와 달성해야 할 작업을 알려줍니다. | DROID 체크포인트의 상태·언어 입력 |
| 예측한 동작 시퀀스 | 팔 관절과 그리퍼의 목표를 여러 제어 시점에 걸쳐 제안합니다. | Arena 어댑터를 거쳐 Isaac Sim의 제어 입력 |

### GR00T 내부에서는 어떤 계산을 할까요?

이 실습의 DROID 체크포인트는 GR00T N1.6-3B를 DROID 데이터로 미세 조정한 모델입니다. 먼저 시각·언어 모델이 카메라 영상과 지시문을 숫자 표현으로 바꿉니다. 행동을 생성하는 부분은 그 표현과 로봇 상태를 조건으로 받아, 처음에 샘플링한 노이즈를 여러 번 갱신해 연속적인 동작 시퀀스를 만듭니다. 이런 방식으로 입력과 맞는 행동을 생성하도록 학습하는 기법이 **플로 매칭(flow matching)**입니다. 모델 내부의 갱신은 한 번의 행동 예측을 만드는 과정이고, 아래 로그의 스텝은 시뮬레이터가 실제로 동작을 적용한 제어 시점입니다. [NVIDIA N1.6 모델 구조](https://huggingface.co/nvidia/GR00T-N1.6-3B#model-architecture) · [DROID 체크포인트](https://huggingface.co/nvidia/GR00T-N1.6-DROID)

정책이 여러 시점의 동작을 한꺼번에 제안해도, 실행기는 설정된 구간만 적용한 뒤 새 관측을 받아 다시 추론합니다. 팔이 움직이면 카메라에 보이는 장면과 관절 상태가 달라지므로, 화면에 나온 행동을 그대로 재생하는 것과 달리 이후 동작을 다시 정할 수 있습니다. 관절 순서와 정규화는 체크포인트의 설정 및 어댑터가 맞춰야 합니다. [Arena의 GR00T 실행 구조](https://isaac-sim.github.io/IsaacLab-Arena/release/0.3.1/pages/quickstart/running_a_real_policy/gr00t.html) · [GR00T 입력·출력 설정](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_config.md)

### 저장된 로그에서 ‘들기’와 ‘놓기’ 읽기

[70초 설정의 첫 기록](../../../labs/gr00t-placement/recorded-70s.jsonl)에서 일부 필드만 뽑으면 다음과 같습니다. JSONL은 한 줄이 한 시도를 나타내는 텍스트 파일입니다. `progress.events`에 한 시도에서 통과한 조건과 시점이 들어 있습니다.

```json
{
  "success": true,
  "episode_length": 521,
  "progress": { "events": [{ "step": 1 }, { "step": 442 }, { "step": 521 }] }
}
```

`1`은 물체가 안정된 조건, `442`는 큐브가 기준 높이를 넘은 조건, `521`은 물체가 목적지에 놓인 조건을 통과한 제어 스텝입니다. 스텝 수를 그대로 초로 읽으면 안 됩니다. 이 실습의 판정 코드는 15Hz를 기준으로 `442 ÷ 15 ≈ 29.47초`를 구합니다. 앞선 24초 설정 기록에서는 들어 올리는 데 성공한 시도도 최종 배치 조건을 통과하지 못했습니다. 재현할 때는 그리퍼가 닫혔는지와 함께 `object_on_destination` 이벤트까지 확인합니다. [판정 코드](../../../labs/gr00t-placement/check_result.py)

### 행동 배열 읽기

두 카메라 입력은 각각 `[1,1,180,320,3]`이며 배치·시간·높이·너비·RGB 순서입니다. 출력은 `joint_position[1,32,7]`과 `gripper_position[1,32,1]`입니다. 한 번에 행동 32개를 예측하고 일부를 실행한 뒤 새 관측을 읽습니다.

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

창이 닫히고 터미널 입력이 가능해지면 아래 명령을 실행합니다. 파일 이름이 다르면 `find`가 보여준 경로를 두 번째 줄에 넣으세요. `lift`는 들어 올린 때, `placed`는 그릇에 놓였다는 판정을 받은 때를 뜻합니다. `no`는 해당 단계에 도달하지 못했다는 뜻입니다.

```sh
find ./runs/gr00t -name 'episode_results_*.jsonl'
python labs/gr00t-placement/check_result.py ./runs/gr00t/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

### 실제 GUI 화면도 함께 녹화하기

터미널 A의 정책 서버는 그대로 두고, 터미널 B에서는 **2단계 대신** 아래 명령을 실행합니다. 실제로 움직이는 Isaac Sim 창과 시작 시점의 USD 장면, 물체 위치 기록을 저장합니다. X11 데스크톱과 `ffmpeg`, `xwininfo`가 필요하며, 앞서 성공한 동작을 재생하는 방식이 아닙니다.

```sh
export GR00T_GUI_FFMPEG="$(command -v ffmpeg)"
bash labs/gr00t-placement/run_recorded.sh "$ARENA_DIR" 70 ./runs/gr00t-gui
python labs/gr00t-placement/check_result.py \
  ./runs/gr00t-gui/evaluation/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

[GUI 녹화 코드](../../../labs/gr00t-placement/record_gui.py)는 영상·시작 USD 장면·물체 위치를 저장합니다. 모델 입출력도 보려면 [정책 기록 코드](../../../labs/gr00t-placement/record_policy.py)에 `GR00T_MODEL_PATH`와 `GR00T_POLICY_OUTPUT`을 지정하세요.

## 테스트 결과

큐브를 **드는 것**과 **그릇에 놓는 것**을 구분해 보세요. 앞선 70초 예제는 그릇에 놓았지만, 이후 두 시도에서는 집어 든 뒤 그릇을 놓쳤습니다. [이후 시도 영상, 2배속](https://james-joobs.github.io/awesome-nvidia-physical-ai/showcase/gr00t-transfer-check.mp4).

집어 드는 순간에 멈추지 말고 마지막 위치와 `object_on_destination` 판정까지 확인하세요. GPU 없이 동봉한 기록을 검사할 수 있습니다.

```sh
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-24s.jsonl
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-70s.jsonl
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-2026-11-19.jsonl
```

[앞선 성공 기록](../../../labs/gr00t-placement/recorded-70s.jsonl) · [이후 시도 기록](../../../labs/gr00t-placement/recorded-2026-11-19.jsonl)
