# 로봇 경로 계획과 시연 생성

## 동작 원리

cuRobo로 Franka 팔의 경로를 두 번 계산했습니다. 시작 자세와 목표는 같고, 두 번째는 기존 팔 경로가 지나던 곳에 직육면체 장애물을 추가했습니다. 화면의 구체는 경로를 계산할 때 사용한 로봇 충돌 형상입니다. AutoData는 동작 구간이 표시된 시연에 MimicGen을 적용해 새 큐브 쌓기 시연을 만들고, 성공한 시연을 Isaac Lab에서 재생합니다. [GR00T 집기·놓기 실습](gr00t-placement.md) · [Microduck 보행 실습](microduck.md)

## 따라 하기

Isaac Sim에서 [cuRobo 경로 씬](../../../labs/robot-motion/curobo-clearance.usda)이나 [AutoData 재생 씬](../../../labs/robot-motion/autodata-stack.usda)을 열고 `/World/FilmCamera`로 바꾼 뒤 **Play**를 누릅니다.

경로를 다시 계산하려면 cuRobo V2 `71ce172`의 CUDA 환경을 사용합니다. AutoData `4a3d1f3`의 Isaac Lab 서브모듈을 포함해 설치하고 공식 실습의 주석이 붙은 Franka HDF5를 준비합니다.

```sh
python labs/robot-motion/plan.py ./runs/curobo
bash labs/robot-motion/autodata.sh /path/to/AutoData /path/to/dataset_franka_annotated.hdf5 ./runs/autodata
python labs/robot-motion/audit.py ./runs/autodata/franka-generated.hdf5 ./runs/autodata-audit
```

[cuRobo 경로 계획](https://nvlabs.github.io/curobo/latest/getting-started/motion_planning.html) · [AutoData 첫 데이터셋 실습](https://github.com/isaac-sim/AutoData/blob/main/docs/pages/quickstart/first_data_generation.rst)

## 테스트 결과

기존 경로는 끝단 중심이 새 장애물 안을 지났고, 재계획한 경로는 우회했습니다. 경유점은 24개와 26개였습니다. AutoData는 여섯 번 시도해 성공 시연 세 개를 생성했고, 재생에서도 세 개가 성공했습니다. HDF5 검사 코드에서 시연별 첫 성공 프레임을 확인할 수 있습니다. [촬영 당시 결과](../../../labs/robot-motion/recorded.json)
