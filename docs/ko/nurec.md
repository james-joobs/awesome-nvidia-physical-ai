# NuRec

[← 프로젝트 홈](../../README.ko.md) · [English](../en/nurec.md)

Omniverse NuRec은 촬영한 장면을 신경 표현으로 재구성해 시뮬레이터가 새로운 시점에서 센서 관측을 렌더링할 수 있게 합니다. 자율주행에서는 주행 로그를 NCore로 변환하고 가우시안 표현을 학습하거나 초기화한 뒤, USDZ로 내보내 렌더링에 사용합니다.

## 주행 장면을 다른 위치의 카메라에서 어떻게 볼 수 있을까요?

### 카메라 보정과 3D Gaussian Splatting

보정값은 두 부분으로 나뉩니다. **내부 파라미터**는 초점거리나 영상 중심처럼 3D 점이 이미지의 어느 픽셀에 나타나는지 정합니다. **외부 파라미터**는 카메라가 차량이나 월드에 대해 어디에 있고 어느 쪽을 향하는지 나타냅니다. 이렇게 각 영상의 시점을 알면 여러 장에서 보이는 표면을 하나의 장면으로 맞출 수 있습니다.

3D Gaussian Splatting은 장면을 여러 타원형 가우시안의 중심·모양과 색·투명도로 표현합니다. 렌더러는 새 카메라에서 보이는 방향으로 가우시안을 투영해 픽셀을 합성합니다. 예를 들어 새 카메라를 0.2m 높이는 경우, 먼저 원래 자세로 얻은 렌더가 기록 영상과 잘 맞는지 확인한 뒤 두 위치에서 차선과 물체가 어떻게 보이는지 비교합니다. [NuRec 공식 문서](https://docs.nvidia.com/nurec/) · [AlpaSim 폐루프 가이드](workflows/alpasim-closed-loop.md)

## 센서 기록에서 장면 재구성

![주행 로그를 USDZ로 재구성하는 NVIDIA NuRec 공식 파이프라인](https://docs.nvidia.com/nurec/_images/nurec-pipeline-overview.png)

공식 구성도는 형식 변환, 재구성, USDZ 패키징을 나눕니다. 문서의 계층화 예시에서는 고정 배경, 움직이는 강체, 보행자와 도로를 서로 다른 가우시안 층으로 다루고, 하늘에는 환경 맵을 사용합니다. 객체 추적과 시맨틱 라벨을 활용해 관측을 각 층에 배정합니다. [공식 재구성 확장 및 레이어 가이드](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html)

## 공식 센서 구성 변경 워크플로 읽기

![NVIDIA NuRec 차종별 센서 구성 변환 아키텍처](https://developer-blogs.nvidia.com/wp-content/uploads/2026/08/image-39.webp)

재구성된 USDZ 장면에서 시작해 대상 차종의 카메라 배치로 다시 렌더링합니다. 그림의 예시는 인식 모델 학습 전에 NVIDIA Harmonizer를 프레임에 적용하는 경로도 보여줍니다. 시뮬레이터 연동에서는 NuRec gRPC가 장면과 카메라 또는 LiDAR 렌더링 요청을 받아 요청한 관측 결과를 반환합니다. [공식 차종 전환 사례](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec) · [gRPC API 가이드](https://docs.nvidia.com/nurec/api/grpc_api_guide.html)

| 데이터 경계 | 확인할 내용 |
|---|---|
| 촬영 로그에서 NCore로 변환 | 센서 보정, 타임스탬프 동기화, 자차 움직임 |
| 재구성에서 USDZ로 내보내기 | 지정한 장면 ID로 결과와 기준 렌더가 열리는지 |
| 실행 서비스에서 클라이언트로 전달 | 카메라 내부 파라미터, 요청한 자세, 출력 형식 |
| 합성 영상에서 검증으로 이동 | 촬영 범위 밖에서 나타나는 가림, 동적 객체, 외관 |

## 활용 예시 — 카메라 배치 변경 비교

재구성한 주행 장면을 먼저 원래 카메라 자세에서 렌더링하고, 다음으로 새 카메라 구성에서 렌더링합니다. 새 시점을 해석하기 전에 원본 영상과 원래 카메라 렌더의 차선 위치 및 동적 객체 타이밍을 비교합니다. 새 시점에서는 기존 센서로 볼 수 없던 영역이 나타날 수 있으므로 이런 샘플을 검토 단계에서 표시합니다. [공식 재구성 안내](https://docs.nvidia.com/nurec/nurec/model.html) · [재구성 확장 가이드](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html)

배포 경로에 따라 접근 방법, 런타임, 학습된 아티팩트와 데이터 조건이 달라집니다. [공식 NuRec 소개](https://developer.nvidia.com/omniverse/nurec)

## 소스와 런타임 배포

공개 NuRec SDK에는 Apache-2.0으로 제공되는 복원·렌더링 라이브러리, 학습 시스템, 애플리케이션 실행 코드가 있습니다. 런타임 컨테이너는 NVIDIA NGC의 각 카탈로그 페이지에 명시된 조건으로 배포합니다. 모델 체크포인트와 장면 데이터에는 별도 조건이 적용됩니다. NCore는 복원에 입력하는 센서 기록의 공통 형식과 변환 도구를 Apache-2.0으로 제공합니다. [NuRec SDK와 배포 조건](https://github.com/NVIDIA/NuRec#source-containers-and-models) · [SDK 라이선스](https://github.com/NVIDIA/NuRec/blob/main/LICENSE.md) · [NCore](https://github.com/NVIDIA/ncore)

[준비된 NuRec 장면으로 AlpaSim 폐루프 평가 따라 하기](workflows/alpasim-closed-loop.md).

[RGB만으로 시작하기: COLMAP → NVIDIA 3DGUT → RTX 5090 한 장으로 만드는 도로 뷰어](labs/rgb-reality-view.md). 카메라 보정값과 자세를 사진에서 추정하며 LiDAR·외부 깊이를 쓰지 않는 별도 오픈소스 실습입니다.

[직접 만든 도로 실습: NuRec 새 시점, Harmonizer 전후 비교, Alpamayo 예측 경로](labs/reality-view.md).


[실사 데이터 실습: PandaSet 도로 복원과 Volvo 자차 표시](labs/pandaset-nurec.md). 실측 RGB·LiDAR, 차량 모델 출처·사용 조건, GPU 없는 결과 검사를 제공합니다.
