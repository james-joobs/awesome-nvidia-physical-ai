# NeMo Megatron Bridge

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-megatron-bridge.md)

Megatron Core 학습 레시피와 Hugging Face 체크포인트 양방향 변환.

![Megatron Bridge 프로젝트 개요](https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/main/Repo-Mbridge.png)

체크포인트 변환 도구와 학습 생태계의 관계를 보여 주는 프로젝트 그림입니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/Megatron-Bridge)

## 아키텍처와 데이터 흐름

Bridge는 지원 Hugging Face 모델의 가중치와 구성을 Megatron Core 표현에 매핑합니다. 학습 레시피에서 데이터, 병렬화, 옵티마이저와 학습 방식을 설정합니다. 지원 모델을 사전학습하거나 SFT·LoRA로 조정한 후 적합한 변환을 통해 Hugging Face 형식으로 내보낼 수 있습니다.

## 물리 AI 활용 예시

대형 VLM을 여러 GPU에서 지도 미세조정하기 전에 소량의 검사 이미지로 Hugging Face→Megatron 변환을 검증합니다. 학습 후 같은 영상과 문구로 학습 환경과 내보낸 모델의 출력을 비교합니다.

## 검증할 항목

정확한 모델 아키텍처의 변환 지원 여부와 토크나이저, 영상 프로세서, 변환 전후 수치 일치도를 확인합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/Megatron-Bridge)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/HEAD/LICENSE)

## 관련 가이드

[NeMo AutoModel](nemo-automodel.md) · [NeMo RL](nemo-rl.md)
