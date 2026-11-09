# NeMo Data Designer

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-data-designer.md)

스키마와 시드 데이터를 이용한 합성 데이터 생성.

![Data Designer 아키텍처](https://arxiv.org/html/2609.17699v1/figures/ndd_architecture_diagram.png)

기술 보고서의 그림에서 데이터셋 설정이 생성 시스템을 거쳐 처리되는 과정을 확인할 수 있습니다. [공식 그림 출처](https://arxiv.org/html/2609.17699)

## 아키텍처와 데이터 흐름

열마다 레코드 생성 규칙을 정의합니다. 샘플러 열은 기본값을 만들고, 생성 열은 다른 필드나 시드 행을 참조할 수 있습니다. 검증기가 결과를 검사합니다. 모델을 사용하는 열은 설정에 따라 멀티모달 문맥과 도구 호출을 활용할 수 있습니다. 엔진은 명세의 의존 관계를 따라 실행하고 검토할 산출물을 기록합니다.

## 물리 AI 활용 예시

창고 클립 목록과 기준 이벤트 시각에서 질의응답 후보를 생성합니다. 원본 클립 ID와 생성 라벨 표시를 보존합니다. 영상 길이 밖의 타임스탬프나 정의되지 않은 이벤트를 제외하고, 사람이 질문과 답변을 영상과 대조합니다.

## 검증할 항목

스키마와 함께 출처와 데이터 분포를 검증합니다. 생성한 질의와 라벨은 영상 픽셀이나 시뮬레이터 정답과 구분해 기록합니다. 공급자, 모델, 시드 데이터, 플러그인 조건을 확인합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/DataDesigner)
- [공식 문서](https://docs.nvidia.com/nemo/datadesigner)
- [기술 보고서와 그림](https://arxiv.org/html/2609.17699)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/DataDesigner/blob/HEAD/LICENSE)

## 관련 가이드

[Cosmos Data Factory](cosmos-data-factory.md) · [CDF Auto Labeling](cdf-auto-labeling.md)
