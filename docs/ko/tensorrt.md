# TensorRT public code

[← 전체 목록](../../README.ko.md) · [English](../en/tensorrt.md)

TensorRT는 지원 신경망을 NVIDIA 장치에 맞는 추론 엔진으로 만들고 실행합니다. 공개 저장소에는 플러그인과 샘플, 관련 코드가 포함됩니다.

![TensorRT 객체 수명](https://docs.nvidia.com/deeplearning/tensorrt/latest/_images/trt-object-lifetimes.svg)

*빌드와 런타임 객체를 구분하고 어떤 객체가 자신을 참조하는 객체보다 오래 유지되어야 하는지 보여줍니다.* [공식 그림 출처](https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/how-trt-works.html)

## 어떻게 동작하나

빌드 단계에서 파서 또는 네트워크 정의가 계층, 형상, 데이터 타입을 기술합니다. 빌더는 연산 구현 후보를 평가하고 직렬화된 엔진을 생성합니다. 런타임에서는 실행 컨텍스트가 실행 상태와 필요한 런타임 형상을 관리합니다. 애플리케이션이 버퍼를 연결하고 CUDA 스트림에 작업을 넣습니다. 필요한 구현이 있으면 플러그인으로 지원 연산을 확장할 수 있습니다.

### 구성 요소별 입출력

| 구성 요소 | 입력 | 출력 |
|---|---|---|
| 빌드 | 모델 그래프, 최적화 프로파일, 정밀도와 플러그인 | 호환 대상용 직렬화 엔진 |
| 로드 | 엔진 파일과 호환 런타임 | 역직렬화 엔진과 실행 컨텍스트 |
| 실행 | 입력 버퍼, 런타임 형상과 CUDA 스트림 | 애플리케이션 후처리용 출력 버퍼 |

## 실전 워크플로

로봇 탐지기를 ONNX로 내보내고 배포 입력 크기에 맞춰 엔진을 빌드합니다. 같은 입력으로 학습 프레임워크의 원시 출력과 비교합니다. 워밍업 뒤 추론 지연과 전체 파이프라인 지연을 각각 측정합니다.

## 검증할 항목

런타임과 대상 GPU의 호환성, 정밀도, 동적 입력 크기와 플러그인을 확인합니다. 낮은 정밀도에서는 지연과 함께 응용 정확도와 드문 실패 사례를 확인합니다. 대상이나 런타임이 호환되지 않으면 엔진 재빌드가 필요합니다.

## 공개 범위와 라이선스

Repository: Apache-2.0; this does not cover the entire TensorRT binary SDK. 모델, 데이터, 의존성 및 배포 서비스에는 별도 조건이 적용될 수 있으므로 사용 전 각 출처를 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/how-trt-works.html)
- [관련 공식 자료 · github.com](https://github.com/NVIDIA/TensorRT)
