# Warp로 입자 충돌 계산하기

## 동작 원리

Warp의 이산 요소법 예제는 공간 해시 그리드로 가까운 입자를 찾고 CUDA에서 접촉을 계산합니다. 실습 코드는 GPU 계산이 끝난 시점을 기준으로 시간을 재고, 입자 좌표가 유한한 값인지 검사합니다. 화면에는 OpenGL 뷰어로 입자 네 개 중 하나를 그립니다.

## 따라 하기

NVIDIA GPU에서 Warp 1.17.0과 예제 의존성을 설치합니다. 계산 결과만 저장하려면 두 번째 명령에 `--headless`를 붙입니다.

```sh
python -m pip install "warp-lang[examples]==1.17.0"
python labs/warp-particles/run_dem.py ./runs/warp
```

[NVIDIA Warp DEM 소스](https://github.com/NVIDIA/warp/blob/main/warp/examples/core/example_dem.py)

## 테스트 결과

입자 65,536개를 200프레임, 시뮬레이션 시간 약 3.33초 동안 계산했습니다. 뷰어에는 16,384개를 그렸고 평균 이동 거리는 17.05m였습니다. 생성된 `result.json`에서 입자 수, 프레임 수, 이동 거리와 실행 시간을 확인할 수 있습니다. [촬영 당시 결과](../../../labs/warp-particles/recorded.json)
