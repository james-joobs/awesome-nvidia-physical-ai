# SimReady Central Library

[전체 목록](../../README.ko.md) · [English](../en/simready-central-library.md)

NVIDIA와 다른 소유자가 호스팅한 시뮬레이션 에셋을 검색하는 탐색 도구다.

**공식 출처:** [Hugging Face Space](https://huggingface.co/spaces/nvidia/simready-central) · [Documentation](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html)

**라이선스 및 공개 여부:** 공개 탐색 가능; 자산별 라이선스가 다르며 비상업용 자산도 포함. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

**구조:** 에셋은 소유자가 호스팅하며 승인된 등록 정보가 라이브러리 검색 인덱스에 포함된다. 에셋별 사용 조건은 각 카드에서 확인한다. [공식 문서](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html).

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["라이브러리 검색"]
  S1["에셋 카드와 조건 확인"]
  S2["소유자에게서 에셋 확보"]
  S3["통합 및 검증"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

로봇 시뮬레이션 환경에 적합한 객체와 장면을 찾는다.

## 연결 기술

SimReady Foundation, OpenUSD, Hugging Face. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
