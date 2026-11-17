# Isaac Lab과 Newton으로 Microduck 보행 학습하기

## 동작 원리

처음의 보행 정책은 목표 속도에 맞춰 걷는 법을 모릅니다. Isaac Lab이 같은 연습장을 여러 개 띄우고, **Newton**이 발과 바닥의 접촉을 계산합니다. **RSL-RL**은 목표 속도를 얼마나 잘 따라갔는지 점수로 받아 정책을 고칩니다. 학습한 값을 저장한 파일이 **체크포인트**입니다.

## 따라 하기

**준비물** · 새 학습은 RTX 머신에서 합니다. [NVIDIA Microduck 설정](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real)을 따라 Isaac Lab `d7e49f0` 환경과 `uv`를 준비합니다. 아래는 Isaac Lab을 홈 폴더에 받았다는 예입니다.

### 1. 보행 정책 학습하기

이 레포 폴더에서 터미널을 엽니다. Isaac Lab을 다른 곳에 받았다면 첫 줄의 경로를 바꾸세요. 학습 중에는 터미널에 반복 횟수와 보상이 표시됩니다. 이 예제는 가상 환경 512개로 500회 학습합니다.

```sh
ISAAC_LAB_DIR="$HOME/IsaacLab"
bash labs/microduck/train.sh "$ISAAC_LAB_DIR"
```

### 2. 학습을 마친 로봇 재생하기

프롬프트가 돌아오면 로그에 나온 `model_499.pt` 경로를 확인합니다. 아래 첫 줄의 예시를 내 파일의 전체 경로로 바꾼 뒤, 같은 터미널에서 두 줄을 실행합니다. 재생은 학습된 정책으로 가상 로봇을 걷게 합니다.

```sh
CHECKPOINT="/실제/학습/폴더/model_499.pt"
bash labs/microduck/play.sh "$ISAAC_LAB_DIR" "$CHECKPOINT"
```

함께 제공하는 [ONNX 파일](../../../labs/microduck/policy.onnx)은 다른 런타임으로 내보낸 모델입니다. 위 Isaac Lab 재생에서는 학습으로 생성한 `.pt` 파일을 사용합니다.

## 테스트 결과

내 실행에서는 보상이 학습 초반보다 올라가는지, 로봇이 목표 속도로 걷는지 확인합니다. 보상은 주어진 목표를 얼마나 잘 따랐는지 나타내는 점수입니다.

**GPU 없이 기존 학습 기록 읽기** · 이 레포 폴더에서 아래 명령을 실행합니다. 학습을 다시 돌리지 않고 저장된 로그의 앞·뒤 50회 평균을 계산합니다.

```sh
python3 labs/microduck/read_training.py labs/microduck/training-metrics.txt ./runs/microduck-metrics
```

촬영 당시 평균 보상은 0.65에서 23.46으로, 에피소드 길이는 35.50스텝에서 320.94스텝으로 늘었습니다. [촬영 당시 학습 기록](../../../labs/microduck/recorded.json)
