# 프랑크푸르트 3D 주행

[English](README.en.md) · [PandaSet 노면 재투영](../README.ko.md) · [Pages에서 구현 원리와 실습 따라 하기](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/labs/frankfurt-reality/)

[KITScenes Multimodal의 Voxel51 공개 배포본](https://huggingface.co/datasets/Voxel51/kitscenes-multimodal)에서 세 구간을 골랐습니다. **3D 시작**을 누르고 Volvo 추적 시점으로 재생하세요. 멈춘 뒤 **3D 카메라** 또는 **실사 RGB**를 선택하면 같은 시간의 전·측·후방을 볼 수 있습니다. **자유 시점**에서 화면을 드래그해 차선과 외벽을 살펴보세요.

| 구간 | 길이 | 볼거리 |
| --- | ---: | --- |
| 트램이 지나는 교차로 | 19.5초 | 트램, 자전거, 보행자, 교차로의 차량 |
| 가로수길과 양방향 차량 | 27.0초 | 마주 오는 차량과 갓길의 주차 차량 |
| 도심 교량 | 7.2초 | 기존 도심 장면에 추가한 추적·전후방 시점 |

LoMa로 프레임 사이의 특징점을 찾고, COLMAP의 번들 조정으로 카메라 자세를 맞췄습니다. Mask2Former로 노면·하늘·차량을 구분한 뒤 노면은 RGB 재투영, 하늘은 파노라마, 나머지 정적 배경은 gsplat으로 복원했습니다. 세 구간에서 카메라 이미지 936장의 자세를 복원했습니다. 원본은 3504 × 2272이고, **실사 RGB**에서는 브라우저용으로 줄인 이미지를 표시합니다.

Volvo는 주행 경로를 보여주기 위해 추가한 차량입니다. 모델 메시에서 타이어 네 개의 접지점을 찾아 노면 높이에 맞췄습니다. **실사 RGB** 또는 **실사 추적 창**에서 주변 차량을 확인할 수 있습니다. [RT-DETR](https://huggingface.co/PekingU/rtdetr_r50vd)로 실사 프레임의 객체를 검출하고, 박스의 이동과 색 분포를 비교해 ID를 이어 붙입니다. 카메라별로 별도 ID를 사용하며 가림 뒤에는 ID가 달라질 수 있습니다. **촬영 경로 표시**를 켜면 카메라가 지나온 길을 볼 수 있습니다.

[설치와 재현 명령](README.en.md#reproduce) · [데이터 출처와 변경 사항](../../../../site/public/showcase/reality-kitscenes/ATTRIBUTION.txt).
