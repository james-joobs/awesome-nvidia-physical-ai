# CDF Orchestration

[← 전체 목록](../../README.ko.md) · [English](../en/cdf-orchestration.md)

![CDF Orchestration official example](https://raw.githubusercontent.com/NVIDIA/cdf-orchestration/main/docs/assets/architecture_diagram.png)

이미지: 아래 공식 프로젝트 출처.

## 소개

데이터 팩토리 작업 실행·관리 구성 요소.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["데이터 워크플로 정의"] --> n1
    n1["처리 작업 스케줄링"] --> n2
    n2["실행 모니터링"] --> n3
    n3["결과 확인"]
```

## 활용 흐름과 사례

데이터 워크플로 정의 → 처리 작업 스케줄링 → 실행 모니터링 → 결과 확인. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 영상 처리 워크플로 관리. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Cosmos Data Factory, OSMO.

## 구성과 구체적인 활용

Airflow DAG와 플러그인을 컨트롤러 이미지로 묶고 Kubernetes에 워크플로우 작업과 GPU 추론 서비스를 배포한다. 일부 공식 워크플로우는 OSMO도 지원한다.

영상 증강 DAG를 실행해 조명·날씨를 다양하게 바꾸고 관련 주석을 생성한다.

[공식 기술 자료](https://github.com/NVIDIA/cdf-orchestration)

## 공개 및 이용 조건

저장소는 Apache-2.0을 명시하며 실행 서비스와 의존성에는 별도 조건이 적용될 수 있다. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[저장소](https://github.com/NVIDIA/cdf-orchestration)
