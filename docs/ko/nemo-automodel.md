# NeMo AutoModel

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-automodel.md)

지원 언어·멀티모달 모델의 PyTorch 기반 분산 학습.

![AutoModel 구성 개요](https://raw.githubusercontent.com/NVIDIA-NeMo/Automodel/main/docs/automodel_diagram.png)

지원 모델과 학습·분산 실행 계층의 관계를 보여 주는 공식 개요입니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/Automodel)

## 아키텍처와 데이터 흐름

학습 레시피는 지원 Hugging Face 모델과 프로세서를 데이터셋, 손실, 학습 루프에 연결합니다. PyTorch DeviceMesh와 DTensor는 모델·옵티마이저 상태를 장치에 나누는 방식을 표현합니다. 학습 설정에서 지원 병렬화와 체크포인트 형식을 선택합니다.

## 물리 AI 활용 예시

로봇 작업 셀에서 검증한 이미지·질문·답변으로 지원 VLM을 적응시킵니다. 작은 데이터로 영상 디코딩과 정답 토큰 마스킹을 확인한 뒤 장치를 늘립니다. 체크포인트를 내보내 별도 평가 데이터로 비교합니다.

## 검증할 항목

레시피마다 지원 모달리티와 전처리 규약을 확인합니다. 로봇 행동 헤드와의 호환성은 별도로 검증합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/Automodel)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/Automodel/blob/HEAD/LICENSE)

## 관련 가이드

[NeMo Megatron Bridge](nemo-megatron-bridge.md) · [NeMo RL](nemo-rl.md)
