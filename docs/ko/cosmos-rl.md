# Cosmos RL

[← 전체 목록](../../README.ko.md) · [English](../en/cosmos-rl.md)

AlpaGym에서 사용하는 분산 강화학습 인프라.

> **제한적 유지보수**

![Cosmos RL 워커 아키텍처](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-rl/main/assets/rl_infra.svg)

롤아웃 생성, 정책 갱신과 컨트롤러 메시지를 구분해 볼 수 있습니다. [공식 그림 출처](https://github.com/nvidia-cosmos/cosmos-rl)

## 아키텍처와 데이터 흐름

컨트롤러가 정책 워커와 롤아웃 워커를 조정합니다. 롤아웃 복제본이 경험을 생성하고 정책 복제본이 이를 학습에 사용합니다. 공식 제어 메시지에는 롤아웃, 평가와 가중치 동기화가 포함됩니다. AlpaGym은 AlpaSim 자율주행 후학습에 이 프레임워크를 사용합니다.

## 물리 AI 활용 예시

AlpaGym과 호환하는 학습기 버전을 고정한 뒤 장면 하나에서 보상, 종료 조건과 가중치 갱신을 확인합니다. 별도 경로에서 초기 정책과 학습한 정책을 비교합니다.

## 검증할 항목

공식 저장소는 제한적 유지보수 상태를 명시하고 신규 개발은 Cosmos 3 생태계를 안내합니다. 재현 가능한 실험은 버전을 고정하고 이동 시 모델별 레시피를 확인합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/nvidia-cosmos/cosmos-rl)
- [AlpaGym 연동 사례](https://github.com/NVlabs/alpagym#architecture)
- [저장소 라이선스](https://github.com/nvidia-cosmos/cosmos-rl/blob/HEAD/LICENSE)

## 관련 가이드

[Alpagym](alpagym.md) · [NeMo RL](nemo-rl.md) · [Cosmos Framework](cosmos-framework.md)
