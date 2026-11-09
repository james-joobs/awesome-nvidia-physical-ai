# DeepStream

[← 전체 목록](../../README.ko.md) · [English](../en/deepstream.md)

DeepStream은 GStreamer 플러그인 그래프로 영상 스트림을 가속 처리합니다. 노드 사이에는 영상 버퍼와 메타데이터가 전달됩니다.

![DeepStream 그래프 아키텍처](https://docs.nvidia.com/deepstream/_fern-files/_img/5fdf8ab2ed4a2aeaffbd54df8069478f95071121dbf460cf0ebff3a293da95e2.webp)

*GStreamer 플러그인과 아래에 표시된 가속 엔진을 비교해 보세요. 영상 처리 단계와 결과를 받는 출력 단계가 분리되어 있습니다.* [공식 그림 출처](https://docs.nvidia.com/deepstream/text/DS_Overview)

## 어떻게 동작하나

RTSP 애플리케이션에서는 소스와 하드웨어 디코더가 프레임을 만듭니다. `nvstreammux`가 소스별 프레임을 배치로 묶고, `nvinfer` 또는 Triton 통합이 추론 후 메타데이터를 붙입니다. 추적기가 지속 ID를 붙일 수 있고, 이후 분기에서 오버레이, 메타데이터 발행 또는 영상 인코딩을 수행합니다. 호환 경로에서는 GPU 버퍼를 유지해 프레임을 CPU에 복사하는 비용을 줄일 수 있습니다.

### 구성 요소별 입출력

| 구성 요소 | 입력 | 출력 |
|---|---|---|
| 소스와 디코더 | RTSP 스트림, 로컬 파일 또는 카메라 | 디코딩한 영상 버퍼 |
| 배치와 추론 | 프레임과 모델 구성 | 탐지값 또는 텐서가 담긴 배치 메타데이터 |
| 추적과 출력 | 프레임, 탐지값과 소스 ID | 추적 ID, 오버레이, 메타데이터 또는 인코딩 영상 |

## 실전 워크플로

시설 탐지기에 카메라 두 대를 연결합니다. 오버레이 영상에서 카메라별 타임스탬프와 ID를 확인한 뒤 하위 애플리케이션으로 객체 메타데이터를 보냅니다. 배치를 늘리거나 느린 스트림을 추가했을 때 카메라별 프레임 지연을 측정합니다.

## 검증할 항목

디코딩, 배치 대기, 전처리, 추론, 출력을 따로 측정합니다. 카메라 연결 해제와 복구 동작, 분기별 타임스탬프 의미를 확인합니다. 탐지값을 이벤트로 사용하기 전에 모델 클래스와 좌표 변환을 검증합니다.

## 공개 범위와 라이선스

제품 SDK; 공개 샘플과 바이너리의 조건 별도. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://docs.nvidia.com/deepstream/text/DS_Overview)
- [관련 공식 자료 · docs.nvidia.com](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Overview.html)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/deepstream-sdk)
