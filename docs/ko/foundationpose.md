# FoundationPose

[← 전체 목록](../../README.ko.md) · [English](../en/foundationpose.md)

FoundationPose는 학습 때 보지 못한 물체의 6D 자세를 추정하고 추적합니다. CAD 메시나 참조 영상이 대상 물체의 형상 정보를 제공합니다.

![FoundationPose 기법 구성도](https://nvlabs.github.io/FoundationPose/static/images/pipeline.jpg)

*메시와 참조 시점 경로는 후보 보정과 점수 계산 전에 하나로 합쳐집니다.* [공식 그림 출처](https://nvlabs.github.io/FoundationPose/)

![FoundationPose 연구 결과](https://nvlabs.github.io/FoundationPose/static/images/intro.jpg)

*추정 자세와 형상이 영상에 맞는지 확인할 때 참고할 수 있는 결과입니다.* [공식 그림 출처](https://nvlabs.github.io/FoundationPose/)

## 어떻게 동작하나

모델 기반 경로는 메시를 렌더링합니다. 논문의 모델 없는 경로는 물체 중심 신경장으로 참조 관측에서 새로운 RGB-D 시점을 렌더링합니다. 이후 두 경로 모두 자세 후보 생성, 관측과 비교해 후보 보정, 점수 계산과 선택 순서로 동작합니다. 추적은 이전 프레임의 자세를 시작점으로 사용합니다.

## 실전 워크플로

보정된 RGB-D 시퀀스, 물체 마스크, 실제 크기에 맞는 메시를 준비합니다. 초기 자세의 렌더링 실루엣을 RGB 위에 겹칩니다. 프레임 간 추적을 시험하고 의도적으로 물체를 가려 언제 초기화할지 정합니다. 로봇에 적용할 때는 물체에서 카메라로의 변환을 로봇 베이스 기준으로 바꿔 파지를 계산합니다.

## 검증할 항목

측정 자세나 고정구를 기준으로 사용합니다. 마스크, 깊이 단위, 메시 원점, 카메라 내부 파라미터와 물체 대칭성을 확인합니다. 초기 추정 실패와 추적 실패를 구분해 기록합니다.

## 공개 범위와 라이선스

연구 저장소 코드는 비상업적 사용 제한; 별도 배포 모델은 별도 조건. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [연구 프로젝트, 아키텍처와 예제](https://nvlabs.github.io/FoundationPose/)
- [FoundationPose 논문](https://arxiv.org/abs/2312.08344)
- [관련 공식 자료 · github.com](https://github.com/NVlabs/FoundationPose)
- [관련 공식 자료 · huggingface.co](https://huggingface.co/nvidia/foundationpose)
