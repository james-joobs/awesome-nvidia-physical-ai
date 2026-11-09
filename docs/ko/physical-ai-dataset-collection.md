# NVIDIA Physical AI dataset collection

[전체 목록](../../README.ko.md) · [English](../en/physical-ai-dataset-collection.md)

로봇, 자율주행 등 피지컬 AI 데이터셋을 찾는 NVIDIA 컬렉션이다.

**공식 출처:** [Collection](https://huggingface.co/collections/nvidia/physical-ai) · [All NVIDIA datasets](https://huggingface.co/nvidia/datasets)

**라이선스 및 공개 여부:** Dataset terms and access vary by entry. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["컬렉션 탐색"]
  S1["데이터셋 카드 확인"]
  S2["접근 권한과 라이선스 확인"]
  S3["호환 데이터 준비"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

로봇 학습, 월드 모델, 주행 평가용 데이터를 찾는다.

## 연결 기술

Hugging Face, Isaac GR00T, Cosmos. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
