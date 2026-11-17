# 가상 카메라로 과자 서랍 제어하기

## 동작 원리

과자 서랍은 **보고 → 판단하고 → 움직이는** 순서를 보여줍니다. 가상 카메라가 서랍 앞을 찍으면 OpenCV가 지정된 영역에서 카드와 장애물 색을 찾습니다. 결과에 따라 서랍을 한 방향으로 미는 관절을 움직입니다. 같은 방식으로 알람은 손과의 거리, 카트는 통로 폭을 판단에 사용합니다.

## 따라 하기

### 1. Isaac Sim에서 서랍 동작 보기

[과자 서랍 USD](../../../labs/everyday-robots/snack-guard.usda)를 **File → Open**으로 엽니다. 카메라를 **FilmCamera**로 바꾸고 **Play**를 누릅니다. 카드가 보일 때와 입구가 막혔을 때 서랍이 각각 어떻게 움직이는지 보세요.

### 2. 내 컴퓨터에서 판단 로그 만들기

터미널에서 이 레포로 이동합니다. Python, NumPy, OpenCV와 FFmpeg가 필요합니다. `command -v ffmpeg`에 설치 경로가 나오면 아래 블록을 실행합니다. 이 단계는 GPU 없이 할 수 있습니다.

```sh
python3 -m venv .venv-desk
source .venv-desk/bin/activate
python -m pip install numpy opencv-python-headless
python labs/everyday-robots/run_story_demos.py ./runs/stories "$(command -v ffmpeg)"
```

`runs/stories/28-snack-guard/result/result.json`을 텍스트 편집기로 엽니다. `badge_seen`은 카드를 봤는지, `slot_occupied`는 입구가 막혔는지, `drawer_closed_fraction`은 서랍을 얼마나 닫았는지 나타냅니다.

### 3. 다른 장면도 바꿔 보기

[알람](../../../labs/everyday-robots/runaway-alarm.usda), [책상 정리](../../../labs/everyday-robots/desk-cleanup.usda), [카트](../../../labs/everyday-robots/cart-clearance.usda)도 같은 방법으로 열 수 있습니다. 카트의 `workbench-asset.usda`는 원래 폴더에 둡니다. 새 장면을 만들려면 [서랍 물리](../../../labs/everyday-robots/physics.py)·[책상 정리](../../../labs/everyday-robots/desk_cleanup.py)는 Isaac Sim의 Python, [통로 폭 계산](../../../labs/everyday-robots/aisle.py)은 `usd-core`가 설치된 Python에서 실행합니다.

## 테스트 결과

알람은 직선으로 후진할 때 책상 밖으로 떨어졌고, 가장자리에서 방향을 튼 경우는 책상 위에 남았습니다. 카드가 없는 경우에만 서랍이 약 30.5cm 닫혔습니다. 선별 정리는 과자만 수거함에 넣고 컵과 마우스를 남겼습니다. 통로는 필요한 폭이 80cm라 55cm와 75cm는 통과하지 못했고, 95cm에서 통과했습니다. [촬영 당시 결과](../../../labs/everyday-robots/recorded.json)
