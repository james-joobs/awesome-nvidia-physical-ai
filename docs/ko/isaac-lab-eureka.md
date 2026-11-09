# Isaac Lab Eureka

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-lab-eureka.md)

Isaac Lab Eureka는 Eureka 연구 방식을 Isaac Lab 작업에 적용한 구현이다. 언어 모델이 실행 가능한 보상 함수를 제안하고 강화학습 러너가 후보별 정책을 학습한 뒤, 별도 작업 지표로 결과 정책의 순위를 정한다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| 작업 설정 | 이 구현은 DirectRLEnv 작업을 대상으로 관측 구현을 사용한다. 지원 작업마다 후보 평가에 쓸 성공 지표를 정의한다. |
| 보상 후보 제안과 피드백 | 언어 모델이 작업 맥락에서 보상 코드를 생성한다. 학습을 시도해 피드백과 지표 또는 실행 오류를 얻고 반복 로그에 남긴다. |
| 학습과 재생 | RSL RL 또는 RL-Games가 유효한 후보를 학습한다. Eureka는 반복 요약과 RL 체크포인트를 따로 저장하고 scripts/play.py에서 체크포인트를 재생한다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    task["작업 관측과 성공 지표"]
    llm["언어 모델 보상 코드 후보"]
    rl["Isaac Lab 정책 학습"]
    rank["별도 성공 지표와 로그"]
    ckpt["선택 정책 체크포인트"]
    task --> llm
    task --> rank
    llm --> rl
    rl --> rank
    rank --> llm
    rank --> ckpt
```

### 공식 그림과 예시

![원래 Eureka 연구의 카트폴 이미지. Isaac Lab 이식 구현에는 별도 카트폴 작업과 체크포인트가 있다.](https://eureka-research.github.io/videos/task_final/cartpole.png)

원래 Eureka 연구의 카트폴 이미지. Isaac Lab 이식 구현에는 별도 카트폴 작업과 체크포인트가 있다. [그림 출처와 원문 설명](https://eureka-research.github.io/)

## 워크플로 예시

1. 문서의 Isaac-Cartpole-Direct-v0 예제부터 시작한다. 수작업 보상 기준선과 균형 유지 시간 같은 별도 평가 지표를 정한다.
2. 같은 학습 예산으로 보상 후보를 시험한다. Eureka 로그에서 원본 제안과 피드백을 읽고 저장된 체크포인트로 후보 정책을 비교한다.
3. 선택 정책을 새로운 초기 각도와 속도에서 재생한다. 다른 작업에 쓰기 전에 생성 보상 함수를 검토한다.

## 검증 포인트

- 학습 보상과 성공 지표를 분리해 기록한다. 정책이 대리 지표를 최적화하면서 의도한 행동을 놓칠 수 있다.
- 저장소에 지원 직접 구현 작업과 RL 라이브러리가 명시돼 있다. 생성 코드가 실행에 실패하거나 겉보기 점수만 높을 수 있어 코드와 롤아웃을 점검한다.

## 라이선스와 범위

공개 저장소 README에 MIT 배지가 있다. 이 이식 구현에 적용되는 독립 라이선스 파일은 확인하지 못했다. 논문의 원래 구현은 별도 프로젝트다.

## 관련 가이드

[Isaac Lab](isaac-lab.md) · [Isaac RLPT](isaac-rlpt.md)

## 공식 자료

- [Isaac Lab 이식 구현과 작업 예제](https://github.com/NVlabs/IsaacLabEureka)
- [지원 작업 설정과 성공 지표](https://github.com/NVlabs/IsaacLabEureka/blob/main/source/isaaclab_eureka/isaaclab_eureka/config/tasks.py)
- [원래 Eureka 논문과 실험](https://eureka-research.github.io/)
