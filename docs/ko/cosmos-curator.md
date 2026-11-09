# Cosmos Curator

[전체 목록](../../README.ko.md) · [English](../en/cosmos-curator.md)

Cosmos Curator는 원본 영상에서 필요한 클립을 고르고 주석을 달아 데이터셋을 만든다. 큐레이션 레시피에 처리 단계를 지정하면 Cosmos-Xenna가 Ray 워커로 실행한다.

## 논리 구조와 실제 배치

![Cosmos Curator 공식 논리 구조](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-logical-view.png)

논리 구성도에서 각 단계는 상태를 유지하는 Ray 액터 풀을 사용한다. 영상 디코딩과 분할 결과를 필터, 캡션, 임베딩, 결과 기록으로 넘길 수 있다. 드라이버는 데이터의 참조로 다음 작업을 예약한다. 워커는 실제 입력이 필요할 때 참조가 가리키는 데이터를 불러온다. [공식 논리 구조](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#logical-view)

![Cosmos Curator 공식 물리 구조](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-physical-view.png)

물리 구성도에는 여러 노드의 워커와 객체 저장소가 나온다. 다음 단계는 같은 노드 또는 다른 노드에서 데이터를 읽을 수 있다. 스케줄러는 데이터가 가까운 워커를 우선할 수 있고, 단계별 처리율과 필요한 자원에 따라 워커 풀을 조정한다. [공식 물리 구조](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#physical-view)

## 활용 예시 — 로봇 조작 영상 아카이브 선별

긴 영상 몇 개를 클립으로 나눠 움직임과 영상 품질을 기준으로 선별한다. 통과한 영상에는 원본 영상 ID, 클립 시작과 끝, 캡션이나 임베딩 결과를 남긴다. 각 임계값 전후의 샘플을 비교해 필요한 장면이 빠지는지 확인한다. 캡션 단계 앞에 클립이 쌓이면 디코더를 늘리기 전에 해당 단계의 처리율과 GPU 할당을 확인한다. 원본 영상 단위로 학습과 평가를 나누면 겹치는 장면이 양쪽에 섞이는 것을 줄일 수 있다. [공식 파이프라인과 문서](https://github.com/NVIDIA/cosmos-curator#documentation)

코드는 Apache-2.0이다. 모델 및 저장소 접근 조건은 별도로 확인한다. [공식 라이선스](https://github.com/NVIDIA/cosmos-curator#license-and-contact)
