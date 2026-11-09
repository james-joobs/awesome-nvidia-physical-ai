# Cosmos Curator

[전체 목록](../../README.ko.md) · [English](../en/cosmos-curator.md)

대규모 비디오·이미지 컬렉션의 처리와 필터링을 위한 데이터 선별 프레임워크다.

**공식 출처:** [Repository](https://github.com/NVIDIA/cosmos-curator)

**라이선스 및 공개 여부:** Apache-2.0; 모델은 별도. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![Cosmos Curator dashboard](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-dashboard.png)

이미지 출처: [Cosmos Curator](https://github.com/NVIDIA/cosmos-curator)

**구조:** 파이프라인은 단계별 병렬 워커를 이용한다. 공식 구조 문서는 영상 작업 처리, 산출물 전달과 단계별 확장 방식을 설명한다. [공식 구조 문서](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md).

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["미디어 수집"]
  S1["분할 및 처리"]
  S2["필터링과 중복 제거"]
  S3["검토 및 내보내기"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

모델 학습이나 데이터 검색 전에 영상 데이터 품질을 정리한다.

## 연결 기술

Cosmos Data Factory, Cosmos Dataset Search. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
