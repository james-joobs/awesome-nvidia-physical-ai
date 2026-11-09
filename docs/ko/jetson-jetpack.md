# Jetson / JetPack

[← 전체 목록](../../README.ko.md) · [English](../en/jetson-jetpack.md)

## 소개

엣지 AI 하드웨어 / 소프트웨어 개발 키트.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["Jetson 하드웨어 선택"] --> n1
    n1["JetPack 설치"] --> n2
    n2["모델 최적화"] --> n3
    n3["엣지 추론 실행"]
```

## 활용 흐름과 사례

Jetson 하드웨어 선택 → JetPack 설치 → 모델 최적화 → 엣지 추론 실행. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 엣지 장치에서 로봇 인식 실행. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** TensorRT, Isaac ROS, DeepStream.

## 구성과 구체적인 활용

Jetson은 임베디드 컴퓨팅 하드웨어 제품군이다. JetPack은 Jetson Linux와 호환되는 CUDA·TensorRT 등을 제공하며 지원 범위는 하드웨어와 배포 버전에 따라 다르다.

지원되는 Jetson 모듈에 로봇 카메라 인식 파이프라인을 배포하고 실제 장치에서 지연 시간을 측정한다.

[공식 기술 자료](https://developer.nvidia.com/embedded/jetpack/downloads)

## 공개 및 이용 조건

제품·배포판; 개별 구성 요소의 조건 상이. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[Jetson](https://developer.nvidia.com/embedded/jetson-modules) · [JetPack](https://developer.nvidia.com/embedded/jetpack)
