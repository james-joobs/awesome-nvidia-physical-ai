# NeMo Gym

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-gym.md)

도구를 사용하는 에이전트의 롤아웃 환경과 검증기.

![NeMo Gym 환경 개요](https://raw.githubusercontent.com/NVIDIA-NeMo/Gym/main/fern/assets/images/product_overview.png)

에이전트, 리소스와 모델 서비스가 롤아웃에 참여하는 방식을 보여 줍니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/Gym)

## 아키텍처와 데이터 흐름

모델 서버가 생성을 제공하고 에이전트 서버가 상호작용 루프를 제어합니다. 리소스 서버는 작업 도구와 검증기를 제공합니다. 롤아웃에는 모델·도구 상호작용이 기록되어 평가와 학습에 사용됩니다. NeMo RL에 환경 통합이 문서화되어 있습니다.

## 물리 AI 활용 예시

읽기 전용 클립 메타데이터 도구가 있는 오프라인 사고 분류 과제를 만듭니다. 에이전트가 기대한 이벤트 ID를 인용하고 허용된 호출만 하는지 검증합니다. 후학습 전에 같은 과제로 반복 평가합니다.

## 검증할 항목

과제 데이터와 도구 스키마, 검증기 버전을 고정하고 환경·데이터셋별 조건을 확인합니다. 로봇 물리와 제어는 시뮬레이터 또는 로봇 스택에서 실행합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/Gym)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/Gym/blob/HEAD/LICENSE)

## 관련 가이드

[NeMo RL](nemo-rl.md) · [Isaac Lab](isaac-lab.md)
