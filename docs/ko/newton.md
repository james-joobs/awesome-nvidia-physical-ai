# Newton

[← 전체 목록](../../README.ko.md) · [English](../en/newton.md) · [공식 소스](https://github.com/newton-physics/newton) · [공식 문서](https://newton-physics.github.io/newton/stable/faq.html)

NVIDIA Warp 위에 구축된 로봇용 확장형 GPU 가속 물리 엔진입니다. Disney Research, Google DeepMind, NVIDIA 등이 참여하는 커뮤니티 프로젝트입니다.

**라이선스:** Apache-2.0. 사용 전에 해당 버전과 에셋·모델·의존성의 조건을 확인하세요.

![Newton official example](https://raw.githubusercontent.com/newton-physics/newton/main/docs/images/examples/example_basic_urdf.jpg)

*이미지 출처: [공식 프로젝트 저장소](https://github.com/newton-physics/newton). 저작자 표시 및 재사용 조건은 원본을 확인하세요.*

## 구성과 아키텍처

모델, 시뮬레이션 상태, 솔버, 에셋 가져오기 기능을 분리합니다. URDF·MJCF·OpenUSD와 여러 솔버를 지원하며, 기능과 미분 가능 여부는 솔버마다 다릅니다.

```mermaid
flowchart LR
    A["로봇 모델과 에셋"] --> B["Newton 모델·상태"] --> C["솔버"] --> D["시뮬레이션 궤적"]
```

*이 안내서에서 만든 개념적 흐름도입니다. 실제 구현은 공식 문서를 확인하세요.*

## 활용 흐름

로봇과 장면 에셋을 가져와 모델과 상태를 구성하고 솔버를 선택합니다. 시뮬레이션을 진행한 뒤 궤적을 살펴보거나 학습에 활용합니다.

## 활용 사례

이동·조작 정책 학습, 접촉이 많은 로봇 시뮬레이션 시제품 제작, 솔버 동작 비교에 활용할 수 있습니다.

## 연계 기술

Warp가 커널 기반을 제공하고 MuJoCo Warp는 주요 솔버입니다. Isaac Lab 연동은 실험적이며 지원 범위는 버전별로 확인해야 합니다.

## 공식 자료

- [프로젝트 저장소](https://github.com/newton-physics/newton)
- [공식 문서](https://newton-physics.github.io/newton/stable/faq.html)
