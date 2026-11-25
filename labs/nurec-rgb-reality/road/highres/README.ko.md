# 프랑크푸르트 도로를 새 시점에서 보기

[English](README.en.md) · [PandaSet 노면 재투영](../README.ko.md)

[KITScenes Multimodal의 Voxel51 공개 배포본](https://huggingface.co/datasets/Voxel51/kitscenes-multimodal)에서 프랑크푸르트 도심 7.2초 구간을 골랐습니다. **3D 시작**을 누르고 촬영 경로, 좌우 위치, 높이를 바꿔 보세요. 정적 장면을 복원할 때 움직이는 차량과 사람을 제외했습니다. 먼 건물과 가려진 부분에는 빈 곳이나 잔상이 남습니다.

| 데이터 후보 | 카메라와 공개 조건 |
| --- | --- |
| [KITScenes Multimodal](https://www.kitscenes.com/multimodal/) | 이번에 쓴 주변 카메라 6대의 원본은 각각 3504 × 2272입니다. 전체 리그는 카메라 9대에서 시점당 72.5MP를 기록합니다. 공식 다운로드는 접근 신청이 필요하고, Voxel51 배포본은 CC BY-NC 4.0 및 KITScenes 조건에 따라 공개돼 있습니다. |
| [Zenseact Open Dataset](https://zod.zenseact.com/) | 8MP 광각 전방 카메라, CC BY-SA 4.0. 시퀀스 다운로드에는 접근 신청이 필요합니다. |
| [Argoverse 2 Sensor](https://www.argoverse.org/av2.html) | 주변 카메라 7대와 전방 스테레오. 가로 또는 세로 2048 × 1550. [AWS에서 공개 다운로드](https://registry.opendata.aws/argoverse/), CC BY-NC-SA 4.0. |

RGB와 제공된 카메라 내부 파라미터를 입력으로 사용했습니다. LoMa로 이미지의 같은 지점을 찾고 COLMAP으로 차량 경로와 3D 점을 복원했습니다. 25시점 × 카메라 6대의 **150장 모두 등록**됐습니다. 최대 1440px 너비에서 학습에 사용한 특징점의 평균 재투영 오차는 **1.00px**입니다.

RTX 5090 한 장에서 최대 1152px 너비의 영상으로 Gaussian **292,762개**를 학습했습니다. 노면은 1920 × 852 텍스처에 원본 해상도의 RGB를 샘플링했고, 하늘은 별도 파노라마에 담았습니다. 텍스처 생성과 외관 학습에서 뺀 이미지 8장의 정적 영역은 평균 **24.49dB PSNR**이었습니다. 이 이미지들은 카메라 자세 추정에 사용했습니다.

[설치와 재현 명령](README.en.md#reproduce) · [데이터 출처와 변경 사항](../../../../site/public/showcase/reality-kitscenes/ATTRIBUTION.txt).
