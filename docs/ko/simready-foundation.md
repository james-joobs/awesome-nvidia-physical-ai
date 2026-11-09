# SimReady Foundation

[전체 목록](../../README.ko.md) · [English](../en/simready-foundation.md)

OpenUSD 에셋 프로파일, 명세, 검증 도구와 샘플 콘텐츠를 제공한다.

**공식 출처:** [GitHub](https://github.com/NVIDIA/simready-foundation)

**라이선스 및 공개 여부:** NVIDIA 작성 콘텐츠 Apache-2.0; 제3자 자산은 별도 라이선스. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![SimReady sample object](https://media.githubusercontent.com/media/NVIDIA/simready-foundation/main/nv_core/cip_specs/isaac_asset_transformer/tests/fixtures/prop_physx_toolbox/simready_usd/.thumbs/sm_obs_electricians_large_tool_box_a01_01_thumbnail.png)

이미지 출처: [SimReady Foundation](https://github.com/NVIDIA/simready-foundation)

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["에셋 프로파일 선택"]
  S1["에셋 작성 또는 가져오기"]
  S2["필수 속성 검증"]
  S3["시뮬레이션 장면에 사용"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

시뮬레이션에 필요한 물리·의미 속성을 갖춘 재사용 객체를 준비한다.

## 연결 기술

SimReady, OpenUSD, Isaac Sim, SimReady Central. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
