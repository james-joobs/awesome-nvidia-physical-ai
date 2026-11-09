# MuJoCo Warp (MJWarp)

[← 전체 목록](../../README.ko.md) · [English](../en/mujoco-warp.md)

MuJoCo Warp는 MuJoCo 동역학을 NVIDIA Warp로 CUDA에서 실행한다. 동일 로봇과 작업을 수천 개의 독립 환경에서 동시에 반복하는 작업에 맞춰 배치 상태를 구성한다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| MJCF → `MjModel` / `MjData` | MuJoCo가 로봇·환경을 읽어 모델을 컴파일한다. 호스트의 모델과 초기 상태가 장치 변환 입력이 된다. |
| `mjw.put_model` / `mjw.put_data` | GPU 모델과 데이터를 생성한다. 여러 동적 Data 필드의 첫 차원은 nworld이며 접촉과 제약 저장 공간은 미리 정한다. |
| `mjw.step`과 그래프 캡처 | Warp 커널이 기구학, 충돌, 제약, 적분, 센서 데이터를 계산한다. GPU 스텝을 반복할 때 캡처·재생으로 커널 호출 비용을 줄일 수 있다. |
| 연동 경계 | 네이티브 MuJoCo Warp와 MJX의 impl="warp" 경로는 Warp 구현에 서로 다른 인터페이스를 제공한다. Newton은 자체 Model과 State API에서 MuJoCo 기반 솔버를 노출한다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    xml["MJCF 로봇과 장면"]
    host["호스트 MjModel과 MjData"]
    gpu["GPU 모델과 배치 Data"]
    act["환경별 제어 입력"]
    step["충돌·제약·적분"]
    read["관절 상태와 센서"]
    xml --> host
    host --> gpu
    gpu --> step
    act --> step
    step --> read
    step --> gpu
```

### 공식 그림과 예시

![평지에서 진행한 Unitree G1 벤치마크 롤아웃. 공식 벤치마크 구성에서 제어와 시뮬레이션 조건을 비교할 수 있다.](https://raw.githubusercontent.com/google-deepmind/mujoco_warp/main/benchmarks/unitree_g1/rollout_flat.webp)

평지에서 진행한 Unitree G1 벤치마크 롤아웃. 공식 벤치마크 구성에서 제어와 시뮬레이션 조건을 비교할 수 있다. [그림 출처와 원문 설명](https://github.com/google-deepmind/mujoco_warp/tree/main/benchmarks/unitree_g1)

## 워크플로 예시

1. Unitree G1 벤치마크나 환경 한 개를 실행해 관절 인덱스, 제어 방식과 보행 정책에 필요한 관측을 점검한다.
2. nworld를 늘리고 지형에 맞는 접촉·제약 저장 용량을 정한다. 환경별 제어를 장치 배열에 쓰고 스텝을 진행해 다음 정책 행동에 필요한 상태를 읽는다.
3. 초당 전체 환경 스텝 수와 단일 스텝 지연을 함께 측정한다. 다중 환경 벤치마크와 대화형 단일 로봇 제어에서 중요한 지표가 다르다.

## 검증 포인트

- njmax는 환경별 제약 수를 제한한다. nconmax 또는 naconmax 방식으로 접촉 풀을 환경 사이에 공유한다. 넘어짐과 다중 접촉에서 용량 초과 진단을 확인한다.
- 대상 릴리스의 기능표를 읽고 작은 장면에서 CPU MuJoCo와 결과를 비교한다. MJX-Warp는 자동 미분을 지원하지 않는다.

## 라이선스와 범위

MuJoCo Warp는 Apache-2.0이다. 모델과 에셋 약관은 별도로 확인한다.

## 관련 가이드

[Newton](newton.md) · [Warp](nvidia-warp.md) · [Isaac Lab](isaac-lab.md)

## 공식 자료

- [MuJoCo Warp 저장소](https://github.com/google-deepmind/mujoco_warp)
- [배치 데이터·메모리 제한·튜닝](https://mujoco.readthedocs.io/en/latest/mjwarp/)
- [MuJoCo Warp API](https://mujoco.readthedocs.io/en/latest/mjwarp/api.html)
- [MJX 구현별 차이](https://mujoco.readthedocs.io/en/latest/mjx.html)
