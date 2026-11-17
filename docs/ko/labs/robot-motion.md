# 로봇 경로 계획과 시연 생성

## 동작 원리

팔의 시작과 목표는 같은데 중간에 상자가 생겼다면 갈 수 있는 길이 달라집니다. **cuRobo**는 팔이 장애물에 닿지 않도록 관절 위치의 순서를 계산합니다. 시연 생성은 별도 실습입니다. **AutoData**는 사람이나 로봇이 한 번 보여준 동작을 바탕으로 다른 시작 조건에서 쓸 시연 데이터를 만듭니다.

## 따라 하기

### 1. Isaac Sim에서 이미 만든 두 경로 보기

[cuRobo 경로 장면](../../../labs/robot-motion/curobo-clearance.usda)을 **File → Open**으로 엽니다. 카메라를 **FilmCamera**로 바꾸고 **Play**를 누릅니다. 같은 목표를 향하는 두 경로 중 장애물을 비켜 가는 쪽을 찾아보세요. 이 단계는 경로 계산 환경 없이도 장면을 열 수 있습니다.

### 2. 터미널에서 새 경로 계산하기

RTX 머신에 [cuRobo V2](https://nvlabs.github.io/curobo/latest/getting-started/motion_planning.html) `71ce172` 환경을 준비합니다. 그 Python이 활성화된 터미널에서 이 레포로 이동하고 아래를 실행합니다. `motion.npz`에는 경로 좌표 배열이, `result.json`에는 비교 결과가 남습니다.

```sh
python labs/robot-motion/plan.py ./runs/curobo
```

### 3. 새 시연 데이터가 필요하면 AutoData 실행하기

먼저 [AutoData 공식 예제](https://github.com/isaac-sim/AutoData/blob/main/docs/pages/quickstart/first_data_generation.rst)에서 `4a3d1f3`과 Isaac Lab 서브모듈, 동작 구간을 표시한 Franka HDF5를 준비합니다. HDF5는 여러 시도의 관절 값과 물체 위치를 한 파일에 담습니다. AutoData 환경을 켠 터미널에서 첫 두 줄을 내 경로로 바꾸고 실행하세요.

```sh
AUTODATA_DIR="$HOME/AutoData"
DEMO_FILE="$HOME/dataset_franka_annotated.hdf5"
bash labs/robot-motion/autodata.sh "$AUTODATA_DIR" "$DEMO_FILE" ./runs/autodata
python labs/robot-motion/audit.py ./runs/autodata/franka-generated.hdf5 ./runs/autodata-audit
```

[AutoData 재생 장면](../../../labs/robot-motion/autodata-stack.usda)으로 시연을 먼저 살펴봐도 됩니다. [GR00T 집기·놓기](gr00t-placement.md) · [Microduck 보행](microduck.md)

## 테스트 결과

기존 경로는 끝단 중심이 새 장애물 안을 지났고, 재계획한 경로는 우회했습니다. 경유점은 24개와 26개였습니다. AutoData는 여섯 번 시도해 성공 시연 세 개를 생성했고, 재생에서도 세 개가 성공했습니다. HDF5 검사 코드에서 시연별 첫 성공 프레임을 확인할 수 있습니다. [촬영 당시 결과](../../../labs/robot-motion/recorded.json)
