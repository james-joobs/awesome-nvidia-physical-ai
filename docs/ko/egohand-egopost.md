# EgoHand / EgoPost

[← 목록으로](../../README.ko.md) · [English](../en/egohand-egopost.md)

EgoHand는 헤드마운트 영상으로 사람의 손을 복원합니다. EgoPost는 Isaac Capture에서 이 워크플로의 후처리 코드를 담는 구성 요소입니다. 복원 결과는 카메라 좌표계에서 검토할 수 있으며, 카메라 궤적이 있으면 월드 좌표계로 변환할 수 있습니다.

## 아키텍처와 데이터 흐름

| 구성 요소 | 입력·처리·출력 |
|---|---|
| **영상과 카메라 보정** | 디코딩한 RGB 영상과 카메라 보정값을 넣습니다. 각 손의 2D 바운딩 박스는 선택적 RT-DETR 검출기나 프레임별 박스 파일로 제공할 수 있습니다. |
| **손 복원** | 추론 파이프라인은 손 영역과 카메라 보정값으로 SOMA 손 자세, 3D 관절, 메시를 추정합니다. 선택적 시퀀스 피팅에서는 손의 형상과 크기를 클립 전체에서 공유하고 자세와 위치는 프레임마다 추정합니다. |
| **카메라 위치 추정** | 호환되는 카메라 위치 추정 또는 SLAM 파이프라인의 카메라 움직임을 사용해 손 추정값을 월드 좌표계로 변환합니다. |
| **검토용 산출물** | 시퀀스 피팅 결과는 `soma_parameters.npz`와 진단 보고서로 내보낼 수 있습니다. 오버레이 영상은 복원한 관절을 원본 영상에 투영해 프레임별 검토를 돕습니다. |

![구성도에서 손 복원과 카메라 위치 추정이 별개 경로로 표시됩니다. 월드 좌표계의 손 궤적을 구하려면 두 추정값이 모두 필요합니다.](https://nvidia.github.io/IsaacCapture/main/_images/egohand-pipeline.svg)

구성도에서 손 복원과 카메라 위치 추정이 별개 경로로 표시됩니다. 월드 좌표계의 손 궤적을 구하려면 두 추정값이 모두 필요합니다. [공식 그림 출처](https://nvidia.github.io/IsaacCapture/main/ego_post_processing/egohand.html)

![공식 V2D 예시에는 입력 카메라 시점과 복원 결과가 나옵니다. 물체와 접촉해 손이 가려지기 쉬운 순간의 손가락과 손목을 살펴볼 수 있습니다.](https://nvidia.github.io/IsaacCapture/main/_images/egohand-v2d-example.jpg)

공식 V2D 예시에는 입력 카메라 시점과 복원 결과가 나옵니다. 물체와 접촉해 손이 가려지기 쉬운 순간의 손가락과 손목을 살펴볼 수 있습니다. [공식 그림 출처](https://nvidia.github.io/IsaacCapture/main/ego_post_processing/egohand.html)

## 적용 예시

1. 공식 문서의 V2D 헤드마운트 예시와 제공되는 보정값으로 시작합니다. 손 영역을 검출하거나 프레임별 좌·우 손 박스 파일을 지정합니다.
2. 손을 복원하고 오버레이를 확인한 후 로봇 리타기팅에 전달합니다. 여러 시점에서 일관된 월드 좌표가 필요한 작업에 카메라 궤적을 추가합니다.

## 검증할 항목

- 박스는 원본 영상 픽셀과 인체 기준 좌·우를 사용합니다. 영상이 좌우 반전되거나 보정값이 틀리면 투영이 그럴듯해 보여도 3D 자세가 어긋날 수 있습니다.
- 관절을 영상에 다시 투영해 보고, 가림 구간의 떨림이나 갑작스러운 크기 변화를 확인합니다. 카메라 위치 추정을 사용했다면 월드 좌표의 드리프트도 별도로 검사합니다.

## 공식 자료와 이용 조건

EgoPost는 OpenMDW-1.1을 적용합니다. EgoHand의 독립 라이선스는 미확인입니다. 사용하는 에셋과 가중치에 표시된 조건을 확인합니다.

- [EgoHand 설치·입출력 문서](https://nvidia.github.io/IsaacCapture/main/ego_post_processing/egohand.html)
- [Isaac Capture 소스와 구성 요소별 이용 조건](https://github.com/NVIDIA/IsaacCapture)

## 연관 상세 페이지

[Isaac Capture](isaac-capture.md) · [Video to Data](video-to-data.md)
