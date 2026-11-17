# 가상 카메라로 과자 서랍 제어하기

## 동작 원리

### 카메라 영상을 세 가지 판단 값으로 바꾸기

실습 스크립트는 손·카드·장애물을 그린 컬러 배열을 만들어 카메라 입력으로 사용합니다. OpenCV는 영상 전체를 분류하는 대신, 손·카드·서랍 입구가 있을 위치를 잘라 **관심 영역(ROI)** 세 곳을 봅니다. 각 영역에서 지정한 BGR(파랑·초록·빨강) 범위에 들어온 픽셀만 마스크에 남깁니다. 예를 들어 카드 영역의 초록색 후보가 160픽셀을 초과하면 `badge_seen`을 참으로 기록합니다. [카메라 입력과 제어 코드](../../../labs/everyday-robots/run_story_demos.py) · [OpenCV 색 범위 마스크](https://github.com/opencv/opencv/blob/4.x/doc/tutorials/imgproc/threshold_inRange/threshold_inRange.markdown)

### 의사결정과 이동은 어떻게 연결되나요?

손을 발견하면 닫힘 동작을 검사하기 시작합니다. 그 뒤 초록색 카드가 보이거나 서랍 입구가 막혀 있으면 닫힘 목표를 0으로 유지합니다. 두 조건 모두 없으면 목표를 1로 바꾸고, 각 프레임에서 조금씩 움직입니다.

| 추적 필드 | 해석 |
| --- | --- |
| `badge_seen`, `slot_occupied` | 영상에서 찾은 카드·장애물 판정입니다. 같은 색의 카드를 든 사람은 같은 판정을 받습니다. |
| `drawer_closed_fraction` | 닫힘 정도를 0~1로 기록합니다. 0은 열린 상태, 1은 닫힌 상태입니다. |
| `drawer_final_m` | [영상 장면의 저장된 결과](../../../labs/everyday-robots/recorded.json)에 기록된 최종 슬라이드 이동량입니다. 카드가 없고 입구가 빈 사례는 약 0.305m 이동했습니다. |

이 흐름을 다른 예제에도 적용할 수 있습니다. 카트에서는 영상 대신 **통로 폭**이 입력이고, 정리 예제에서는 물체를 버릴지 보관할지 정한 **작업 규칙**이 입력입니다. 각각 판단에 쓰이는 데이터를 하나만 바꿔 결과를 비교할 수 있습니다.

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
