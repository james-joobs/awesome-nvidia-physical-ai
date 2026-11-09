# NeMo RL

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-rl.md)

지원 LLM·VLM의 분산 지도 미세조정과 강화학습.

![NeMo RL 아키텍처](https://raw.githubusercontent.com/NVIDIA-NeMo/RL/main/docs/assets/RL_diagram.png)

분산 런타임이 롤아웃과 학습 책임을 연결하는 구조를 보여 줍니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/RL)

## 아키텍처와 데이터 흐름

롤아웃 워커가 응답 후보를 생성하고 환경 또는 채점 함수가 보상을 반환하면 학습 워커가 정책을 갱신합니다. Ray가 워커를 조정합니다. 레시피에 따라 AutoModel DTensor 또는 Megatron Bridge 경로를 사용하며, 저장소는 VLM의 SFT와 GRPO를 지원합니다.

## 물리 AI 활용 예시

작업 셀 이미지 질문 세트를 만들고 실제 이벤트 라벨 또는 허용된 구조화 값으로 응답을 채점합니다. 분리한 장면에서 학습 전후 모델을 비교합니다. 자율주행 롤아웃은 해당되는 경우 AlpaGym과 Cosmos RL의 별도 구성을 참고합니다.

## 검증할 항목

사람 라벨과 보상을 비교하고 보상이 높아졌을 때 실제 작업 정확도도 개선됐는지 확인합니다. 레시피별 모델과 백엔드 조건을 따릅니다. 실제 로봇 제어 성능은 별도로 평가합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/RL)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/RL/blob/HEAD/LICENSE)

## 관련 가이드

[NeMo Gym](nemo-gym.md) · [Cosmos RL](cosmos-rl.md) · [Alpagym](alpagym.md)
