# SigLIP 2

[← 전체 목록](../../README.ko.md) · [English](../en/siglip-2.md) · [공식 소스](https://huggingface.co/google/siglip2-base-patch16-224) · [공식 문서 / 관련 프로젝트](https://huggingface.co/google/siglip2-base-patch16-224)

이미지와 텍스트를 표현해 교차 모달 작업에 활용하는 Google 비전·언어 모델 계열입니다.

**공개 및 이용 조건:** 모델 카드와 체크포인트별 라이선스를 확인하고 대상 데이터에 대한 한계와 편향을 평가하세요.

## 구성과 활용 흐름

```mermaid
flowchart LR
    A["이미지 + 텍스트"] --> B["각 인코더"] --> C["임베딩 / 유사도"] --> D["순위화"]
```

*이 안내서의 개념도이며, 지원 구현은 공식 자료를 확인하세요.*

체크포인트의 전처리기로 이미지와 후보 텍스트를 준비하고 임베딩이나 점수를 계산해 검색 또는 분류합니다. 영상은 보통 프레임을 추출해 처리하므로 해당 파이프라인을 확인해야 합니다.

## 활용 사례

제로샷 이미지 분류와 이미지·텍스트 검색에 사용할 수 있습니다.

## 연계 기술

임베딩은 영상 수집·라벨링 시스템과 함께 데이터 선별이나 검색에 활용할 수 있습니다.

## 공식 자료

- [프로젝트 자료](https://huggingface.co/google/siglip2-base-patch16-224)
- [공식 문서 / 관련 프로젝트](https://huggingface.co/google/siglip2-base-patch16-224)
