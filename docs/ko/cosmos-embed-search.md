# Cosmos Embed / Dataset Search

[← 전체 목록](../../README.ko.md) · [English](../en/cosmos-embed-search.md)

Cosmos Dataset Search(CDS)는 대규모 영상·텍스트 모음을 색인하고 후보 클립을 찾아준다. Cosmos Embed NIM은 지원되는 텍스트와 영상 입력을 같은 벡터 공간에 표현한다.

## 공식 서비스 구성도 읽기

![NVIDIA Cosmos Dataset Search 구성도](https://docs.nvidia.com/cosmos/cds/latest/_images/cds_system_overview.png)

| 계층 | 역할 |
|---|---|
| 코어 서비스와 색인 | 입력을 수집하고 데이터 볼륨과 버전에 대응하는 색인을 생성 |
| Cosmos Embed NIM | 클립과 텍스트 질의를 비교 가능한 벡터로 변환 |
| Milvus | 벡터를 저장하고 가까운 후보를 검색 |
| PostgreSQL | 컬렉션 메타데이터와 저장소 구성 기록 |
| 검색과 UI | 선택한 볼륨과 색인에 질의하고 결과 파일을 사용자에게 표시 |

색인 경로는 저장된 미디어에서 이름이 붙은 색인으로 이어진다. 검색 경로는 질의에서 가까운 벡터를 찾아 해당 원본 파일로 연결한다. 검색 결과가 이상할 때는 색인 갱신 문제, 순위 문제, 파일 접근 문제를 이 흐름에 따라 나눠 확인한다. [NVIDIA CDS 아키텍처](https://docs.nvidia.com/cosmos/cds/latest/introduction.html) · [Docker Compose 배포 문서](https://docs.nvidia.com/cosmos/cds/latest/docker-compose-deployment.html)

## 활용 예시 — 보행자 근접 사고 후보 검색

사용 권한이 있는 영상 모음을 색인하고 주차 차량 뒤에서 횡단보도로 진입하는 보행자를 찾는다. 상위 검색 결과를 사람이 분류한 소규모 표본과 비교한다. 짧은 사건이 클립 경계에 걸칠 수 있으므로 순위와 함께 타임스탬프를 확인한다. 클립 분할 기준이나 임베딩 체크포인트가 달라지면 새 색인 버전을 만든다. 검색 결과를 정답 라벨로 쓰기 전에 시간 구간을 다루는 모델이나 사람 검토로 확인한다. [공식 저장소](https://github.com/NVIDIA-Omniverse-blueprints/cosmos-dataset-search) · [Cosmos Reason2](cosmos-reason2.md)

사용할 CDS와 NIM 버전의 배포 절차와 서비스 조건을 공식 문서에서 확인한다. [NVIDIA 공식 문서](https://docs.nvidia.com/cosmos/cds/latest/introduction.html)
