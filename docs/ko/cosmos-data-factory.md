# Cosmos Data Factory (CDF; formerly Physical AI Data Factory)

[전체 목록](../../README.ko.md) · [English](../en/cosmos-data-factory.md)

피지컬 AI 학습 데이터를 선별·레이블링·증강·생성하는 조합 가능한 워크플로우와 스킬 모음이다.

**공식 출처:** [Repository](https://github.com/NVIDIA/cosmos-data-factory)

**라이선스 및 공개 여부:** Code: Apache-2.0; documentation and skills: CC-BY-4.0; models and services have separate terms. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

**구성 요소:** 참조 블루프린트는 선별·레이블링·증강·시뮬레이션·평가 구성 요소를 조합한다. CDF Orchestration은 참조 블루프린트를 Airflow DAG로 실행하며 백엔드는 블루프린트에 따라 다르다. [공식 개요](https://github.com/NVIDIA/cosmos-data-factory).

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["원본 데이터 수집"]
  S1["선별·레이블링"]
  S2["증강 또는 시뮬레이션"]
  S3["평가"]
  S4["내보내기"]
  S0 --> S1 --> S2 --> S3 --> S4
```

## 활용 사례

제한된 원본으로 다양한 주행 영상, 희귀 이벤트 영상, 결함 검사 데이터를 생성한다.

## 연결 기술

CDF Auto Labeling, CDF Augmentation, CDF Simulation, Cosmos Curator, Cosmos Evaluator, OSMO. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
