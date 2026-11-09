# Cosmos Predict2 code

[전체 목록](../../README.ko.md) · [English](../en/cosmos-predict2.md)

월드 및 영상 생성 모델의 추론과 학습 코드다.

**공식 출처:** [Repository](https://github.com/nvidia-cosmos/cosmos-predict2)

**라이선스:** Apache-2.0 code; model weights separately licensed.

## 워크플로우

이해를 돕기 위한 개념도다.

```mermaid
flowchart LR
  S0["조건 입력 준비"]
  S1["모델 로드"]
  S2["영상 생성"]
  S3["결과 평가"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

피지컬 AI 연구용 시각 시나리오를 생성하고 평가한다.

## 연결 기술

Cosmos, Cosmos Evaluator.
