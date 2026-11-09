# SkillGen / SkillMimicGen

[← 전체 목록](../../README.ko.md) · [English](../en/skillgen.md)

## 소개

동작계획으로 시연 구간을 연결·생성하는 방법.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["시연을 스킬 단위로 나눔"] --> n1
    n1["동작계획으로 구간 연결"] --> n2
    n2["시연 데이터 생성 및 검증"]
```

## 활용 흐름과 사례

시연을 스킬 단위로 나눔 → 동작계획으로 구간 연결 → 시연 데이터 생성 및 검증. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 작업 구간을 새로운 배치로 연결. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac Lab, cuRobo.

## 구성과 실제 활용

SkillGen은 하위 작업 구간의 시작과 끝을 수동으로 표시해야 합니다. 목표를 샘플링하고 cuRobo로 변환된 기술 구간 사이의 이동을 계획한 뒤 궤적을 연결하고 작업 성공을 확인합니다. 예를 들어 물체 위치를 바꾼 큐브 쌓기 시연을 생성하면서 계획 실패를 검토할 수 있습니다.

[공식 문서](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/features/imitation-learning/skillgen.html)

## 공개 및 이용 조건

Isaac Lab 구현과 cuRobo 등 의존성의 조건을 각각 확인; 논문명과 구현명은 구분. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[Isaac Lab 구현 문서](https://github.com/isaac-sim/IsaacLab/blob/main/docs/source/features/imitation-learning/skillgen.rst)
