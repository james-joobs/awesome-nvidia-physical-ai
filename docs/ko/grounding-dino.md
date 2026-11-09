# Grounding DINO

[← 전체 목록](../../README.ko.md) · [English](../en/grounding-dino.md) · [공식 소스](https://github.com/IDEA-Research/GroundingDINO) · [공식 문서 / 관련 프로젝트](https://github.com/IDEA-Research/GroundingDINO)

텍스트 조건으로 물체를 탐지하는 IDEA Research의 모델입니다.

**공개 및 이용 조건:** 저장소 코드 라이선스, 체크포인트 조건과 제3자 구성 요소를 각각 확인하세요.

## 구성과 활용 흐름

```mermaid
flowchart LR
    A["이미지 + 텍스트 프롬프트"] --> B["탐지 모델"] --> C["박스와 점수"] --> D["후속 작업"]
```

*이 안내서의 개념도이며, 지원 구현은 공식 자료를 확인하세요.*

이미지와 물체 설명을 입력하고 추론한 뒤 점수 기준으로 후보 박스를 걸러 활용합니다.

## 활용 사례

라벨링을 위해 지정한 물체를 찾거나 분할 모델에 박스를 전달할 수 있습니다.

## 연계 기술

탐지 박스를 SAM 같은 분할 작업의 입력으로 사용할 수 있으며 정확도는 프롬프트와 데이터에 따라 달라집니다.

## 공식 자료

- [프로젝트 자료](https://github.com/IDEA-Research/GroundingDINO)
- [공식 문서 / 관련 프로젝트](https://github.com/IDEA-Research/GroundingDINO)
