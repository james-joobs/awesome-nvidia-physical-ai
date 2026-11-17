# 로봇 경로 계획과 시연 생성

## 동작 원리

### 팔 끝의 목표를 여러 관절의 경로로 바꾸기

목표는 팔 끝의 위치와 방향으로 정하고, 출발은 관절 값의 벡터로 정합니다. 로봇 모델을 통해 관절을 움직였을 때 팔 끝과 각 링크가 어디에 놓이는지 계산할 수 있습니다. cuRobo는 목표에 닿는 관절 자세와 도중에 충돌을 피할 경로를 찾습니다. 장애물을 모델에 추가하면 같은 목적지라도 허용되는 중간 자세가 달라집니다. [cuRobo 공식 문서](https://curobo.org/) · [이 실습의 계획 코드](../../../labs/robot-motion/plan.py)

| 출력 | 읽는 법 |
| --- | --- |
| `motion.npz`의 `baseline_q`, `obstacle_q` | 각 행이 경로의 한 시점입니다. 열은 로봇 모델 순서의 관절 값입니다. |
| `baseline_tool`, `obstacle_tool` | 각 행은 팔 끝 위치 `[x, y, z]`입니다. 이 실습의 기준 경로는 24행, 우회 경로는 26행입니다. |
| `result.json`의 `replanned_tool_enters_obstacle` | 저장된 팔 끝 표본이 새 장애물 상자 내부에 들어갔는지 알려줍니다. 팔 링크 전체의 충돌 판정은 플래너가 따로 수행합니다. |

### 경로 계획과 시연 생성이 어디서 갈라지나요?

AutoData 실습은 별도로 실행합니다. MimicGen은 성공 시연에서 물체를 집고 놓는 구간을 재사용해 새로운 물체 배치에 맞게 시연을 만듭니다. 시뮬레이터에서 실행해 성공한 시연을 남깁니다. [기록](../../../labs/robot-motion/recorded.json)의 `num_attempts: 6`, `num_success: 3`은 이 장면에서 생성한 시도와 성공 시연의 개수입니다. `demo_0`의 `first_success_frame: 243`은 성공을 처음 기록한 프레임이며 관절 경로의 길이와는 다른 지표입니다. [MimicGen 공식 프로젝트](https://github.com/NVlabs/mimicgen)

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
