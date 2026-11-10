# Isaac GR00T 코드

[← 목록으로](../../README.ko.md) · [English](../en/isaac-gr00t.md)

<p align="center">
  <img src="../../assets/project-marks/isaac-groot.png" width="290" alt="NVIDIA Isaac GR00T 워드마크"><br>
  <sub><a href="https://github.com/NVIDIA/Isaac-GR00T/blob/7aa0bca50f1097f8b17f5c274c98264b72a1419f/media/header_compress.png">Isaac GR00T 공식 저장소 워드마크</a></sub>
</p>

Isaac GR00T 저장소에는 로봇 정책을 미세조정하고 평가한 후 제공하는 소프트웨어가 있습니다. N1.7 체크포인트는 이 워크플로의 입력 중 하나입니다. 저장소에는 학습 데이터 구조, 로봇 형태별 전처리, 학습 정책의 평가·배포 인터페이스도 있습니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **데이터셋과 모달리티 매핑** | N1.7 코드는 LeRobot v2를 변형한 형식을 읽습니다. 영상 파일에 이미지가, Parquet에 수치 상태와 행동이 들어갑니다. 추가 파일인 `meta/modality.json`이 벡터와 영상 키를 정책의 이름 있는 입출력에 대응시킵니다. |
| **로봇 형태와 미세조정** | 로봇 형태 태그가 모달리티 구성과 정규화 방식을 선택합니다. 새 로봇을 추가할 때는 카메라와 상태 필드, 상대적인 말단 장치 행동 표현이 데이터와 모달리티 설정에서 일치해야 합니다. |
| **정책 인터페이스** | 정책은 관측값 묶음을 받아 여러 제어 시점의 행동 묶음을 반환합니다. 정책은 같은 프로세스나 정책 서버에서 실행할 수 있으며, 클라이언트가 센서와 실행, 다음 관측을 연결합니다. |

![공식 N1.7 구성도를 보면 저장소의 데이터·정책 인터페이스가 모델에 제공할 텐서와 제어를 위해 변환해야 할 출력이 구분됩니다.](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

공식 N1.7 구성도를 보면 저장소의 데이터·정책 인터페이스가 모델에 제공할 텐서와 제어를 위해 변환해야 할 출력이 구분됩니다. [공식 그림 출처](https://github.com/NVIDIA/Isaac-GR00T)

![공식 Unitree G1 예시는 하드웨어에서 정책을 실행하는 모습을 보여줍니다. 저장소는 G1과 G1 SONIC 구성의 전신 제어 인터페이스를 구분합니다.](https://media.githubusercontent.com/media/NVIDIA/Isaac-GR00T/main/media/unitree_g1.gif)

공식 Unitree G1 예시는 하드웨어에서 정책을 실행하는 모습을 보여줍니다. 저장소는 G1과 G1 SONIC 구성의 전신 제어 인터페이스를 구분합니다. [공식 그림 출처](https://github.com/NVIDIA/Isaac-GR00T)

## 적용 예시

1. 번들 SO100 큐브 담기 예시에서 정상 데이터셋과 모달리티 매핑을 살펴봅니다. 자체 기록이 LeRobot v3 형식이면 공식 v3→v2 변환 절차를 따릅니다.
2. 의도한 로봇 형태 설정으로 미세조정합니다. 학습에 쓰지 않은 행동과 개루프에서 비교해 카메라, 벡터 필드, 행동 크기 매핑 오류를 찾습니다.
3. 지원되는 시뮬레이터 또는 하드웨어에서 폐루프 평가를 하고 작업 성공, 초기화 동작, 실패 사례를 기록합니다.

## 검증할 항목

- 행동이 상대값인지 절대값인지와 변화량의 좌표계를 확인합니다. 개루프 행동 비교는 인터페이스 점검에, 폐루프 성공률은 오차가 누적된 후의 실제 동작 평가에 활용합니다.
- 호환되는 체크포인트와 로봇 형태 태그를 함께 선택합니다. 컨트롤러에 연결하기 전에 배포 추론 백엔드와 학습 설정의 일치 여부를 검증합니다.

## 공식 자료와 이용 조건

코드는 Apache-2.0입니다. 저장소는 N1.7 가중치에 NVIDIA Open Model License를 명시합니다.

- [저장소와 공식 평가 예제](https://github.com/NVIDIA/Isaac-GR00T)
- [데이터셋 준비 가이드](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_preparation.md)
- [정책 API와 로봇 형태 태그](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/policy.md)

## 연관 상세 페이지

[N1.7 모델 아키텍처](groot-model.md) · [LeRobot 데이터 형식](lerobot.md) · [Isaac ROS Deploy](isaac-ros-deploy.md)
