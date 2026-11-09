# PyTorch

[← 전체 목록](../../README.ko.md) · [English](../en/pytorch.md) · [공식 소스](https://github.com/pytorch/pytorch) · [공식 문서 / 관련 프로젝트](https://docs.pytorch.org/docs/stable/index.html)

텐서 계산과 자동 미분을 제공하는 오픈소스 머신러닝 프레임워크입니다.

**공개 및 이용 조건:** PyTorch는 BSD 계열 라이선스이며 모델·패키지·CUDA 런타임 등 의존성의 조건은 별도입니다.

![PyTorch official illustration](https://raw.githubusercontent.com/pytorch/pytorch/main/docs/source/_static/img/tensor_illustration.png)

*이미지 출처: [공식 프로젝트 저장소](https://github.com/pytorch/pytorch). 원본의 재사용 조건을 확인하세요.*

## 구성과 활용 흐름

```mermaid
flowchart LR
    A["데이터"] --> B["텐서와 모델"] --> C["학습 / 추론"] --> D["결과"]
```

*이 안내서의 개념도이며, 지원 구현은 공식 자료를 확인하세요.*

데이터를 텐서로 불러오고 모델과 손실을 정의한 뒤 자동 미분으로 학습하고 결과를 평가하거나 내보냅니다.

## 활용 사례

비전 모델, 로봇 정책, 물리 기반 모델 학습에 활용할 수 있습니다.

## 연계 기술

생태계의 여러 모델과 도구가 PyTorch를 사용하며 지원되는 배포 경로에서 TensorRT를 활용할 수 있습니다.

## 공식 자료

- [프로젝트 자료](https://github.com/pytorch/pytorch)
- [공식 문서 / 관련 프로젝트](https://docs.pytorch.org/docs/stable/index.html)
