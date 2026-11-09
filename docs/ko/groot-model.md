# Isaac GR00T / GR00T N1.7

[← 전체 목록](../../README.ko.md) · [English](../en/groot-model.md)

## 소개

로봇 행동 기반 모델·플랫폼.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["시연 데이터 준비"] --> n1
    n1["모델과 로봇 형태 선택"] --> n2
    n2["정책 학습·적응"] --> n3
    n3["평가 및 배포"]
```

## 활용 흐름과 사례

시연 데이터 준비 → 모델과 로봇 형태 선택 → 정책 학습·적응 → 평가 및 배포. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 로봇 정책을 특정 작업에 맞게 적응. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac Capture, Isaac Lab, Isaac GR00T code.

## 구성과 실제 활용

GR00T N1.7은 언어와 이미지 관측, 로봇별 설정을 바탕으로 행동을 예측하는 비전·언어·행동 모델입니다. 공식 흐름은 시연 데이터 준비, 추론 또는 미세조정, 시뮬레이션·하드웨어 평가, 정책과 제어기 연결 순서입니다. 정확한 체크포인트별 이용 조건을 확인하세요.

[공식 문서](https://github.com/NVIDIA/Isaac-GR00T)

![GR00T model architecture](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

*이미지 출처: [Official repository](https://github.com/NVIDIA/Isaac-GR00T)*

## 공개 및 이용 조건

코드와 가중치의 라이선스 별도; 모델 이용 조건은 버전별 확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[공식 저장소](https://github.com/NVIDIA/Isaac-GR00T)
