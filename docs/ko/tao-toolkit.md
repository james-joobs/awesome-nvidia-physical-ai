# TAO Toolkit

[← 전체 목록](../../README.ko.md) · [English](../en/tao-toolkit.md)

## 소개

비전 AI 모델 학습·파인튜닝 도구.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["라벨 데이터 준비"] --> n1
    n1["모델 선택 및 학습"] --> n2
    n2["평가"] --> n3
    n3["배포용 내보내기"]
```

## 활용 흐름과 사례

라벨 데이터 준비 → 모델 선택 및 학습 → 평가 → 배포용 내보내기. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 탐지 모델을 새로운 환경에 맞게 조정. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Replicator, TensorRT, DeepStream.

## 구성과 구체적인 활용

TAO 참조 워크플로우는 학습·평가·추론 등의 모델 작업과 그 사이의 데이터 서비스를 연결한다. 모델 구조와 내보내기 방식은 작업에 따라 다르다.

레이블이 있는 공장 이미지로 탐지 모델을 미세조정하고 별도 평가 데이터로 검증한 뒤 배포를 준비한다.

[공식 기술 자료](https://docs.nvidia.com/tao/tao-toolkit/latest/text/reference_workflows/index.html)

## 공개 및 이용 조건

제품·SDK; 모델과 구성 요소별 조건 확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[공식 페이지](https://developer.nvidia.com/tao-toolkit)
