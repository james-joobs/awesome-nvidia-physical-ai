# Isaac Lab과 Newton으로 Microduck 보행 학습하기

## 동작 원리

Isaac Lab의 평지 속도 추종 과제에서 Newton으로 로봇을 시뮬레이션하고 RSL-RL로 보행 정책을 학습합니다. 촬영에는 `backlash` 프리셋, 환경 512개, 난수 시드 17을 사용했습니다. 영상은 학습을 마친 체크포인트를 Newton OpenGL 뷰어의 환경 네 개에서 재생한 장면입니다.

## 따라 하기

[Microduck 공식 실습](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real)에 따라 환경을 준비합니다. 촬영 때는 Isaac Lab `d7e49f0`을 사용했습니다. 이 레포에서 첫 줄로 학습한 뒤, 출력된 `model_499.pt` 경로를 `CHECKPOINT` 변수에 넣고 둘째 줄을 실행합니다.

```sh
bash labs/microduck/train.sh /path/to/IsaacLab
bash labs/microduck/play.sh /path/to/IsaacLab "$CHECKPOINT"
```

[ONNX 내보내기 파일](../../../labs/microduck/policy.onnx)도 함께 제공됩니다. 위 재생 명령에서는 학습에 사용한 `.pt` 체크포인트를 불러옵니다.

## 테스트 결과

학습 500회를 완료했습니다. 처음 50회와 마지막 50회를 비교하면 평균 보상은 0.65에서 23.46으로, 평균 에피소드 길이는 35.50스텝에서 320.94스텝으로 늘었습니다. CPU에서 `python labs/microduck/read_training.py labs/microduck/training-metrics.txt ./runs/microduck-metrics`를 실행하면 같은 값을 확인할 수 있습니다. [촬영 당시 학습 기록](../../../labs/microduck/recorded.json)
