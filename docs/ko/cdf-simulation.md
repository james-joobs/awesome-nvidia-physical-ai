# CDF Simulation (formerly paidf-simulation)

[전체 목록](../../README.ko.md) · [English](../en/cdf-simulation.md)

Isaac Sim과 Replicator를 사용해 주석이 있는 합성 이미지를 렌더링하는 워크플로우다.

**공식 출처:** [Repository](https://github.com/NVIDIA/cdf-simulation)

**라이선스 및 공개 여부:** Apache-2.0; simulator and assets have separate terms. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![CDF Simulation (formerly paidf-simulation) official example](https://raw.githubusercontent.com/NVIDIA/cdf-simulation/main/docs/images/defect_closeups_ict.jpg)

이미지 출처: [CDF Simulation (formerly paidf-simulation)](https://github.com/NVIDIA/cdf-simulation)

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["장면과 에셋 구성"]
  S1["시뮬레이션 조건 변경"]
  S2["센서 이미지와 레이블 렌더링"]
  S3["결과 검증"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

실제 레이블 데이터가 부족할 때 가상 물체를 이용해 검사 데이터를 생성한다.

## 연결 기술

Isaac Sim, Replicator, SimReady, Cosmos Data Factory. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
