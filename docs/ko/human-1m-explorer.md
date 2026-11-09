# Human-1M Explorer

[전체 목록](../../README.ko.md) · [English](../en/human-1m-explorer.md)

Human-1M Explorer는 NVIDIA의 1인칭 사람 작업 시연 브라우저다. Space에서는 선별한 예시와 주석을 살펴볼 수 있다. 데이터셋 카드는 공개된 10만 시간 분량과 파일 형식을 설명한다.

## 에피소드 구성 읽기

![꽃 줄기 묶기 에피소드의 NVIDIA Human-1M 공식 구성도](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K/resolve/main/figures/card_episode_anatomy.png)

꽃 줄기 묶기 예제에서는 머리와 손목 카메라, 재구성된 장면, 머리와 손 궤적, 작업 목표(T1), 시간 구간별 세부 동작(T2)을 같이 본다. 이 그림은 손목 카메라가 있는 스테레오 예시다. 촬영 장비 구성에 따라 사용할 수 있는 카메라는 달라진다. [데이터셋 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K#anatomy-of-an-episode) · [공식 Explorer](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer)

![Human-1M Explorer의 3D 작업 지도](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer/resolve/main/figures/task_landscape_3d.png)

작업 지도에서는 설명 임베딩의 유사도로 관련 작업을 찾는다. 관심 있는 작업을 선택한 뒤 개별 에피소드에서 실제 동작과 사용 물체가 찾던 데이터인지 확인한다. [공식 작업 탐색기](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer#semantic-map)

## 활용 예시 — 손과 도구의 상호작용 모으기

조립과 수리 작업을 검색한다. 표본에서 T2 구간과 MP4 타임스탬프를 맞추고 가려지는 지점의 양손을 살펴본다. 프레임 데이터의 자세 추정 신뢰도와 추적 마스크를 확인한다. LeRobot v3 샤드는 영상, Parquet 프레임 행, 에피소드 메타데이터가 분리돼 있다. 에피소드마다 카메라나 길이가 다를 수 있으므로 메타데이터와 시간으로 연결한다. 로봇에 적용할 때는 로봇 구조와 접촉 제약에 맞게 동작을 다시 매핑하는 단계가 필요하다. [공식 스키마](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K/blob/main/SCHEMA.md) · [품질 기준](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K#quality-at-every-step)
