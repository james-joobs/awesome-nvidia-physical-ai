# Isaac GR00T 코드
[← 목록으로](../../README.ko.md) · [English](../en/isaac-gr00t.md)

GR00T 로봇 정책의 학습·추론·배포 코드.

**공식 자료:** [저장소](https://github.com/NVIDIA/Isaac-GR00T)  
**라이선스와 범위:** 코드 Apache-2.0; 모델과 가중치는 별도 조건.

![Isaac GR00T robot demonstration](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/header_compress.png)
*이미지 출처: [Repository](https://github.com/NVIDIA/Isaac-GR00T)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**로봇 시연과 로봇 구성 → 정책 학습·미세조정 → 행동 추론 → 평가·배포**

## 주요 구성과 공식 아키텍처

![GR00T 모델 아키텍처](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

*이미지 출처: [Official repository](https://github.com/NVIDIA/Isaac-GR00T)*

저장소는 정책 학습·추론 코드와 모델별 설정을 제공합니다. 로봇 관측과 언어 지시를 처리해 행동을 예측하며, 정확한 입력·출력과 설정은 모델 버전 및 로봇 인터페이스에 따라 달라집니다. 모델 가중치 약관을 코드와 별도로 확인하세요.

## 활용 사례

적합한 시연 데이터를 사용해 범용 로봇 정책을 조작 작업에 맞춥니다.

## 연결 기술

Isaac Capture, Isaac Lab, LeRobot.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
