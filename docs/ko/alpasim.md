# AlpaSim

[전체 목록](../../README.ko.md) · [English](../en/alpasim.md)

정책을 폐루프에서 시험하는 모듈형 자율주행 시뮬레이터다.

**공식 출처:** [Repository](https://github.com/NVlabs/alpasim)

**라이선스 및 공개 여부:** Apache-2.0 코드; 모델·데이터 별도. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

![AlpaSim driving simulation](https://raw.githubusercontent.com/NVlabs/alpasim/main/docs/assets/images/thumbnail.gif)

이미지 출처: [AlpaSim](https://github.com/NVlabs/alpasim)

**구조:** 주행 정책은 시뮬레이션 관측값을 받고 궤적을 반환한다. 시뮬레이터는 차량을 전진시키고 다음 관측값을 제공한다. 모듈형 서비스와 인터페이스는 [공식 설계 문서](https://github.com/NVlabs/alpasim/blob/main/docs/DESIGN.md)를 참고한다.

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["장면과 주행 정책 선택"]
  S1["센서와 차량 움직임 시뮬레이션"]
  S2["관측값 재입력"]
  S3["주행 결과 평가"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

자율주행 정책을 비교하고 어려운 시나리오를 시험한다.

## 연결 기술

Alpamayo, AlpaGym, NuRec. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
