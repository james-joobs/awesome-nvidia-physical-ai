# CDF Augmentation (formerly paidf-augmentation)

[전체 목록](../../README.ko.md) · [English](../en/cdf-augmentation.md)

모델 기반 워크플로우로 기존 데이터의 영상·이미지·텍스트 변형을 생성한다.

**공식 출처:** [Repository](https://github.com/NVIDIA/cdf-augmentation)

**라이선스 및 공개 여부:** Apache-2.0; models have separate terms. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![CDF Augmentation (formerly paidf-augmentation) official example](https://raw.githubusercontent.com/NVIDIA/cdf-augmentation/main/docs/Augmentation_v1.1.0.png)

이미지 출처: [CDF Augmentation (formerly paidf-augmentation)](https://github.com/NVIDIA/cdf-augmentation)

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["입력 준비"]
  S1["변형 및 모델 선택"]
  S2["변형 생성"]
  S3["일관성 검토"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

새 사례 수집이 어려운 날씨·조명·외형 조건의 다양성을 늘린다.

## 연결 기술

Cosmos Data Factory, Cosmos models, Cosmos Evaluator. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
