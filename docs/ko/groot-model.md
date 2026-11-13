# Isaac GR00T 모델 계열

[← 목록으로](../../README.ko.md) · [English](../en/groot-model.md)

| 버전 | 모델 유형과 역할 | 공개 상태 · 2026년 11월 13일 기준 |
|---|---|---|
| **GR00T 2 / GR00T 2 Turbo** | Cosmos 기반 월드 액션 모델(WAM). 관측, 지시, 로봇 상태에서 미래 영상과 행동 시퀀스를 함께 예측합니다. Turbo는 로봇에서 직접 실행하는 전신 제어용입니다. | 11월 9일 CoRL에서 발표했습니다. NVIDIA Research는 2026년 12월 코드 공개를 예고했습니다. 11월 13일 기준 공개 가중치와 적용 약관은 확인되지 않았습니다. [연구·데모](https://research.nvidia.com/labs/gear/gr00t-2/) · [CoRL 발표](https://blogs.nvidia.com/blog/robotics-simulation-advancements-corl/) |
| **GR00T N1.7-3B** | 여러 로봇 형태에 대응하는 조작용 시각·언어·행동(VLA) 모델. | [2026년 7월 7일](https://github.com/NVIDIA/Isaac-GR00T/commit/1a1837f20538b7d7e21f977a11a5aee14f99803c) 정식 공개(GA). 참조 코드는 Apache-2.0, 가중치는 NVIDIA Open Model License를 적용합니다. [코드](https://github.com/NVIDIA/Isaac-GR00T) · [기본 체크포인트](https://huggingface.co/nvidia/GR00T-N1.7-3B) · [가중치 약관](https://huggingface.co/nvidia/GR00T-N1.7-3B/blob/main/LICENSE) |

## N1.7 아키텍처와 데이터 흐름

N1.7의 시각·언어 백본은 장면과 지시를 임베딩하고, 행동 헤드는 로봇의 현재 상태와 형태를 조건으로 연속값 행동 시퀀스를 예측합니다.

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **비전과 언어** | 로봇 카메라 프레임과 텍스트 지시를 Cosmos Reason2 기반 비전·언어 백본에 입력합니다. N1.6에서 달라진 백본은 N1.7 저장소 설명에서 확인할 수 있습니다. |
| **자기 상태와 로봇 형태** | 로봇 형태에 대응하는 MLP가 로봇 상태를 인코딩합니다. 패딩과 이름이 지정된 모달리티 필드를 사용해 로봇별 필드의 의미를 유지하면서 서로 다른 상태 차원을 처리합니다. |
| **흐름 정합 행동 헤드** | 확산 트랜스포머가 잡음이 있는 행동 시퀀스를 행동 묶음으로 바꾸는 흐름을 추정합니다. 제어 벡터의 인코딩과 디코딩은 로봇 형태별 투영 계층이 담당합니다. |
| **컨트롤러 연결 지점** | 상대 말단 장치 목표는 설정에 따른 현재 자세를 기준으로 움직임을 표현합니다. 실행 시스템이 선택한 행동을 로봇 컨트롤러가 처리할 수 있는 명령으로 변환합니다. |

![구성도에서 비전·언어 조건과 행동 생성 경로가 구분됩니다. 상태와 로봇 형태 입력을 행동 경로와 함께 보면 로봇의 제어 의미가 모델의 어느 지점에 반영되는지 알 수 있습니다.](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

구성도에서 비전·언어 조건과 행동 생성 경로가 구분됩니다. 상태와 로봇 형태 입력을 행동 경로와 함께 보면 로봇의 제어 의미가 모델의 어느 지점에 반영되는지 알 수 있습니다. [공식 그림 출처](https://huggingface.co/nvidia/GR00T-N1.7-3B)

## 적용 예시

1. 릴리스된 모델과 지원되는 DROID 관측 샘플에서 시작합니다. 선언된 카메라 키, 상태 필드, 작업 지시, 로봇 형태 태그를 제공합니다.
2. 예상한 좌표 및 정규화 규약에 따라 행동 묶음을 검토합니다. 호환되는 컨트롤러로 폐루프 롤아웃을 실행한 후 목표 작업의 성공 여부를 평가합니다.

## 검증할 항목

- 행동 차원의 수와 순서는 로봇 형태 설정에 따라 달라집니다. 값을 모터 명령으로 해석하기 전에 컨트롤러와 모달리티 정의를 확인합니다.
- 배포 체크포인트가 다루는 작업과 환경을 구분하고, 새로운 작업과 환경은 별도로 평가합니다. 수치상 행동 오차와 함께 추론 지연 및 작업 성공률을 기록합니다.

## 공식 자료와 이용 조건

NVIDIA는 11월 11일 N1.7-3B와 공식 Bridge·Fractal·DROID·LIBERO 체크포인트에 남아 있던 비상업용 약관 파일을 교체했다고 확인했습니다. 수정된 NVIDIA Open Model License는 약관에 따라 상업적 사용을 허용합니다. [NVIDIA 확인](https://forums.developer.nvidia.com/t/gr00t-n1-7-license-clarification-model-card-says-commercial-use-but-license-file-in-hf-repo-says-non-commercial/387959/3)

- [N1.7 코드 라이선스](https://github.com/NVIDIA/Isaac-GR00T/blob/main/LICENSE)
- [N1.7 벤치마크 체크포인트와 로봇 형태 태그](https://github.com/NVIDIA/Isaac-GR00T#model-checkpoints--embodiment-tags)

## 연관 상세 페이지

[Isaac GR00T 코드](isaac-gr00t.md) · [GR00T-H](gr00t-h.md)
