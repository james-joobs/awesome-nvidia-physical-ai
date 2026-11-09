# AlpaGym

[전체 목록](../../README.ko.md) · [English](../en/alpagym.md)

자율주행 정책 개발을 위한 강화학습 도구다.

**공식 출처:** [Repository](https://github.com/NVlabs/alpagym)

**라이선스 및 공개 여부:** Apache-2.0 코드; 의존성·모델 별도. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

**구조:** 호스트가 설정을 준비하고 실행을 시작한다. 런타임은 AlpaSim 에피소드를 실행하고 점수를 매기며, Cosmos-RL은 결과를 사용해 정책을 학습한다. [공식 구조 설명](https://github.com/NVlabs/alpagym#architecture).

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["주행 과제와 정책 설정"]
  S1["시뮬레이션 경험 수집"]
  S2["정책 최적화"]
  S3["평가"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

시뮬레이션 강화학습으로 주행 정책을 개선한다.

## 연결 기술

AlpaSim, autonomous-driving models. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
