# Cosmos Curator

[전체 목록](../../README.ko.md) · [English](../en/cosmos-curator.md)

Cosmos Curator는 원본 영상에서 필요한 클립을 고르고 주석을 달아 데이터셋을 만듭니다. 큐레이션 레시피에 처리 단계를 지정하면 Cosmos-Xenna가 Ray 워커로 실행합니다.

## 긴 영상이 검색·학습에 쓸 클립이 되기까지

### 원본 파일과 쓸 구간을 연결하기

Curator의 처리 단계를 골라 영상 분할, 품질 필터링, 주석 등을 구성합니다. 설명용 예시에서 `source_id=demo07`, `start_s=12.4`, `end_s=17.8`이면 원본의 5.4초 구간을 가리킵니다. 여기에 흐림 여부나 작업 설명을 붙이면 왜 남겼는지 이해하기 쉽습니다. 실제 단계별 필드 이름은 선택한 파이프라인에서 확인합니다.

### 필터가 남기는 것 확인하기

흔들림이 큰 영상이나 중복 구간을 줄이려는 기준이 빠르게 손을 움직이는 유용한 시연까지 제외할 수 있습니다. 설정을 바꿨을 때 통과율과 탈락 표본을 같이 보고, 같은 원본 영상에서 잘라낸 인접 구간이 학습·검증 쪽에 나뉘지 않도록 원본 ID로 분리합니다. [Cosmos Curator 공식 프로젝트](https://github.com/NVIDIA/cosmos-curator)

## 논리 구조와 실제 배치

![Cosmos Curator 공식 논리 구조](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-logical-view.png)

논리 구성도에서 각 단계는 상태를 유지하는 Ray 액터 풀을 사용합니다. 영상 디코딩과 분할 결과를 필터, 캡션, 임베딩, 결과 기록으로 넘길 수 있습니다. 드라이버는 데이터의 참조로 다음 작업을 예약합니다. 워커는 실제 입력이 필요할 때 참조가 가리키는 데이터를 불러옵니다. [공식 논리 구조](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#logical-view)

![Cosmos Curator 공식 물리 구조](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-physical-view.png)

물리 구성도에는 여러 노드의 워커와 객체 저장소가 나옵니다. 다음 단계는 같은 노드 또는 다른 노드에서 데이터를 읽을 수 있습니다. 스케줄러는 데이터가 가까운 워커를 우선할 수 있고, 단계별 처리율과 필요한 자원에 따라 워커 풀을 조정합니다. [공식 물리 구조](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#physical-view)

## 활용 예시 — 로봇 조작 영상 아카이브 선별

긴 영상 몇 개를 클립으로 나눠 움직임과 영상 품질을 기준으로 선별합니다. 통과한 영상에는 원본 영상 ID, 클립 시작과 끝, 캡션이나 임베딩 결과를 남깁니다. 각 임계값 전후의 샘플을 비교해 필요한 장면이 빠지는지 확인합니다. 캡션 단계 앞에 클립이 쌓이면 디코더를 늘리기 전에 해당 단계의 처리율과 GPU 할당을 확인합니다. 원본 영상 단위로 학습과 평가를 나누면 겹치는 장면이 양쪽에 섞이는 것을 줄일 수 있습니다. [공식 파이프라인과 문서](https://github.com/NVIDIA/cosmos-curator#documentation)

코드는 Apache-2.0입니다. 모델 및 저장소 접근 조건은 별도로 확인합니다. [공식 라이선스](https://github.com/NVIDIA/cosmos-curator#license-and-contact)

## 연관 도구

이 문서의 피지컬 AI 레시피와 [NeMo Curator](nemo-curator.md)의 범용 멀티모달 정제를 비교할 수 있습니다. 일부 파이프라인이 사용하는 단계 실행기는 [Cosmos Xenna](cosmos-xenna.md)를 참고하세요.
