# OpenUSD

[← 전체 목록](../../README.ko.md) · [English](../en/openusd.md) · [공식 소스](https://github.com/PixarAnimationStudios/OpenUSD) · [공식 문서](https://openusd.org/release/intro.html)

복잡한 3D 장면과 에셋을 기술·합성·교환하기 위한 프레임워크입니다.

**라이선스:** 구현체는 수정 BSD 계열 라이선스; 표준과 상표는 별도. 사용 전에 해당 버전과 에셋·모델·의존성의 조건을 확인하세요.



## 구성과 아키텍처

스테이지는 합성된 장면 그래프를 나타냅니다. 레이어와 합성 기능을 통해 각 기여를 모두 평탄화하지 않고도 장면 데이터를 조립하고 수정할 수 있습니다.

```mermaid
flowchart LR
    A["에셋과 레이어"] --> B["합성"] --> C["USD 스테이지"] --> D["호환 애플리케이션"]
```

*이 안내서에서 만든 개념적 흐름도입니다. 실제 구현은 공식 문서를 확인하세요.*

## 활용 흐름

재사용할 에셋과 레이어를 작성하고 참조와 오버라이드를 합성해 스테이지를 만든 후 호환 애플리케이션과 장면을 교환합니다.

## 활용 사례

재사용 가능한 로봇·공장 에셋 구성, 3D 도구 간 장면 교환, 시뮬레이션 환경 조립에 활용할 수 있습니다.

## 연계 기술

SimReady는 시뮬레이션용 에셋의 규약을 제공하며 Omniverse와 Isaac Sim은 OpenUSD 기반 장면을 활용합니다. USD는 장면을 기술하며 자체 물리 솔버는 아닙니다.

## 공식 자료

- [프로젝트 저장소](https://github.com/PixarAnimationStudios/OpenUSD)
- [공식 문서](https://openusd.org/release/intro.html)
