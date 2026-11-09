# Cosmos Evaluator

[전체 목록](../../README.ko.md) · [English](../en/cosmos-evaluator.md)

Cosmos Evaluator는 합성 영상의 여러 특성을 독립된 검사기로 평가한다. 파이프라인에서 검사기를 직접 호출하거나 오케스트레이션 서비스에 여러 검사를 함께 제출할 수 있다.

## 공식 서비스 아키텍처 읽기

![NVIDIA Cosmos Evaluator 서비스 구성도](https://raw.githubusercontent.com/NVIDIA/cosmos-evaluator/main/docs/assets/architecture_diagram.png)

Arbitrator는 가용 검사기를 파악하고 의존성 순서에 맞춰 작업을 배치한다. 클라이언트가 /process/async에 작업을 제출하면 실행 ID를 받는다. /executions/{request_id}에서 전체 실행 상태와 검사별 결과를 확인한다. 공식 구성대로 배포하면 Database REST API가 결과를 PostgreSQL에 기록한다. [공식 아키텍처](https://github.com/NVIDIA/cosmos-evaluator#architecture-diagram) · [오케스트레이션 엔드포인트](https://github.com/NVIDIA/cosmos-evaluator/blob/main/docs/services/orchestration.md)

| 검사기 | 확인하는 질문 |
|---|---|
| 환각 검사 | 원본 움직임 마스크와 비교해 움직임이 추가되거나 사라졌는가? |
| 물체 검사 | 예상한 물체가 기준 위치에 있는가? |
| 속성 검증 | 생성 장면에 요청한 속성이 나타나는가? |
| 물리적 개연성 | 선택한 모델이 봤을 때 시간에 따른 움직임이 물리적으로 자연스러운가? |

## 활용 예시 — 비 오는 도로 변형 평가

비가 나타나는지 검사하고, 원본 주행 영상과 움직임을 비교한다. 두 점수를 따로 남기고 한 검사만 통과한 사례를 검토한다. 전체 배치에 적용하기 전에 사람이 본 표본으로 임계값을 조정한다. 검사 점수는 모델이 주어진 검사 조건을 충족한다고 판단한 정도다. 실제 차량의 안전성 검증에는 별도 기준이 필요하다. [공식 검사 정의](https://github.com/NVIDIA/cosmos-evaluator#whats-included) · [CDF Augmentation](cdf-augmentation.md)

코드는 Apache-2.0이다. 검사기마다 재배포 모델 안내와 의존성 조건을 확인한다. [공식 이용 조건](https://github.com/NVIDIA/cosmos-evaluator#license-and-contributions)

## 연관 도구

모델·에이전트 벤치마크에는 [NeMo Evaluator](nemo-evaluator.md)를 사용합니다. 이 문서의 Cosmos Evaluator는 생성 영상을 검사합니다.
