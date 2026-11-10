# NuRec

[← 전체 목록](../../README.ko.md) · [English](../en/nurec.md)

Omniverse NuRec은 촬영한 장면을 신경 표현으로 재구성해 시뮬레이터가 새로운 시점에서 센서 관측을 렌더링할 수 있게 한다. 자율주행에서는 주행 로그를 NCore로 변환하고 가우시안 표현을 학습하거나 초기화한 뒤, USDZ로 내보내 렌더링에 사용한다.

## 센서 기록에서 장면 재구성

![주행 로그를 USDZ로 재구성하는 NVIDIA NuRec 공식 파이프라인](https://docs.nvidia.com/nurec/_images/nurec-pipeline-overview.png)

공식 구성도는 형식 변환, 재구성, USDZ 패키징을 나눈다. 문서의 계층화 예시에서는 고정 배경, 움직이는 강체, 보행자와 도로를 서로 다른 가우시안 층으로 다루고, 하늘에는 환경 맵을 사용한다. 객체 추적과 시맨틱 라벨을 활용해 관측을 각 층에 배정한다. [공식 재구성 확장 및 레이어 가이드](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html)

## 공식 센서 구성 변경 워크플로 읽기

![NVIDIA NuRec 차종별 센서 구성 변환 아키텍처](https://developer-blogs.nvidia.com/wp-content/uploads/2026/08/image-39.webp)

재구성된 USDZ 장면에서 시작해 대상 차종의 카메라 배치로 다시 렌더링한다. 그림의 예시는 인식 모델 학습 전에 NVIDIA Harmonizer를 프레임에 적용하는 경로도 보여준다. 시뮬레이터 연동에서는 NuRec gRPC가 장면과 카메라 또는 LiDAR 렌더링 요청을 받아 요청한 관측 결과를 반환한다. [공식 차종 전환 사례](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec) · [gRPC API 가이드](https://docs.nvidia.com/nurec/api/grpc_api_guide.html)

| 데이터 경계 | 확인할 내용 |
|---|---|
| 촬영 로그에서 NCore로 변환 | 센서 보정, 타임스탬프 동기화, 자차 움직임 |
| 재구성에서 USDZ로 내보내기 | 지정한 장면 ID로 결과와 기준 렌더가 열리는지 |
| 실행 서비스에서 클라이언트로 전달 | 카메라 내부 파라미터, 요청한 자세, 출력 형식 |
| 합성 영상에서 검증으로 이동 | 촬영 범위 밖에서 나타나는 가림, 동적 객체, 외관 |

## 활용 예시 — 카메라 배치 변경 비교

재구성한 주행 장면을 먼저 원래 카메라 자세에서 렌더링하고, 다음으로 새 카메라 구성에서 렌더링한다. 새 시점을 해석하기 전에 원본 영상과 원래 카메라 렌더의 차선 위치 및 동적 객체 타이밍을 비교한다. 새 시점에서는 기존 센서로 볼 수 없던 영역이 나타날 수 있으므로 이런 샘플을 검토 단계에서 표시한다. [공식 재구성 안내](https://docs.nvidia.com/nurec/nurec/model.html) · [재구성 확장 가이드](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html)

배포 경로에 따라 접근 방법, 런타임, 학습된 아티팩트와 데이터 조건이 달라진다. [공식 NuRec 소개](https://developer.nvidia.com/omniverse/nurec)

## 소스와 런타임 배포

공개 NuRec SDK에는 Apache-2.0으로 제공되는 복원·렌더링 라이브러리, 학습 시스템, 애플리케이션 실행 코드가 있습니다. 런타임 컨테이너는 NVIDIA NGC의 각 카탈로그 페이지에 명시된 조건으로 배포합니다. 모델 체크포인트와 장면 데이터에는 별도 조건이 적용됩니다. NCore는 복원에 입력하는 센서 기록의 공통 형식과 변환 도구를 Apache-2.0으로 제공합니다. [NuRec SDK와 배포 조건](https://github.com/NVIDIA/NuRec#source-containers-and-models) · [SDK 라이선스](https://github.com/NVIDIA/NuRec/blob/main/LICENSE.md) · [NCore](https://github.com/NVIDIA/ncore)

[준비된 NuRec 장면으로 AlpaSim 폐루프 평가 따라 하기](workflows/alpasim-closed-loop.md).
