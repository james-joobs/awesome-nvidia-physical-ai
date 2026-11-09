# DexMimicGen

[← 전체 목록](../../README.ko.md) · [English](../en/dexmimicgen.md)

## 소개

양손·다중 조작 시연 데이터 생성 연구.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["다중 로봇팔 시연 수집"] --> n1
    n1["변형 생성"] --> n2
    n2["정교한 조작 궤적 검증"] --> n3
    n3["모방학습에 활용"]
```

## 활용 흐름과 사례

다중 로봇팔 시연 수집 → 변형 생성 → 정교한 조작 궤적 검증 → 모방학습에 활용. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 양팔 조작 시연 생성. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** MimicGen, Isaac Lab.

## 구성과 실제 활용

공식 배포는 양손 정교 조작을 다루는 DexMimicGen 연구의 시뮬레이션 환경과 데이터셋을 제공합니다. 문서화된 흐름은 robosuite 환경과 robomimic 학습 설정 생성을 사용하며 코드와 데이터셋 약관이 다릅니다.

[공식 문서](https://github.com/NVlabs/dexmimicgen)

## 공개 및 이용 조건

코드 NVIDIA Source Code License; 데이터 CC-BY-4.0, 코드 이용 제한 확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[저장소](https://github.com/NVlabs/dexmimicgen)
