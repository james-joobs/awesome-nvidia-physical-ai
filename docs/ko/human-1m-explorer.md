# Human-1M Explorer

[전체 목록](../../README.ko.md) · [English](../en/human-1m-explorer.md)

사람의 일인칭 촬영과 재구성 예시를 탐색하는 도구다.

**공식 출처:** [Hugging Face Space](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer)

**라이선스 및 공개 여부:** Space 공개; 데이터셋 접근과 약관은 별도. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["예시 탐색"]
  S1["제공 모달리티 확인"]
  S2["데이터셋 카드와 사용 조건 확인"]
  S3["데이터 선택"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

체화 AI 연구에 사용할 사람 동작 예시를 살펴본다.

## 연결 기술

Human-1M, Hugging Face, Video-to-Data. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
