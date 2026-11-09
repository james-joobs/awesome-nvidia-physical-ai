# NeMo Retriever Library

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-retriever.md)

멀티모달 문서 추출·색인과 근거 검색.

![NeMo Retriever 추출 파이프라인](https://docs.nvidia.com/nemo/retriever/extraction/images/overview-extraction.png)

원본 파일을 검색에 사용할 데이터와 메타데이터로 변환하는 추출 흐름입니다. [공식 그림 출처](https://docs.nvidia.com/nemo/retriever/latest/)

## 아키텍처와 데이터 흐름

수집 단계는 텍스트, 표, 그림 또는 전사를 타입과 메타데이터가 있는 레코드로 추출합니다. 청킹과 임베딩으로 벡터를 저장할 수 있고, 질의와 재정렬을 거쳐 관련 레코드를 찾습니다. 선택 추론은 로컬 모델 또는 별도 NIM 엔드포인트를 사용할 수 있습니다. NVIDIA Ingest라는 이름도 사용됩니다.

## 물리 AI 활용 예시

장비 매뉴얼과 표준작업절차를 색인합니다. 사고 분석 에이전트는 VSS에서 시각이 있는 영상 근거를, Retriever에서 인용 가능한 정비 절차를 가져와 보고서에 함께 표시할 수 있습니다.

## 검증할 항목

문서 개정 버전, 페이지 출처와 검색 정확도를 확인합니다. 시각 이벤트 검색과 전사 검색의 입력 및 근거는 다릅니다. 호스팅 서비스와 모델 엔드포인트 조건을 확인합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA/NeMo-Retriever)
- [추출·수집 아키텍처](https://docs.nvidia.com/nemo/retriever/latest/)
- [VSS와 문서 RAG를 결합한 NVIDIA 사례](https://developer.nvidia.com/blog/?p=120054)
- [저장소 라이선스](https://github.com/NVIDIA/NeMo-Retriever/blob/HEAD/LICENSE)

## 관련 가이드

[Metropolis / VSS](metropolis-vss.md) · [NemoClaw](nemoclaw.md)
