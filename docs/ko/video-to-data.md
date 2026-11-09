# Video-to-Data (V2D)
[← 목록으로](../../README.ko.md) · [English](../en/video-to-data.md)

영상의 장면·동작을 복원하고 로봇 학습에 연결하는 파이프라인.

**공식 자료:** [저장소](https://github.com/nvidia-isaac/video_to_data)  
**라이선스와 범위:** 소스 Apache-2.0, 문서·스킬 CC-BY-4.0; 의존 모델 별도.

![Video-to-Data pipeline diagram](https://raw.githubusercontent.com/nvidia-isaac/video_to_data/main/docs/figures/v2d_overview.png)
*이미지 출처: [Repository](https://github.com/nvidia-isaac/video_to_data)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**영상 → 장면·동작 추출 및 복원 → 리타기팅 또는 내보내기 → 로봇 학습 데이터 검토**

## 활용 사례

사람의 영상에서 로봇 손 조작 학습에 활용할 수 있는 표현을 생성합니다.

## 연결 기술

Isaac Capture, Isaac Lab, GR00T.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
