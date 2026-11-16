# 눈으로 확인하는 물리

## 동작 원리

OpenUSD 씬마다 조건 하나를 바꿨습니다. SimReady 씬은 같은 상자 메시 한쪽에 볼록 껍질 충돌체를 추가합니다. 두 번째 씬은 충돌체를 12cm 올리거나 끕니다. 마찰과 반발 씬은 초기 조건을 고정하고 PhysX 물리 재질만 바꿉니다. PhysX·Newton 화면은 상자 여섯 개를 같은 위치에서 시작해 120Hz로 240스텝 계산한 뒤 자세 기록을 재생합니다. [USD 씬](../../../labs/physics/scenes) · [두 엔진에 사용한 설정](../../../labs/physics/scene.json)

## 따라 하기

Isaac Sim 6.1에서 [USD 씬](../../../labs/physics/scenes)을 열고 뷰포트에서 `/World/FilmCamera`를 선택한 뒤 **Play**를 누릅니다. SimReady의 상자 USD 파일 두 개는 `simready-live.usda`와 같은 폴더에 둡니다. Linux에서 네 장면을 녹화하려면 Isaac Sim이 설치된 Isaac Lab 환경과 X11, FFmpeg가 필요합니다.

```sh
python labs/physics/capture_gui.py labs/physics/scenes ./runs/physics "$(command -v ffmpeg)" \
  --plan labs/physics/takes.json --takes simready offset friction bounce --viz kit
```

솔버별 Python 환경에서 `python labs/physics/run_physx.py ./runs/solvers`와 `python labs/physics/run_newton.py ./runs/solvers`를 실행하면 엔진별 자세 배열이 생성됩니다. [SimReady 검증 가이드](https://github.com/NVIDIA/simready-foundation/blob/main/nv_core/sr_specs/docs/guides/validate_workflow.md) · [Newton XPBD](https://newton-physics.github.io/newton/latest/api/_generated/newton.solvers.SolverXPBD.html)

## 테스트 결과

SimReady 구슬의 최종 중심 높이는 14cm 차이 났습니다. 충돌체가 맞는 경우, 12cm 올린 경우, 충돌체를 끈 경우에 물체 바닥은 각각 약 0.80m, 0.92m, 0m에서 멈췄습니다. 마찰이 커지면 이동 거리가 57.0cm에서 25.5cm, 11.4cm로 줄었고 반발계수가 커지면 첫 반동이 높아졌습니다. `capture.json`과 물리 샘플을 [촬영 당시 측정값](../../../labs/physics/recorded.json)과 비교할 수 있습니다.
