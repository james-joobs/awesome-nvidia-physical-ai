# OpenUSD

[← 전체 목록](../../README.ko.md) · [English](../en/openusd.md)

<p align="center">
  <img src="../../assets/project-marks/openusd.svg" width="106" alt="OpenUSD 로고"><br>
  <sub><a href="https://openusd.org/release/index.html">OpenUSD 공식 문서 로고</a></sub>
</p>

OpenUSD는 장면 기술과 합성 시스템이다. 스테이지에서 합성된 장면을 프림으로 탐색하며 각 프림의 값과 설정은 독립 파일이나 메모리 레이어에 남겨 둘 수 있다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| 레이어, 명세와 편집 대상 | 레이어는 프림과 프로퍼티의 작성 명세를 저장한다. 스테이지의 편집 대상으로 값을 저장할 레이어를 정하므로 원본 에셋을 수정하지 않고 작업 레이어에서 값을 덮어쓸 수 있다. |
| 합성 아크 | 서브레이어는 여러 레이어의 설정을 쌓는다. 참조로 내용을 특정 경로에 포함하고 페이로드는 필요할 때 로드할 콘텐츠를 표현한다. 배리언트 세트는 장비 구성처럼 이름을 붙인 대안을 노출한다. |
| 스테이지, 프림과 스키마 | 합성 스테이지가 여러 레이어의 설정을 해석해 프림과 프로퍼티를 제공한다. 적용 스키마는 물리 속성과 같은 도메인별 정보를 추가하고 호환 런타임이 이를 해석한다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    assets["참조할 로봇과 장비 에셋"]
    layer["배치·작업 오버라이드 레이어"]
    comp["USD 합성과 값 해석"]
    stage["스테이지·프림 경로·스키마"]
    app["렌더러 또는 시뮬레이션 런타임"]
    assets --> comp
    layer --> comp
    comp --> stage
    stage --> app
```

### 공식 그림과 예시

![독립 레이어가 기하와 속성을 합성 장면에 제공하는 과정.](https://docs.nvidia.com/learn-openusd/latest/_images/Layers.png)

독립 레이어가 기하와 속성을 합성 장면에 제공하는 과정. [그림 출처와 원문 설명](https://docs.nvidia.com/learn-openusd/latest/composition-basics/layers.html)

![상위 레이어가 여러 서브레이어를 포함하는 예시. 순서는 같은 속성을 여러 곳에서 작성했을 때 어떤 값이 선택되는지에 영향을 준다.](https://docs.nvidia.com/learn-openusd/latest/_images/Sublayers.png)

상위 레이어가 여러 서브레이어를 포함하는 예시. 순서는 같은 속성을 여러 곳에서 작성했을 때 어떤 값이 선택되는지에 영향을 준다. [그림 출처와 원문 설명](https://docs.nvidia.com/learn-openusd/latest/composition-basics/layers.html)

## 워크플로 예시

1. 재사용할 로봇을 /World/Robot에 참조한다. 장비 배치는 레이아웃 레이어에 두고 테스트의 센서 자세와 작업 목표는 별도 편집 레이어에 둔다.
2. 두 레이어를 합성한다. pxr.Usd나 Isaac Sim에서 최종 프림을 확인한다. 작업 레이어 값을 바꿔 어느 레이어에서 그 값이 왔는지 추적한다.
3. 무거운 환경 세부 요소를 선택적으로 불러와야 하면 페이로드를 쓴다. 다른 컴퓨터에서도 장면이 열리도록 텍스처 등의 의존성을 패키징하거나 경로를 설정한다.

## 검증 포인트

- 시뮬레이터로 넘기기 전 미해결 경로, 위 방향 축, metersPerUnit, 프림 경로와 합성 결과를 확인한다.
- 작업에 쓴 적용 스키마를 런타임이 지원하는지 확인한다. OpenUSD는 런타임이 사용할 콘텐츠를 기술한다.

## 라이선스와 범위

Pixar 구현은 수정된 BSD 계열 라이선스다. 에셋, 명세, 상표 조건은 별도다.

## 관련 가이드

[SimReady](simready.md) · [Omniverse](omniverse.md) · [Isaac Sim](isaac-sim.md)

## 공식 자료

- [Pixar OpenUSD 소개](https://openusd.org/release/intro.html)
- [레이어 작성과 순서](https://docs.nvidia.com/learn-openusd/latest/composition-basics/layers.html)
- [합성 아크](https://docs.nvidia.com/learn-openusd/latest/creating-composition-arcs/index.html)
- [OpenUSD 소스](https://github.com/PixarAnimationStudios/OpenUSD)
