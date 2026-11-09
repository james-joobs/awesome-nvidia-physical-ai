# Microduck

[← 전체 목록](../../README.ko.md) · [English](../en/microduck.md)

<p align="center">
  <img src="../../assets/microduck/wordmark.svg" alt="Microduck" width="240">
</p>

Microduck은 Hugging Face의 로봇 팀인 Pollen Robotics가 만든 소형 이족보행 로봇입니다. NVIDIA의 Isaac Lab 3.0 튜토리얼은 GPU에서 여러 환경을 병렬로 돌려 보행 정책을 학습하고, ONNX로 내보내 평가한 뒤 실물 로봇에 탑재하는 과정을 보여줍니다. [Pollen Robotics 프레스 키트와 워드마크](https://pollen-robotics.com/microduck/press-kit/) · [Hugging Face의 NVIDIA 튜토리얼](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real)

[브라우저에서 조종하기](https://huggingface.co/spaces/pollen-robotics/microduck-simulator) · [Arena에서 정책 평가하기](https://huggingface.co/spaces/pollen-robotics/microduck-arena) · [공개 ONNX 정책 보기](https://huggingface.co/pollen-robotics/microduck-policies)

<p align="center">
  <img src="https://github.com/user-attachments/assets/c2f7c245-8217-46a1-8d1e-e0ba967cd969" alt="Pollen Robotics가 공개한 Microduck 공식 프로젝트 이미지" width="640">
</p>

[이미지 출처 · Pollen Robotics 로봇 소프트웨어 저장소](https://github.com/pollen-robotics/microduck)

## 시뮬레이션 학습에서 실물 배포까지

| 단계 | 도구의 역할 |
|---|---|
| 학습 환경 구성 | Isaac Lab의 Microduck 예제는 로봇 모델, 관측값, 관절 목표, 보상과 초기화 방식을 정의합니다. 평지 예제로 시작할 수 있고, 험지 예제에는 고르지 않은 지면, 경사로와 계단이 추가됩니다. [예제 소스](https://github.com/isaac-sim/IsaacLab/tree/main/source/isaaclab_tasks/isaaclab_tasks/contrib/microduck) |
| 시뮬레이션에서 학습 | Isaac Lab은 Newton의 MJWarp 솔버로 여러 환경을 병렬 실행합니다. 백래시 프리셋은 BAM으로 기어 유격 등 서보의 동작을 재현합니다. 마찰, 질량, 명령 지연 등을 바꿔 실물에서 마주칠 수 있는 조건을 학습 중에 경험하게 합니다. [NVIDIA 튜토리얼](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real) |
| 재생 및 내보내기 | RSL-RL로 학습한 체크포인트를 Newton 시각화 도구에서 재생하면 Isaac Lab이 `policy.onnx`를 내보냅니다. 예제 정책은 관측값 61개를 받아 관절 위치 목표 14개를 반환합니다. 런타임을 옮길 때 관측값 순서와 정규화, 행동값 스케일을 맞춥니다. [NVIDIA 내보내기 안내](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real#4-evaluate-the-microduck-walking-policy-and-export-it-to-onnx) |
| 평가와 배포 | 호환되는 ONNX 정책을 Microduck Arena에 제출하면 공통 코스에서 서버가 점수를 계산합니다. 실물에서는 Rust 런타임이 ONNX 정책을 불러와 서보를 구동합니다. [Arena 제출 안내](https://github.com/pollen-robotics/microduck-arena/blob/main/docs/guides/train-a-policy.md) · [로봇 정책 명령 안내](https://github.com/pollen-robotics/microduck/blob/main/docs/robot/cheatsheet.md) |

Pollen Robotics가 먼저 공개한 학습 스택은 [Microduck RL](https://github.com/pollen-robotics/microduck_rl)입니다. mjlab에서 MuJoCo Warp와 PPO를 사용합니다. Hub의 mjlab 체크포인트를 이어 학습할 때는 Microduck RL 문서를, Isaac Lab 예제를 실행할 때는 NVIDIA 튜토리얼을 참고하세요.

## Hugging Face 리소스

| 리소스 | 활용 방법 | 공개 범위와 라이선스 |
|---|---|---|
| [Microduck Sandbox](https://huggingface.co/spaces/pollen-robotics/microduck-simulator) | 키보드나 게임패드로 기존 정책을 체험합니다. MuJoCo 물리 계산과 ONNX 추론이 브라우저에서 실행됩니다. | 공개 Space. 앱 코드는 Apache-2.0으로 표시되며 포함된 로봇 자산의 조건은 별도입니다. |
| [Microduck Arena](https://huggingface.co/spaces/pollen-robotics/microduck-arena) | 공통 챌린지에서 제출한 정책의 성능을 비교합니다. | 공개 Space 및 [소스 저장소](https://github.com/pollen-robotics/microduck-arena). Space에 제출하려면 Hugging Face 로그인이 필요하며 저장소 전체의 라이선스는 미확인입니다. |
| [Microduck ONNX 정책](https://huggingface.co/pollen-robotics/microduck-policies) | 걷기, 일어서기 등 배포 가능한 정책을 내려받습니다. | 공개 모델 저장소. Apache-2.0 태그가 표시됩니다. |
| [Microduck 학습 체크포인트](https://huggingface.co/pollen-robotics/microduck-training) | 옵티마이저와 정규화 상태가 들어 있는 RSL-RL `.pt` 번들로 mjlab 학습을 이어가거나 초기화합니다. | 공개 모델 저장소. 라이선스 미확인입니다. |
| [Microduck 탐지 모델](https://huggingface.co/pollen-robotics/microduck-duck-detector)과 [데이터셋](https://huggingface.co/datasets/pollen-robotics/microduck-duck-detector-dataset) | 로봇 카메라가 촬영한 프레임과 다른 Microduck의 바운딩 박스를 사용해 객체 탐지 과정을 살펴봅니다. 유사한 프레임이 학습·검증에 동시에 들어가지 않도록 촬영 세션 단위로 나눕니다. | 공개 모델과 데이터셋. 둘 다 Apache-2.0 태그가 표시됩니다. |

## 라이선스와 공개 범위

[로봇 런타임 코드](https://github.com/pollen-robotics/microduck/blob/main/LICENSE)와 [Microduck RL 코드](https://github.com/pollen-robotics/microduck_rl/blob/main/LICENSE)는 Apache-2.0입니다. [별도 목록에 명시된 시뮬레이션용 STL 메시](https://github.com/pollen-robotics/microduck_rl/blob/develop/LICENSE-MODELS.md)에는 CC BY-NC-SA 4.0이 적용됩니다. Pollen Robotics가 밝힌 소프트웨어 오픈소스 범위에서 제품의 기구·전자 설계 파일은 제외됩니다. [공식 하드웨어 공개 범위](https://pollen-robotics.com/microduck/press-kit/)

## 관련 가이드

[Isaac Lab](isaac-lab.md) · [Newton](newton.md) · [MuJoCo Warp](mujoco-warp.md)
