# TensorRT public code

[전체 목록](../../README.ko.md) · [English](../en/tensorrt.md)

TensorRT 저장소는 추론 최적화 예제·플러그인·도구를 제공하며 배포 SDK에는 별도 조건이 적용된다.

**공식 출처:** [Repository](https://github.com/NVIDIA/TensorRT)

**라이선스 및 공개 여부:** Repository: Apache-2.0; this does not cover the entire TensorRT binary SDK. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

## 워크플로우

아래는 이해를 돕기 위한 개념도이며 공식 아키텍처 도면이 아니다.

```mermaid
flowchart LR
  S0["학습된 모델 준비"]
  S1["대상 하드웨어에 맞춰 최적화"]
  S2["수치 결과 검증"]
  S3["추론 배포"]
  S0 --> S1 --> S2 --> S3
```

## 활용 사례

인식 또는 로봇 정책 애플리케이션의 추론 지연을 줄인다.

## 연결 기술

CUDA, ONNX, Isaac ROS, Jetson. 실제 호환성과 실행 요건은 각 버전의 공식 문서를 확인한다.
