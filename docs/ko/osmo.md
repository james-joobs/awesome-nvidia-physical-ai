# OSMO

[전체 목록](../../README.ko.md) · [English](../en/osmo.md)

GPU 기반 시뮬레이션과 학습 워크플로우를 관리하는 오케스트레이션 시스템이다.

**공식 출처:** [Repository](https://github.com/NVIDIA/OSMO)

**라이선스 및 공개 여부:** Apache-2.0. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![OSMO workflow overview](https://media.githubusercontent.com/media/NVIDIA/OSMO/main/docs/front_cover.png)

이미지 출처: [OSMO](https://github.com/NVIDIA/OSMO)

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["워크플로우와 자원 정의"]
  S1["작업 예약"]
  S2["인프라에서 실행"]
  S3["결과 수집"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

여러 단계의 로봇 시뮬레이션과 학습 작업을 관리한다.

## 연결 기술

Isaac Sim, Isaac Lab, Cosmos Data Factory. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
