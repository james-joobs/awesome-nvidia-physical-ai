# 눈으로 확인하는 물리

## 동작 원리

### 화면에 보이는 모양과 물체가 닿는 모양

**메시**는 화면에 그릴 표면, **충돌체**는 물리 엔진이 거리와 접촉을 계산하는 형상입니다. 단순한 상자 충돌체를 쓰면 계산이 가벼워지지만 실제 물체와 위치나 크기가 어긋날 수 있습니다. **강체**를 적용한 물체의 상태에는 위치·방향·속도 등이 들어 있습니다. 엔진은 한 스텝 동안 중력으로 상태를 바꾼 뒤, 접촉이 발견되면 물체가 겹쳐 들어가지 않도록 접촉 반응을 계산합니다. 마찰은 접촉면을 따라 미끄러지는 움직임에, 반발계수는 닿은 뒤 튀어 오르는 움직임에 영향을 줍니다. [Isaac Sim 물리 구성 요소](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

### 두 높이의 차이는 어떤 데이터에 나타나나요?

| 충돌체 설정 | [실행 기록](../../../labs/physics/recorded.json)의 값 | 화면에서 볼 것 |
| --- | --- | --- |
| 보이는 상판과 정렬 | `aligned ≈ 0.80 m` | 탐침이 보이는 상판에 닿습니다. |
| 충돌체만 12cm 위로 이동 | `raised ≈ 0.92 m` | 탐침이 상판 위 공중에서 멈춘 것처럼 보입니다. |
| 상판 충돌체 비활성화 | `disabled ≈ 0 m` | 탐침이 상판을 지나 바닥까지 내려갑니다. |

위 값은 각 탐침 **밑면**의 최종 월드 Z 좌표입니다. 마찰 실험에서는 멈출 때까지의 **이동 거리**, 반발 실험에서는 첫 접촉 이후의 **최대 중심 높이**를 비교합니다. 같은 장면을 PhysX와 Newton에 넣는 별도 실험은 120Hz에서 240스텝을 진행하므로 비교 구간은 2초입니다. 마지막 높이가 비슷해도 다른 축의 위치는 달라질 수 있습니다. [비교에 사용한 초기 조건](../../../labs/physics/scene.json)

## 따라 하기

**준비물** · Isaac Sim 6.1과 이 레포의 [장면 폴더](../../../labs/physics/scenes)를 준비합니다. [Isaac Sim에서 USD 여는 법](../onboarding/isaac-sim-tools.md)을 먼저 볼 수 있습니다.

### 1. 창에서 충돌체 비교하기

1. Isaac Sim에서 **File → Open**으로 `labs/physics/scenes/simready-live.usda`를 엽니다. 옆의 `simready-before.usda`와 `simready-after.usda`는 장면이 참조하는 파일이니 같은 폴더에 둡니다.
2. 뷰포트의 카메라 메뉴에서 **FilmCamera**를 고른 뒤 **Play**를 누릅니다. 두 물체가 같은 높이에 멈추는지 보세요.
3. **Stop**을 눌러 초기 상태로 돌아갑니다. `collider-live.usda`를 열면 충돌체를 올렸을 때와 껐을 때도 비교할 수 있습니다.

### 2. 좌표를 파일로 저장하기

Linux X11에서 영상을 남기려면 Isaac Lab Python 환경이 활성화된 터미널에서 이 레포로 이동합니다. `command -v ffmpeg`에 경로가 나오는지 확인한 뒤 아래 명령을 붙여 넣습니다. `--takes simready offset`은 방금 본 두 장면만 고릅니다.

```sh
python labs/physics/capture_gui.py labs/physics/scenes ./runs/physics "$(command -v ffmpeg)" \
  --plan labs/physics/takes.json --takes simready offset --viz kit
```

뉴턴과 PhysX의 계산을 숫자로 비교하려면 [공통 설정 `scene.json`](../../../labs/physics/scene.json)을 읽는 [PhysX](../../../labs/physics/run_physx.py)·[Newton](../../../labs/physics/run_newton.py) 스크립트를 각 엔진의 Python 환경에서 실행합니다. 두 스크립트는 결과 폴더 경로를 인자로 받고 위치 배열을 저장합니다. [SimReady 검증](https://github.com/NVIDIA/simready-foundation/blob/main/nv_core/sr_specs/docs/guides/validate_workflow.md) · [PhysX](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/simulation_control/simulation_control.html) · [Newton XPBD](https://newton-physics.github.io/newton/latest/api/_generated/newton.solvers.SolverXPBD.html)

## 테스트 결과

SimReady 구슬의 최종 중심 높이는 14cm 차이 났습니다. 충돌체가 맞는 경우, 12cm 올린 경우, 충돌체를 끈 경우에 물체 바닥은 각각 약 0.80m, 0.92m, 0m에서 멈췄습니다. 마찰이 커지면 이동 거리가 57.0cm에서 25.5cm, 11.4cm로 줄었고 반발계수가 커지면 첫 반동이 높아졌습니다. `capture.json`과 물리 샘플을 [촬영 당시 측정값](../../../labs/physics/recorded.json)과 비교할 수 있습니다.
