# SimReady Central

[전체 목록](../../README.ko.md) · [English](../en/simready-central.md)

소유자가 Hugging Face에 호스팅한 시뮬레이션 에셋 패키지의 제출·검토 인덱스다.

**공식 출처:** [GitHub](https://github.com/NVIDIA-Omniverse/simready-central)

**라이선스 및 공개 여부:** 저장소 공개; 제출을 위한 온보딩과 자산 이용 조건은 별도. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["소유자 호스팅 패키지 준비"]
  S1["등록 제출"]
  S2["검토"]
  S3["승인된 에셋을 라이브러리에서 검색"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

원본 호스팅과 라이선스를 유지하면서 에셋을 검색 가능하게 만든다.

## 연결 기술

SimReady Central Library, Hugging Face, OpenUSD. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
