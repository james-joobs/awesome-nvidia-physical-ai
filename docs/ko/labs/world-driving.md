# Cosmos 영상 생성과 Alpamayo 주행 모델 직접 실행하기

Isaac Sim 이미지 한 장으로 짧은 영상을 만들고, 별도로 직접 구성한 교차로의 카메라 영상을 주행 모델에 넣어 봅니다. 저장된 출력은 GPU 없이도 검사할 수 있습니다. 두 실험은 서로 독립적이며, Cosmos가 만든 영상을 Alpamayo에 연결하는 구성은 아닙니다.

## 동작 원리

### 이미지 한 장으로 이어지는 장면을 만들면?

Cosmos3-Edge는 RGB 이미지와 장면 설명을 받아 잠재 공간에서 영상의 노이즈를 제거한 뒤, 결과를 RGB 프레임으로 복원합니다. 이 실습의 첫 이미지에는 작업대 위의 노란 큐브, 초록 큐브, 검은 블록이 있습니다.

```text
Isaac Sim 카메라 → RGB 이미지 한 장 + 움직임 설명 → Cosmos3-Edge → 생성 영상
                  이미지와 시드는 고정하고 left / right만 변경
```

요청하는 출력은 **24 FPS, 49프레임**으로 약 2.04초입니다. 모델이 USD 장면이나 접촉력, 충돌 판정을 내놓는 것은 아닙니다. 영상 파일이 정상적으로 만들어졌는지와, 우리가 요청한 움직임이 나왔는지는 따로 확인해야 합니다. [공식 추론 입출력 안내](https://nvidia.github.io/cosmos-framework/inference/)

### 카메라 동작을 숫자로 직접 지정하면?

동작 조건을 주는 예제에서는 같은 이미지에 `float32 [60, 9]` 배열을 추가합니다. 한 행은 **모델용으로 정규화된 이동 채널 3개와 6차원 회전 표현**으로 구성됩니다. 미터 단위 이동량을 그대로 넣은 값이 아니며, 다시 정규화해서도 안 됩니다. NVIDIA가 공개한 카메라 동작 예제를 그대로 받아 SHA-256(`547b977c…83c5595`)을 확인합니다. Framework는 이 9개 채널에 패딩을 붙여 모델의 동작 입력 너비에 맞춥니다. [고정 리비전의 공식 카메라 예제](https://github.com/NVIDIA/cosmos-framework/blob/afd7d4c4087a8929c84523ff60172642fd11690b/inputs/omni/action_forward_dynamics_camera.json)

```text
직접 만든 RGB 이미지 + NVIDIA의 카메라 동작 60×9 → forward_dynamics → RGB 61프레임
                                                                     30 FPS
```

첫 프레임은 관측 이미지이고, 이후 60프레임은 모델이 예측한 시점입니다. 촬영한 실행에서는 `480` 해상도 등급의 패딩·크롭을 거쳐 **832×464** 영상이 나왔습니다. 카메라 시점이 달라지는 모습은 확인할 수 있지만, 출력은 생성된 RGB 영상입니다. 새로운 3D 장면을 복원하거나 물리 계산으로 카메라 경로의 정확성을 보장하는 과정은 아닙니다.

### 카메라와 차량의 과거 움직임을 어떻게 경로로 바꿀까?

Alpamayo2-Edge는 카메라 영상, 최근 차량 움직임, 내비게이션 지시를 함께 읽습니다. 시각·언어 모델이 주행 상황에 관한 설명을 만들고, 행동 예측 모듈이 움직임을 예측합니다. 공식 디코더는 예측한 가속도와 곡률을 적분해 미래 위치와 자세를 구합니다. 이 실습의 교차로는 직접 만든 기본 도형으로 구성하며, 접근 제한이 있는 실제 주행 영상은 사용하지 않습니다. [공식 모델 카드](https://huggingface.co/nvidia/Alpamayo2-Edge)

```text
카메라 6대 / RGB 22프레임 ─┐
과거 차량 자세 20개 ────────┼→ Alpamayo2-Edge → 상황 설명 + 미래 자세 64개
"교차로에서 직진하세요" ───┘                 → 저장된 숫자 배열 검사
```

| 실습에서 주고받는 데이터 | 형태와 의미 |
|---|---|
| 카메라 이미지 | CPU `uint8 [22, 1, 3, 360, 640]`. 이미지 22장, 항목당 1프레임, RGB 채널, 높이, 너비 순서입니다. |
| 카메라 ID·촬영 시각 | `int64 [22]`. ID `0/1/2/3/5/6`에 각각 `3/5/3/3/3/5`프레임이 대응합니다. 전방 카메라 두 대는 현재 기준 −2, −1, −0.5, −0.1, 0초, 나머지는 −1, −0.1, 0초를 담습니다. |
| 과거 위치 | `float32 [1, 20, 3]`. 차량 기준 XYZ 위치를 0.1초 간격으로 담습니다. 회전 행렬 `[1, 20, 3, 3]`도 함께 줍니다. 실습에서는 카메라 리그를 5 m/s로 이동시킵니다. |
| 예측 위치 | `[1, 1, 1, 64, 3]`. 배치 1개, 경로 묶음 1개, 후보 1개, 64개의 XYZ 위치입니다. 현재 이후 0.1~6.4초를 0.1초 간격으로 예측하며, 회전 출력은 `[1, 1, 1, 64, 3, 3]`입니다. |

예를 들어 `[5.0, 0.4, 0.0]`은 기준 시점의 차량에서 앞으로 5 m, 왼쪽으로 0.4 m 떨어진 위치를 뜻합니다. 이 숫자는 좌표 설명용 예시이며 실제 예측값은 아닙니다. 직접 만든 도로는 모델이 평가받은 실제 주행 데이터와 다릅니다. **합성 입력으로 모델 연결을 확인하는 실험**이므로, 가중치가 실제로 로드되고 올바른 형태의 출력이 나오는지 확인합니다. 차량을 폐루프로 주행시키는 성능 평가는 아닙니다.

## 실행하기

### 1. Linux GPU 머신에서 전용 폴더 준비하기

GPU 머신에서 터미널을 열고 이 저장소 폴더로 이동합니다. [GPU·드라이버 준비](../onboarding/nvidia-linux.md)를 확인한 뒤, 가중치와 가상환경을 저장할 빈 폴더를 저장소 바깥에 지정하세요. 촬영에 사용한 GPU는 RTX 5090 32 GiB입니다. 소스와 모델 버전은 [model-pins.json](../../../labs/world-driving/model-pins.json)에 고정했습니다.

```bash
export WORLD_DRIVING_ROOT="$HOME/physical-ai-experiments/world-driving"
bash labs/world-driving/setup.sh
```

Cosmos와 Alpamayo는 서로 다른 가상환경에 설치됩니다. Cosmos는 CUDA 13.0 추론용 잠금 파일을, Alpamayo는 Python 3.12용 잠금 파일을 사용합니다. 공개 가중치가 약 13.5 GiB, 촬영 환경의 가상환경 두 개가 약 16 GiB였으며 캐시와 별도로 받는 VAE에도 공간이 필요합니다. 이 실습에는 여유 공간을 최소 60 GiB 확보하고, 사용할 체크포인트의 조건을 확인하세요. [Cosmos 설치 안내](https://nvidia.github.io/cosmos-framework/setup/) · [Alpamayo 설치 안내](https://github.com/NVlabs/alpamayo2-edge#setup)

### 2. 같은 이미지로 두 영상 만들기

같은 터미널에서 아래 두 줄을 차례로 실행합니다. 직접 제작한 시뮬레이터 이미지와 시드 19는 그대로 두고, 큐브의 이동 방향만 바꿉니다. 스크립트는 공동 GPU 잠금을 기다리므로, 다른 실습과 동시에 GPU 메모리를 차지하지 않습니다.

```bash
bash labs/world-driving/run_cosmos.sh right
bash labs/world-driving/run_cosmos.sh left
```

`WORLD_DRIVING_ROOT` 아래의 `outputs/cosmos-right/workbench-right/vision.mp4`를 열어 보세요. 지시한 대로 움직이지 않더라도 두 결과를 모두 남겨 비교합니다. 이 스크립트는 정해진 합성 입력을 처리할 때 추가 가드레일 모델을 끕니다. 서비스로 배포할 때는 별도의 가드레일 구성을 정해야 합니다.

숫자로 지정한 카메라 동작도 넣어 보려면 아래 명령을 실행하세요. 고정한 12 KB 동작 파일을 받아 해시와 배열 형태를 확인하고, 같은 공개 Edge 체크포인트로 추론합니다.

```bash
bash labs/world-driving/run_camera_action.sh
```

### 3. Isaac Sim에서 주행 모델에 넣을 이미지 촬영하기

`ISAAC_LAB_PYTHON`에 Isaac Lab과 Isaac Sim이 설치된 Python 실행 파일 경로를 넣습니다. 촬영 환경은 **Isaac Sim 6.1.0.0 / Isaac Lab 17.0.2**이며, `AppLauncher --viz kit`를 사용합니다. 사이트의 Isaac Sim 6.2 작업대 실습과는 별개 환경입니다. 처음 실행할 때는 시뮬레이터의 라이선스 안내를 확인하세요.

```bash
export ISAAC_LAB_PYTHON="/path/to/IsaacLab/.venv/bin/python"
flock /tmp/physical-ai-four-domains.gpu.lock \
  "$ISAAC_LAB_PYTHON" labs/world-driving/make_driving_scene.py \
  --viz kit --output "$WORLD_DRIVING_ROOT/inputs/synthetic-intersection"
```

GUI에 도로 장면이 열리고, 표에 있는 카메라 위치와 시각에 맞춰 이미지 22장을 촬영합니다. 같은 폴더에 `input.json`과 `synthetic-intersection.usda`도 저장됩니다. Linux X11에서 실제 시뮬레이터 창을 녹화하려면 `--record-window /absolute/path/to/ffmpeg`를 추가하세요. 그래픽 데스크톱의 터미널에서 실행하면 해당 세션의 `DISPLAY`와 `XAUTHORITY`를 사용할 수 있습니다.

### 4. 공개된 주행 모델 가중치로 추론하기

앞에서 촬영한 카메라 이미지와 과거 위치를 읽고, 고정한 BF16 체크포인트를 불러와 설명과 경로를 저장합니다. 가속 추론용 컴파일 없이 기본 PyTorch SDPA 어텐션을 사용합니다.

```bash
python3 labs/cli.py --json run alpamayo-synthetic \
  --python "$WORLD_DRIVING_ROOT/alpamayo2-edge/.venv/bin/python" \
  --input "$WORLD_DRIVING_ROOT/inputs/synthetic-intersection" \
  --model "$WORLD_DRIVING_ROOT/checkpoints/Alpamayo2-Edge" \
  --seed 19 --output "$WORLD_DRIVING_ROOT/outputs/alpamayo-cli"
```

`outputs/alpamayo-cli/output.json`에는 설명, `output.safetensors`에는 예측한 숫자 배열이 저장됩니다. 별도 기록에는 GPU, 패키지 버전, 메모리 사용량, 입출력 배열의 형태를 남깁니다. 모델을 불러오기 전에 가중치 파일 두 개의 SHA-256도 대조합니다. 촬영한 실행의 적응형 추론 출력은 긴 설명 대신 `<NOMINAL>` 토큰이었습니다. 실제 폐루프 주행 평가는 장면 접근 권한을 준비한 뒤 [AlpaSim 실습](../workflows/alpasim-closed-loop.md)에서 진행합니다.

## 결과 확인하기

### GPU 없이 저장된 파일 검사하기

검사에는 Python과 FFmpeg·FFprobe만 있으면 됩니다. 생성 폴더와 Alpamayo 출력 폴더를 지정하면 영상을 끝까지 디코딩해 프레임 수와 FPS를 확인합니다. 저장된 경로 배열도 직접 읽어 잘못된 형태나 유효하지 않은 숫자가 없는지 검사합니다.

```bash
python3 labs/world-driving/check.py \
  --cosmos labs/world-driving/evidence/cosmos-camera-actions \
  --alpamayo labs/world-driving/evidence/alpamayo-synthetic
```

동봉한 공개 결과를 사용하므로 모델을 설치하지 않아도 됩니다. GPU에서 실행한 뒤에는 내 출력 폴더로 바꿔 검사하세요.

`evidence/prediction-scene/alpamayo-trajectory.usda`를 열면 예측한 자세 64개를 Isaac Sim에서 재생합니다. 제어 후 다시 관측하는 피드백은 [AlpaSim 실습](../workflows/alpasim-closed-loop.md)에서 이어갑니다. [재생 장면 생성 코드](../../../labs/world-driving/make_prediction_scene.py).

### 무엇을 비교해야 할까?

- **Cosmos:** 첫 프레임과 마지막 프레임을 나란히 보고, 큐브 방향·카메라 움직임·물체 형태를 확인하세요. `sample_outputs.json`이 `success`여도 지시한 동작이 나오지 않았다면 별도로 기록합니다.
- **Alpamayo:** 빠진 가중치 없이 모델이 로드됐는지, 저장된 좌표가 유효한지, 차량 기준 좌표를 올바르게 읽었는지 확인합니다. 그럴듯한 설명과 경로만으로 안전한 주행을 입증할 수는 없습니다.


[소스·모델 버전](../../../labs/world-driving/model-pins.json) · [Cosmos](../cosmos.md) · [Alpamayo](../alpamayo.md) · [AlpaSim 폐루프 실습](../workflows/alpasim-closed-loop.md)
