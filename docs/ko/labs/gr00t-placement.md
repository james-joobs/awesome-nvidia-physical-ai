# GR00T가 큐브를 그릇에 놓기까지

## 동작 원리

Isaac Lab-Arena가 Isaac Sim에서 DROID 집기 과제를 실행합니다. 카메라 영상과 로봇 상태, 자연어 지시를 GR00T N1.6-DROID에 보내고, 모델이 반환한 관절과 그리퍼 목표값을 적용합니다. Arena는 큐브 들기와 그릇에 안정적으로 놓기를 따로 판정합니다. [24초 설정](../../../labs/gr00t-placement/droid-24s.yaml) · [70초 설정](../../../labs/gr00t-placement/droid-70s.yaml)

## 따라 하기

[Isaac Lab-Arena 공식 GR00T 가이드](https://isaac-sim.github.io/IsaacLab-Arena/release/0.3.1/pages/quickstart/running_a_real_policy/gr00t.html)에 따라 설치합니다. 촬영에는 Arena `c7edf3a`와 GR00T 서브모듈 `e29d8fc`를 사용했습니다. GR00T 서브모듈 폴더에서 다음 명령으로 모델 서버를 엽니다.

이 Arena 버전에서 스테이징 에셋 주소가 404를 반환하면 [에셋 주소 패치](../../../labs/gr00t-placement/arena-production-assets.patch)를 Arena 폴더에서 `git apply --unidiff-zero`로 적용합니다. 촬영 때와 같이 같은 에셋을 NVIDIA의 공개 배포 주소에서 불러옵니다.

```sh
uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.6-DROID \
  --embodiment-tag OXE_DROID --device cuda --host 127.0.0.1 --port 5555
```

다른 터미널에서 Arena의 Python 환경을 활성화하고 이 레포 폴더로 이동한 뒤 실행합니다. 모델과 Arena 씬 에셋은 각 공식 프로젝트에서 내려받습니다.

```sh
bash labs/gr00t-placement/run_arena.sh /path/to/IsaacLab-Arena 70 ./runs/gr00t
python labs/gr00t-placement/check_result.py ./runs/gr00t/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

## 테스트 결과

24초 설정에서는 세 번 중 두 번이 들기 판정을 받았고, 그릇에 놓은 경우는 없었습니다. 70초 설정에서는 두 번 모두 성공했고, 시뮬레이션 시간으로 34.73초와 38.27초가 걸렸습니다. 시작 배치도 달랐으므로 이 기록으로 시간 제한의 효과만 따로 판단하기는 어렵습니다. GPU 없이도 결과 검사 코드에 [24초 기록](../../../labs/gr00t-placement/recorded-24s.jsonl)과 [70초 기록](../../../labs/gr00t-placement/recorded-70s.jsonl)을 넣어 판정 시점을 확인할 수 있습니다.
