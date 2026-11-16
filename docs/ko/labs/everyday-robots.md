# 책상 주변에서 해 본 실험

## 동작 원리

알람은 정지, 직선 후진, 가장자리에서 방향을 트는 세 가지 규칙을 비교합니다. 서랍은 가상 카메라 이미지에서 녹색 카드와 장애물을 색으로 찾고, PhysX 직선 조인트로 열고 닫습니다. 책상 정리는 선택한 물체에 초기 속도를 주어 정리 규칙을 비교합니다. 카트는 세 가지 OpenUSD 배치에서 통과에 필요한 여유 폭을 계산합니다.

## 따라 하기

Isaac Sim에서 [알람](../../../labs/everyday-robots/runaway-alarm.usda), [과자 서랍](../../../labs/everyday-robots/snack-guard.usda), [책상 정리](../../../labs/everyday-robots/desk-cleanup.usda), [카트](../../../labs/everyday-robots/cart-clearance.usda) 중 하나를 열고 `/World/FilmCamera`를 선택한 뒤 **Play**를 누릅니다. 알람 낙하를 크게 보려면 `/World/FallCamera`로 바꿉니다. 카트 씬과 `workbench-asset.usda`는 같은 폴더에 둡니다.

첫 명령에는 NumPy, OpenCV, FFmpeg가 필요합니다. 두 번째와 세 번째는 Isaac Sim Python에서, 마지막은 `usd-core`가 설치된 Python에서 실행합니다.

```sh
python labs/everyday-robots/run_story_demos.py ./runs/stories "$(command -v ffmpeg)"
python labs/everyday-robots/physics.py ./runs/stories/physics ./runs/stories/28-snack-guard/result/result.json
python labs/everyday-robots/desk_cleanup.py ./runs/cleanup
python labs/everyday-robots/aisle.py labs/scene-to-data/workbench_scene.usda ./runs/aisle
```

## 테스트 결과

알람은 직선으로 후진할 때 책상 밖으로 떨어졌고, 가장자리에서 방향을 튼 경우는 책상 위에 남았습니다. 카드가 없는 경우에만 서랍이 약 30.5cm 닫혔습니다. 선별 정리는 과자만 수거함에 넣고 컵과 마우스를 남겼습니다. 통로는 필요한 폭이 80cm라 55cm와 75cm는 통과하지 못했고, 95cm에서 통과했습니다. [촬영 당시 결과](../../../labs/everyday-robots/recorded.json)
