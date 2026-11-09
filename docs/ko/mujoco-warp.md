# MuJoCo Warp (MJWarp)

[← 전체 목록](../../README.ko.md) · [English](../en/mujoco-warp.md) · [공식 소스](https://github.com/google-deepmind/mujoco_warp) · [공식 문서](https://github.com/google-deepmind/mujoco/blob/main/doc/mjx.rst)

Warp로 구현한 NVIDIA GPU 최적화 MuJoCo 물리 시뮬레이션 구현체로 Google DeepMind와 NVIDIA가 개발합니다.

**라이선스:** Apache-2.0; 의존성은 별도 조건 적용. 사용 전에 해당 버전과 에셋·모델·의존성의 조건을 확인하세요.

![MuJoCo Warp (MJWarp) official example](https://raw.githubusercontent.com/google-deepmind/mujoco_warp/main/benchmarks/unitree_g1/rollout_flat.webp)

*이미지 출처: [공식 프로젝트 저장소](https://github.com/google-deepmind/mujoco_warp). 저작자 표시 및 재사용 조건은 원본을 확인하세요.*

## 구성과 아키텍처

NVIDIA GPU에서 MuJoCo 물리를 구현하며 MJX를 통해 사용할 수도 있습니다. 지원 기능과 설정은 프로젝트 문서를 확인해야 합니다.

```mermaid
flowchart LR
    A["MuJoCo 모델"] --> B["Warp GPU 시뮬레이션"] --> C["병렬 상태·관측값"] --> D["정책 학습"]
```

*이 안내서에서 만든 개념적 흐름도입니다. 실제 구현은 공식 문서를 확인하세요.*

## 활용 흐름

MuJoCo 모델을 불러와 모델과 시뮬레이션 데이터를 GPU에 올립니다. 여러 환경을 진행하고 상태나 렌더링 관측값을 학습 루프에 전달합니다.

## 활용 사례

병렬 로봇 보행·조작 학습, 접촉이 많은 시뮬레이션, 시각 정책 실험에 활용할 수 있습니다.

## 연계 기술

Newton은 MuJoCo Warp를 솔버로 사용할 수 있고 Warp는 GPU 프로그래밍 기반을 제공합니다. 현재 MJX-Warp는 자동 미분을 지원하지 않으므로 배포 버전의 문서를 확인해야 합니다.

## 공식 자료

- [프로젝트 저장소](https://github.com/google-deepmind/mujoco_warp)
- [공식 문서](https://github.com/google-deepmind/mujoco/blob/main/doc/mjx.rst)
