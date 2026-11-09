# FoundationPose

[← 전체 목록](../../README.ko.md) · [English](../en/foundationpose.md)

![FoundationPose pose estimation demo](https://raw.githubusercontent.com/NVlabs/FoundationPose/main/assets/demo.jpg)

이미지: 아래 공식 프로젝트 출처.

## 소개

물체 6D 자세 추정·추적 연구 코드·모델.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["물체 관측과 모델 정보 제공"] --> n1
    n1["6D 자세 추정"] --> n2
    n2["프레임 간 추적"] --> n3
    n3["로봇 조작에 활용"]
```

## 활용 흐름과 사례

물체 관측과 모델 정보 제공 → 6D 자세 추정 → 프레임 간 추적 → 로봇 조작에 활용. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 로봇 파지를 위한 물체 추적. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac ROS Pose Estimation.

## 구성과 실제 활용

FoundationPose는 모델 기반과 모델 없는 방식의 6D 물체 자세 추정·추적을 지원합니다. CAD 모델 또는 소수의 참조 영상으로 물체 정보를 제공하고, 로봇은 추정 자세를 조작 실험에 사용할 수 있습니다. 연구 저장소와 별도 배포 모델의 약관은 서로 다를 수 있습니다.

[공식 문서](https://github.com/NVlabs/FoundationPose)

## 공개 및 이용 조건

연구 저장소 코드는 비상업적 사용 제한; 별도 배포 모델은 별도 조건. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[코드](https://github.com/NVlabs/FoundationPose) · [모델 카드](https://huggingface.co/nvidia/foundationpose)
