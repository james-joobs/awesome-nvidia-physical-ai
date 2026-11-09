# SimReady Central Library

[← 전체 목록](../../README.ko.md) · [English](../en/simready-central-library.md)

SimReady Central Library는 기여된 시뮬레이션 에셋을 찾는 인터페이스다. 작업이나 메타데이터를 기준으로 에셋을 찾은 뒤 소유자의 데이터셋에서 버전 패키지를 가져올 수 있다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| 소유자 호스팅 데이터셋 | 에셋 소유자가 Hugging Face 네임스페이스에 OpenUSD 패키지를 발행하고 버전을 관리한다. 데이터셋 카드와 패키지가 이용 조건과 지원 프로파일을 설명한다. |
| 검색과 미리보기 | 브라우저와 USD Search가 색인된 USD 및 에셋 메타데이터로 패키지를 찾는다. 미리보기로 가져와 합성하기 전 시각적 적합성을 살펴볼 수 있다. |
| 장면 구성과 런타임 | 사용자가 정확한 리비전을 골라 참조나 페이로드로 OpenUSD 장면에 합성한다. 대상 시뮬레이터가 작성된 물리 또는 센서 메타데이터를 해석한다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    dataset["소유자별 버전 데이터셋"]
    index["검토된 에셋 메타데이터"]
    query["작업과 프로파일 검색 조건"]
    search["라이브러리와 USD Search"]
    pick["정확한 에셋과 리비전"]
    scene["OpenUSD 작업 셀 또는 공장 스테이지"]
    dataset --> index
    index --> search
    query --> search
    search --> pick
    dataset --> pick
    pick --> scene
```

### 공식 그림과 예시

![NVIDIA 생태계 그림은 소유자 데이터셋을 USD 검색과 시뮬레이션 제작 흐름에 연결한다.](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/13KvGj5W3O3D8TX5bEcLn.png)

NVIDIA 생태계 그림은 소유자 데이터셋을 USD 검색과 시뮬레이션 제작 흐름에 연결한다. [그림 출처와 원문 설명](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories)

![공식 AI 공장 사례는 장비 에셋을 참조해 배치 대안과 통로 간격을 비교한다.](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/2_TJVBkaoK6wo1R0FsfES.png)

공식 AI 공장 사례는 장비 에셋을 참조해 배치 대안과 통로 간격을 비교한다. [그림 출처와 원문 설명](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories)

## 워크플로 예시

1. 로봇 작업 셀이라면 로봇팔, 호환 그리퍼, 팔레트, 대상 물체를 검색한다. 버전을 고르기 전에 프로파일과 이용 조건을 읽는다.
2. 선택한 에셋을 USD 장면에서 참조하고 장착 위치와 좌표계를 맞춘다. 파지와 도달 범위를 시험한다. 공장 배치라면 랙 간격과 겹침을 별도 조건으로 확인한다.
3. 다른 사람도 작업 셀을 재현하도록 데이터셋 리비전과 런타임 버전을 기록한다. 관련 배치나 작업 조건만 바꿔 두 번째 장면과 비교한다.

## 검증 포인트

- 목록을 공개로 볼 수 있어도 개별 에셋 라이선스를 확인한다. 검색 결과에 비상업적 에셋이 포함될 수 있다.
- USD 메타데이터나 렌더 미리보기와 별도로 호환성을 시험한다. 기하 단위, 관절 구조, 재질과 필요한 프로파일을 확인한다.

## 라이선스와 범위

라이브러리는 공개 탐색할 수 있다. 호스팅된 에셋 패키지마다 접근·재사용 조건이 다르다.

## 관련 가이드

[SimReady Central](simready-central.md) · [SimReady](simready.md) · [OpenUSD](openusd.md) · [Isaac Sim](isaac-sim.md)

## 공식 자료

- [SimReady Central Library 공식 문서](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html)
- [공식 라이브러리 브라우저](https://huggingface.co/spaces/nvidia/simready-central)
- [라이브러리 데이터셋 카드와 기여 절차](https://huggingface.co/datasets/nvidia/simready-central-library)
- [공식 작업 셀·AI 공장 사례](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories)
