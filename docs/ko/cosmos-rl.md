# Cosmos RL

[← 프로젝트 홈](../../README.ko.md) · [English](../en/cosmos-rl.md)

Cosmos-RL은 여러 GPU에 작업을 나눠 강화학습을 돌리는 프레임워크입니다. AlpaGym에서는 시뮬레이션으로 얻은 주행 기록을 바탕으로 정책을 업데이트할 때 씁니다.

> **제한적 유지보수**

![Cosmos RL 워커 아키텍처](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-rl/main/assets/rl_infra.svg)

롤아웃 생성, 정책 갱신과 컨트롤러 메시지를 구분해 볼 수 있습니다. [공식 그림 출처](https://github.com/nvidia-cosmos/cosmos-rl)

## 경험을 모으는 프로세스와 정책을 갱신하는 프로세스

### 수집과 학습을 나누는 이유

분산 강화학습에서는 롤아웃 워커가 모델을 실행해 경험을 모으고, 학습 프로세스는 그 경험과 점수로 정책 가중치를 갱신합니다. AlpaGym 경로에서 롤아웃은 AlpaSim이 만든 폐루프 주행 기록입니다. 학습 대상과 학습 알고리즘을 설정한 뒤, 경험 수집 속도와 학습 지표를 따로 확인합니다.

### 실제 설정에서 롤아웃 배치 읽기

[AlpaGym의 실제 학습 설정](https://github.com/NVlabs/alpagym/blob/972d160eed0e23d388497851504a3a233fec5879/packages/host/src/alpagym_host/conf/run/public_2507_1epoch.yaml)은 `rollout.n_generation=2`, `rollout.batch_size=1`, `train.num_epochs=1`을 지정합니다. 이 값은 각각 생성 요청 수, 롤아웃 배치 설정, 학습 에포크 수입니다. 차량 성능은 [AlpaGym의 보상과 지표](alpagym.md)에서 확인합니다. [Cosmos RL 공식 프로젝트](https://github.com/nvidia-cosmos/cosmos-rl)

## 아키텍처와 데이터 흐름

컨트롤러가 정책 워커와 롤아웃 워커를 조정합니다. 롤아웃 복제본이 경험을 생성하고 정책 복제본이 이를 학습에 사용합니다. 공식 제어 메시지에는 롤아웃, 평가와 가중치 동기화가 포함됩니다. AlpaGym은 AlpaSim 자율주행 후학습에 이 프레임워크를 사용합니다.

## 피지컬 AI 활용 예시

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
