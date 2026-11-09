# Cosmos Embed / Dataset Search

[← 전체 목록](../../README.ko.md) · [English](../en/cosmos-embed-search.md)

## 소개

멀티모달 임베딩 모델·서비스 및 영상 검색 마이크로서비스.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["영상 컬렉션 준비"] --> n1
    n1["임베딩 생성"] --> n2
    n2["멀티모달 질의로 검색"] --> n3
    n3["검색된 클립 확인"]
```

## 활용 흐름과 사례

영상 컬렉션 준비 → 임베딩 생성 → 멀티모달 질의로 검색 → 검색된 클립 확인. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 영상 아카이브에서 관련 장면 검색. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Cosmos Curator, Cosmos.

## 구성과 구체적인 활용

Dataset Search는 수집·검색 코어 서비스, Cosmos Embed NIM, Milvus 벡터 저장소, Postgres 메타데이터와 웹 UI를 조합한다. 영상과 텍스트를 인덱싱하고 임베딩으로 검색한다.

주행 영상을 인덱싱하고 상황을 의미 검색한 다음, 결과를 검토해 데이터셋에 선별한다.

[공식 기술 자료](https://docs.nvidia.com/cosmos/cds/latest/introduction.html)

## 공개 및 이용 조건

서비스·모델의 전체 소스 및 라이선스 미확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[공식 문서](https://docs.nvidia.com/cosmos/cds/latest/introduction.html)
