# RTX / DGX Spark

[← 전체 목록](../../README.ko.md) · [English](../en/rtx-dgx-spark.md)

RTX는 렌더링과 가속 계산에 사용하는 GPU 제품군입니다. DGX Spark는 GB10 Grace Blackwell과 통합 메모리를 탑재한 독립형 시스템입니다. 물리 AI 개발에서 각 장비가 맡을 역할은 다릅니다.

![DGX Spark GB10 패키지](https://www.nvidia.com/content/nvidiaGDC/us/en_US/products/workstations/dgx-spark/_jcr_content/root/responsivegrid/nv_container_5347712/nv_image.coreimg.png/1792558737455/nvidia-gb10-grace-blackwell-superchip-2x.png)

*NVIDIA 제품 그림의 GB10 하드웨어입니다. 소프트웨어 호환 범위는 별도 문서에서 확인합니다.* [공식 그림 출처](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)

## 어떻게 동작하나

RTX 워크스테이션에서는 호환 시뮬레이터와 렌더링 워크로드를 실행할 수 있습니다. DGX Spark는 Arm CPU와 Blackwell GPU가 시스템 메모리를 공유하며 시스템 이미지로 소프트웨어를 제공합니다. 애플리케이션, 런타임과 모델이 대상 아키텍처를 지원해야 합니다. 체크포인트는 옮길 수 있어도 컴파일된 엔진이나 컨테이너 이미지는 다시 빌드해야 할 수 있습니다.

## 실전 워크플로

지원되는 로컬 시스템에서 인식 모델을 개발한 뒤 고정 테스트 데이터로 출력을 확인합니다. 체크포인트나 이식 가능한 그래프를 대상으로 내보내고, 배포 성능은 대상 장비에서 측정합니다.

## 검증할 항목

명령어 아키텍처, 메모리 용량과 사용량, 패키지 및 CUDA·런타임 버전을 확인합니다. 시뮬레이션은 시뮬레이터의 공식 지원 플랫폼을 기준으로 장비를 선택합니다.

## 공개 범위와 라이선스

하드웨어·제품; 오픈소스 프로젝트 아님. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)
- [관련 공식 자료 · www.nvidia.com](https://www.nvidia.com/en-us/geforce/graphics-cards/)
