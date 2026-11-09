# CUDA / TensorRT / ONNX

[← 전체 목록](../../README.ko.md) · [English](../en/cuda-tensorrt-onnx.md)

CUDA, TensorRT와 ONNX는 배포의 서로 다른 계층입니다. CUDA는 가속 연산, TensorRT는 추론 엔진 빌드와 실행, ONNX는 이식 가능한 모델 그래프의 표현을 담당합니다.

![ONNX 예제 모델 그래프](https://onnx.ai/onnx/_images/linreg1.png)

*간단한 공식 예제로 입력, 상수, 연산자가 모델 계산을 정의하는 방식을 볼 수 있습니다.* [공식 그림 출처](https://onnx.ai/onnx/intro/concepts.html)

## 어떻게 동작하나

ONNX 그래프에는 텐서, 연산자, 초기값과 연산자 집합 버전이 들어갑니다. 호환 TensorRT 파서가 네트워크를 만들고 빌더가 대상 구현을 선택해 엔진을 생성합니다. 실행에는 장치 버퍼와 CUDA 스트림을 사용합니다. 전처리와 출력 텐서의 해석은 애플리케이션에서 수행합니다.

## 실전 워크플로

모델을 내보내고 고정 입출력 예제를 저장합니다. 호환 런타임에서 ONNX를 실행해 원래 프레임워크와 대조한 뒤 TensorRT 엔진 결과를 비교합니다. 불일치가 내보내기와 엔진 실행 중 어디서 시작했는지 구분할 수 있습니다.

## 검증할 항목

연산자와 입력 형상 지원, 플러그인, 정밀도와 장치 호환성을 확인합니다. 그래프와 함께 클래스 라벨 및 변환도 보관합니다. CUDA와 TensorRT 배포 약관을 각각 확인합니다.

## 공개 범위와 라이선스

ONNX 코드와 사양의 조건을 확인하세요. CUDA·TensorRT 배포판, 드라이버와 제3자 구성 요소에는 별도 조건이 적용됩니다.

## 공식 자료

- [공식 기술 자료](https://onnx.ai/onnx/intro/concepts.html)
- [TensorRT 빌드와 런타임](https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/how-trt-works.html)
- [관련 공식 자료 · github.com](https://github.com/onnx/onnx)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/tensorrt)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/cuda-toolkit)
- [관련 공식 자료 · onnx.ai](https://onnx.ai/)
