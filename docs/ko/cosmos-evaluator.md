# Cosmos Evaluator

[전체 목록](../../README.ko.md) · [English](../en/cosmos-evaluator.md)

물리적 타당성과 시각적 충실도 등의 검사를 통해 생성 영상을 평가하는 프레임워크다.

**공식 출처:** [Repository](https://github.com/NVIDIA/cosmos-evaluator)

**라이선스 및 공개 여부:** Apache-2.0; 체커별 모델 조건 별도. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![Cosmos Evaluator architecture diagram](https://raw.githubusercontent.com/NVIDIA/cosmos-evaluator/main/docs/assets/architecture_diagram.png)

이미지 출처: [Cosmos Evaluator](https://github.com/NVIDIA/cosmos-evaluator)

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["생성 영상과 기준 선택"]
  S1["적합한 검사기 실행"]
  S2["결과 검토"]
  S3["데이터 개선"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

합성 주행·조작 영상을 학습 데이터에 추가하기 전에 품질을 선별한다.

## 연결 기술

Cosmos Data Factory, Cosmos generation models. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
