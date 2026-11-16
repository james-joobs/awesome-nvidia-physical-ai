# 같은 카메라에서 RGB·깊이·분할 마스크 얻기

## 동작 원리

`/World/SensorCamera`의 렌더 제품 하나에 Replicator 어노테이터 세 개를 연결합니다. 큐브 위치, 조명 세기, 카메라 위치를 바꾸고 매 네 번째 프레임에는 큐브 앞에 가림판을 둡니다. RGB는 PNG, 깊이와 의미 분할 ID는 NumPy 배열, ID별 클래스 이름은 JSON으로 저장합니다. 깊이의 단위는 미터입니다. [입력 USD 씬](../../../labs/replicator-outputs/replicator-live.usda)

## 따라 하기

Isaac Sim 6.1과 NumPy, Pillow가 설치된 Isaac Lab 환경에서 다음 명령을 실행합니다. Linux X11에서 창을 녹화하려면 첫 명령에 `--record-window "$(command -v ffmpeg)"`를 덧붙입니다. 마지막 명령은 FFmpeg로 데이터 미리보기를 만드는 선택 단계입니다.

```sh
python labs/replicator-outputs/capture.py labs/replicator-outputs/replicator-live.usda ./runs/replicator --viz kit
python labs/replicator-outputs/check_capture.py ./runs/replicator
python labs/replicator-outputs/preview_dataset.py ./runs/replicator
```

[NVIDIA Replicator 튜토리얼](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/tutorial_replicator_getting_started.html)

## 테스트 결과

960 × 540 데이터 12세트가 생성됐습니다. 검사 코드는 배열 크기, RGB 해시, 분할 마스크의 큐브 픽셀 수를 기록과 비교하고, 큐브 위치의 깊이값이 유한한 양수인지 확인합니다. 가림판을 둔 03, 07, 11번 프레임에서는 큐브가 차지하는 픽셀 수가 줄었습니다. [촬영 당시 프레임 기록](../../../labs/replicator-outputs/recorded.json)
