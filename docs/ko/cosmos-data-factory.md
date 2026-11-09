# Cosmos Data Factory (CDF; formerly Physical AI Data Factory)

[전체 목록](../../README.ko.md) · [English](../en/cosmos-data-factory.md)

Cosmos Data Factory(CDF)는 참조 파이프라인과 조합 가능한 스킬을 제공한다. 선택한 블루프린트에 따라 검색, 시뮬레이션, 증강, 라벨링, 평가 도구 중 어떤 것을 쓸지 결정된다.

## 블루프린트 구성

![CDF 공식 영상 증강 워크플로](https://raw.githubusercontent.com/NVIDIA/cosmos-data-factory/main/docs/workflows/physical-ai-video-data-augmentation/media/main_workflow.png)

이 그림은 기존 영상이 장면 조건이 되는 영상 증강 블루프린트다. 자율주행 데이터 수집은 검색에서 시작할 수 있고, PCB 결함 생성은 렌더링한 부품에서 시작할 수 있다. [공식 블루프린트 소개](https://github.com/NVIDIA/cosmos-data-factory#reference-blueprints)

| 계층 | 책임 |
|---|---|
| 블루프린트 | 자율주행, 이벤트, 속성, 영상, 결함 생성의 입력과 실행 순서 및 구성을 정의 |
| 실행 | [CDF Orchestration](cdf-orchestration.md)이 Airflow 작업과 GPU 서비스를 실행. 이벤트 영상과 영상 증강은 공식 문서에 OSMO 경로도 있음 |
| 처리 | [Curator](cosmos-curator.md)와 [CDS](cosmos-embed-search.md)는 클립을 찾고, [Augmentation](cdf-augmentation.md)은 생성 엔드포인트를 호출. [Simulation](cdf-simulation.md)은 3D 장면을 렌더링하고, [Auto Labeling](cdf-auto-labeling.md)은 주석을 내보냄 |
| 평가 | [Cosmos Evaluator](cosmos-evaluator.md)의 검사 결과를 받아 학습에 포함할 변형을 선택 |

![CDF 공식 결함 이미지 생성 워크플로](https://raw.githubusercontent.com/NVIDIA/cosmos-data-factory/main/docs/workflows/physical-ai-defect-image-generation/media/dig_workflows.png)

빨간색 Day 0 경로는 USD와 부품 목록에서 시작해 기판을 렌더링하고 외관을 증강한다. 보라색 Day 1 경로는 정상 부품 사진을 AnomalyGen의 이미지 입력으로 사용한다. 그림 위쪽 후학습 경로에는 결함·마스크 쌍과 결함 명세가 들어간다. 구조 결함과 표면 결함이 서로 다른 경로로 Auto Labeling에 들어가는 점을 보면 라벨 후보가 어디서 만들어지는지 알 수 있다. [공식 결함 이미지 생성 가이드](https://github.com/NVIDIA/cosmos-data-factory/tree/main/docs/workflows/physical-ai-defect-image-generation)

## 활용 예시 — 드문 주행 상황 확장

원하는 상황을 잘 보여주는 클립에서 시작한다. 비슷한 실측 클립을 찾은 뒤 필요하면 RGB 영상이나 사전에 준비한 월드 시나리오 조건으로 날씨 변형을 생성한다. 같은 원본에서 만든 영상이 학습과 검증에 섞이지 않도록 원본 주행 ID 단위로 나눈다. 학습 전 움직임과 차선 기하를 검토하고, 통과 여부와 함께 모델 버전 및 제어 입력을 남긴다. [공식 자율주행 블루프린트](https://github.com/NVIDIA/cdf-orchestration/blob/main/docs/autonomous-vehicle-dataset-generation/getting-started.md)

입구 저장소는 코드 Apache-2.0, 문서와 스킬 CC-BY-4.0을 명시한다. 사용하는 구성 요소, 데이터셋, 모델 엔드포인트의 조건은 각각 확인한다. [공식 라이선스](https://github.com/NVIDIA/cosmos-data-factory#license)

## 연관 도구

[NeMo Data Designer](nemo-data-designer.md)는 클립 메타데이터를 바탕으로 구조화 레코드나 질문 후보를 생성할 수 있습니다. CDF는 영상 생성, 증강과 라벨링 워크플로를 제공합니다.
