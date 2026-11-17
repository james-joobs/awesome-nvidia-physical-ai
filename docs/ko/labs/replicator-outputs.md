# Replicator 심화 · 12프레임에서 RGB·깊이·분할 얻기

**별도 심화 실습** · Isaac Sim 6.1과 Isaac Lab에서 예제 USD와 전용 검사 코드로 960 × 540 데이터를 생성합니다. 처음 카메라 데이터를 만든다면 [Isaac Sim 6.2 작업대 완주 과제](workbench-capstone.md)부터 시작하세요.

## 동작 원리

사진만 보면 큐브의 색은 알 수 있지만, 카메라에서 얼마나 떨어져 있는지나 어느 픽셀이 큐브인지는 따로 알아내야 합니다. Replicator는 가상 장면을 이미 알고 있어 같은 촬영에서 **사진·깊이·물체 라벨**을 함께 뽑을 수 있습니다. 여기서 분할 마스크는 픽셀마다 물체 종류를 번호로 구분한 배열입니다.

## 따라 하기

**준비물** · RTX 머신에서 Isaac Sim 6.1과 연결된 Isaac Lab Python 환경을 활성화합니다. [설치 방식과 실행 환경](../onboarding/isaac-sim-tools.md)을 먼저 확인하세요. 이 예제는 Isaac Lab의 앱 실행기를 사용하므로 일반 Python에 NumPy만 설치한 환경으로는 캡처할 수 없습니다.

### 1. 장면을 열고 캡처하기

시뮬레이터를 실행할 머신의 터미널에서 이 레포 폴더로 이동합니다. 첫 경로는 읽을 USD이고, 두 번째는 결과를 저장할 폴더입니다. `--viz kit`를 붙이면 창에서 장면을 볼 수 있습니다. 같은 실습을 다시 할 때는 출력 폴더를 새 이름으로 바꾸세요.

```sh
python labs/replicator-outputs/capture.py \
  labs/replicator-outputs/replicator-live.usda ./runs/replicator --viz kit
```

### 2. 프레임 하나의 파일을 나란히 보기

실행이 끝나면 같은 터미널에서 아래 명령을 실행합니다. `rgb.png`는 이미지 뷰어로, `semantic_labels.json`은 텍스트 편집기로 열어 보세요. `.npy` 두 개는 숫자 배열이므로 검사 코드가 읽습니다. 검사 코드는 색·깊이·분할이 같은 크기인지, 큐브 픽셀의 깊이값이 정상인지 확인합니다.

```sh
ls ./runs/replicator/frames/00
python labs/replicator-outputs/check_capture.py ./runs/replicator
```

FFmpeg가 설치돼 있다면 `python labs/replicator-outputs/preview_dataset.py ./runs/replicator`로 세 채널을 나란히 보는 미리보기도 만들 수 있습니다. [NVIDIA Replicator 튜토리얼](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/tutorial_replicator_getting_started.html)

## 테스트 결과

960 × 540 데이터 12세트가 생성됐습니다. 검사 코드는 배열 크기, RGB 해시, 분할 마스크의 큐브 픽셀 수를 기록과 비교하고, 큐브 위치의 깊이값이 유한한 양수인지 확인합니다. 가림판을 둔 03, 07, 11번 프레임에서는 큐브가 차지하는 픽셀 수가 줄었습니다. [촬영 당시 프레임 기록](../../../labs/replicator-outputs/recorded.json)
