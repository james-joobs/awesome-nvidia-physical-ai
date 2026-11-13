# Physical Intelligence π 시리즈와 openpi

[← 로봇 파운데이션 모델 목록](../../README.ko.md#로봇-파운데이션-모델과-vla) · [English](../en/physical-intelligence-pi.md)

Physical Intelligence의 π 시리즈는 카메라 영상, 언어 지시, 로봇 상태를 입력으로 받아 로봇의 행동을 생성합니다. openpi 저장소에서 세 모델의 추론·미세조정 코드와 체크포인트를 제공하고, Pi API 베타는 호스팅 환경에서 미세조정과 추론을 제공합니다. 공개 범위는 2026년 11월 13일 기준입니다.

## 모델과 공개 범위

| 모델·서비스 | 역할 | 공개 범위 |
|---|---|---|
| **π0** | PaliGemma 백본과 플로 매칭 행동 모듈을 사용해 연속 행동 시퀀스를 생성합니다. | 기본 체크포인트와 일부 ALOHA·DROID 미세조정 체크포인트를 공개했습니다. [논문](https://arxiv.org/abs/2410.24164) · [공개 발표](https://www.pi.website/blog/openpi) · [체크포인트](https://github.com/Physical-Intelligence/openpi#model-checkpoints) |
| **π0-FAST** | 이산 행동 토큰을 자기회귀 방식으로 생성하고 로봇 행동으로 디코딩합니다. | 기본 및 DROID 체크포인트를 공개했습니다. FAST 행동 토크나이저도 별도로 제공합니다. [체크포인트](https://github.com/Physical-Intelligence/openpi#model-checkpoints) · [FAST 토크나이저](https://huggingface.co/physical-intelligence/fast) |
| **π0.5** | π0를 바탕으로 여러 종류의 로봇 데이터와 시각·언어 데이터를 함께 학습해 새로운 환경에 대한 일반화를 개선합니다. | 기본 및 LIBERO·DROID 미세조정 체크포인트를 공개했습니다. 모델 발표는 2025년 4월, openpi 체크포인트 공개는 2025년 9월입니다. [연구 발표](https://www.pi.website/blog/pi05) · [체크포인트](https://github.com/Physical-Intelligence/openpi#model-checkpoints) |
| **π0.6 / π*0.6** | π0.6은 개선된 기본 VLA입니다. π*0.6은 RECAP 방식으로 로봇의 실행 경험과 피드백을 활용해 강화학습을 추가합니다. | 2025년 11월 17일 연구를 발표했습니다. 두 모델 모두 openpi 체크포인트 목록에 없습니다. [연구 발표](https://www.pi.website/blog/pistar06) |
| **π0.7** | 언어, 중간 목표 이미지 등의 정보를 조건으로 사용해 여러 작업과 로봇 기종에 기술을 적용합니다. | 2026년 4월 16일 연구를 발표했습니다. 공개 체크포인트는 확인되지 않았습니다. [연구 발표](https://www.pi.website/blog/pi07) |
| **Pi API 베타** | 시연 데이터를 올리면 관리형 환경에서 미세조정하고, 학습한 정책을 호스팅해 추론합니다. | 2026년 10월 13일 대기자 등록과 함께 발표했습니다. 공개 발표에는 사용할 수 있는 모델의 식별자가 명시돼 있지 않습니다. [발표](https://www.pi.website/blog/api-beta) · [대기자 등록](https://www.pi.website/) |

## 공개 체크포인트로 시작하기

1. 정책 서버가 관측을 받아 행동 묶음을 반환하는지 확인하려면 지원 GPU 환경에서 공식 테스트 클라이언트를 실행합니다. 이 예제는 로봇 없이 임의의 관측을 만들어 요청을 보냅니다. [openpi 요구사항](https://github.com/Physical-Intelligence/openpi#requirements) · [테스트 클라이언트](https://github.com/Physical-Intelligence/openpi/tree/main/examples/simple_client)
2. 시뮬레이션에서 작업 수행을 평가하려면 공개된 π0.5-LIBERO 체크포인트와 공식 LIBERO 예제를 사용합니다. 시뮬레이션 클라이언트가 새 관측을 정책 서버에 보내고, 돌아온 행동을 적용합니다. [openpi LIBERO 예제](https://github.com/Physical-Intelligence/openpi/tree/main/examples/libero)
3. 다른 로봇에 적용하려면 기본 체크포인트를 선택하고 대상 환경에서 시연을 수집합니다. openpi 미세조정 예제는 LeRobot 데이터를 사용하며, 로봇에 맞는 입력·출력 변환과 정규화 방법을 정의합니다. [미세조정 안내](https://github.com/Physical-Intelligence/openpi#fine-tuning-base-models-on-your-own-data) · [LeRobot π0.5 정책](https://huggingface.co/docs/lerobot/pi05)

카메라 입력 이름, 상태·행동 순서, 정규화 통계, 제어기가 요구하는 행동 형식을 체크포인트와 맞춥니다. 짧게 시뮬레이션을 실행해 동작을 확인하고 작업 성공률과 추론 지연을 측정합니다. openpi의 PyTorch 구현은 π0와 π0.5를 지원합니다. π0-FAST는 공식 JAX 구현을 사용합니다. [openpi PyTorch 지원](https://github.com/Physical-Intelligence/openpi#pytorch-support) · [정규화 통계](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

## 코드·체크포인트 이용 조건

openpi 저장소 코드는 Apache-2.0입니다. 공식 체크포인트 목록에는 다운로드 위치가 있고, 체크포인트별 이용 조건은 명시돼 있지 않습니다. Hugging Face의 LeRobot 변환본 π0와 π0.5 기본 체크포인트에는 Gemma 라이선스 태그가 붙어 있습니다. 사용하려는 체크포인트, 백본, 학습 데이터에 적용되는 조건을 각각 확인합니다. [openpi LICENSE](https://github.com/Physical-Intelligence/openpi/blob/main/LICENSE) · [LeRobot π0 카드](https://huggingface.co/lerobot/pi0_base) · [LeRobot π0.5 카드](https://huggingface.co/lerobot/pi05_base) · [Gemma 약관](https://ai.google.dev/gemma/terms)

## 연관 상세 페이지

[LeRobot](lerobot.md) · [Isaac GR00T](groot-model.md)
