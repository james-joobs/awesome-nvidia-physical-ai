# RTX / DGX Spark

[← 전체 목록](../../README.ko.md) · [English](../en/rtx-dgx-spark.md)

## 소개

GPU 기술·제품군 / AI 컴퓨터.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["컴퓨팅 하드웨어 선택"] --> n1
    n1["호환 소프트웨어 구성"] --> n2
    n2["AI 개발 또는 시뮬레이션 실행"]
```

## 활용 흐름과 사례

컴퓨팅 하드웨어 선택 → 호환 소프트웨어 구성 → AI 개발 또는 시뮬레이션 실행. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 시뮬레이션 또는 모델 개발 작업 실행. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** CUDA, Isaac Sim, Cosmos.

## 구성과 구체적인 활용

RTX는 GPU 제품군이고 DGX Spark는 AI 개발용 컴퓨터다. 지원 소프트웨어와 메모리·성능 특성은 모델 및 작업에 따라 다르다.

시뮬레이터나 모델 요구 사항에 맞춰 장치를 고르고 실제 작업의 메모리 사용량과 성능을 측정한다.

[공식 기술 자료](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)

## 공개 및 이용 조건

하드웨어·제품; 오픈소스 프로젝트 아님. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[RTX](https://www.nvidia.com/en-us/geforce/graphics-cards/) · [DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)
