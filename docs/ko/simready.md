# SimReady

[전체 목록](../../README.ko.md) · [English](../en/simready.md)

SimReady는 물리 기반 시뮬레이션에 활용할 수 있도록 준비된 3D 에셋의 명세와 작업 방식을 설명한다. 에셋은 형상과 외관 외에 충돌, 물리 재질, 의미 정보 등을 포함할 수 있으며 요구 사항은 선택한 에셋 프로파일에 따라 다르다. 단일 라이브러리가 아니라 명세와 관련 도구·에셋으로 이루어진 생태계다.

**공식 자료:** [SimReady 개요](https://docs.omniverse.nvidia.com/simready/latest/index.html) · [SimReady Central](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html) · [SimReady Foundation](https://github.com/NVIDIA/simready-foundation)

**접근과 라이선스:** 명세, 코드, 개별 에셋에는 서로 다른 조건이 적용된다. NVIDIA가 작성한 Foundation 콘텐츠는 Apache-2.0이지만 제3자 에셋에는 비상업적 사용 제한 등 별도 조건이 있을 수 있다. 사용 전 에셋 카드와 실제 파일의 조건을 확인한다.

![SimReady 객체 예시](https://media.githubusercontent.com/media/NVIDIA/simready-foundation/main/nv_core/cip_specs/isaac_asset_transformer/tests/fixtures/prop_physx_toolbox/simready_usd/.thumbs/sm_obs_electricians_large_tool_box_a01_01_thumbnail.png)

이미지 출처: [NVIDIA SimReady Foundation](https://github.com/NVIDIA/simready-foundation).

## 구성과 워크플로우

[SimReady Foundation](simready-foundation.md)은 에셋 프로파일, 명세와 검증 도구를 제공한다. [SimReady Central Library](simready-central-library.md)는 등록된 에셋을 검색할 수 있게 하며 에셋 소유자가 패키지를 호스팅한다. OpenUSD를 이용해 장면을 기술하고 조합한다.

다음은 이해를 돕는 개념적 흐름이며, 구체적인 검증 절차는 에셋 프로파일에 따라 다르다.

```mermaid
flowchart LR
  A["3D 에셋 검색 또는 제작"] --> B["시뮬레이션 속성 추가"] --> C["프로파일 기준 검증"] --> D["OpenUSD 장면 구성"] --> E["시뮬레이션 및 평가"]
```

## 활용 사례

창고 로봇 환경을 만들 때 선반·팔레트·장비 에셋을 선택하고, 라이선스와 물리 속성을 확인한 다음 Isaac Sim 장면에 조합할 수 있다. 시험이나 합성 데이터 생성에 사용하기 전에 충돌과 센서 동작을 검증한다.

## 연결 기술

OpenUSD, Isaac Sim, Omniverse, SimReady Foundation, SimReady Central Library. 각 프로젝트와 에셋의 실행 요건과 이용 조건은 별도로 확인한다.
