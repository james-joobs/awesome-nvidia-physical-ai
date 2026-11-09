# Cosmos Reason2 code

[전체 목록](../../README.ko.md) · [English](../en/cosmos-reason2.md)

시각 입력을 이해하는 월드 추론 모델을 학습하고 실행하는 코드다.

**공식 출처:** [Repository](https://github.com/nvidia-cosmos/cosmos-reason2)

**라이선스:** Apache-2.0 code; model weights separately licensed.

## 워크플로우

이해를 돕기 위한 개념도다.

```mermaid
flowchart LR
  S0["영상·이미지와 프롬프트 준비"]
  S1["모델 로드"]
  S2["추론 실행"]
  S3["결과 평가"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

영상 속 물리적 사건과 시각적 추론을 연구한다.

## 연결 기술

Cosmos, Cosmos datasets.
