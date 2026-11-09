# FoundationStereo

[← 전체 목록](../../README.ko.md) · [English](../en/foundationstereo.md)

![FoundationStereo stereo depth output](https://raw.githubusercontent.com/NVlabs/FoundationStereo/master/teaser/output.jpg)

이미지: 아래 공식 프로젝트 출처.

## 소개

스테레오 깊이 추정 연구 코드·모델.

## 개념적 워크플로

```mermaid
flowchart LR
    n0["스테레오 이미지 쌍 촬영"] --> n1
    n1["깊이 추정"] --> n2
    n2["기하 결과 검토"] --> n3
    n3["후속 인식에 활용"]
```

## 활용 흐름과 사례

스테레오 이미지 쌍 촬영 → 깊이 추정 → 기하 결과 검토 → 후속 인식에 활용. 개념적인 흐름이며 버전별 사전 요구사항과 지원 구성은 공식 문서를 확인한다.

**활용 사례:** 카메라 쌍을 통한 장면 깊이 추정. 지원 입력과 모델 버전은 공식 출처에서 확인한다.

**연결 기술:** Isaac ROS DNN Stereo Depth.

## 구성과 실제 활용

FoundationStereo는 스테레오 영상 쌍에서 조밀한 시차 지도를 생성합니다. 카메라 보정 정보를 이용하면 실제 단위의 깊이나 3D 포인트 클라우드로 변환할 수 있습니다. 예를 들어 로봇 인식용 장면 깊이를 확인할 수 있으며 연구 코드와 상용 배포 모델의 조건은 구분해야 합니다.

[공식 문서](https://github.com/NVlabs/FoundationStereo)

## 공개 및 이용 조건

연구 코드 비상업적 제한; 별도 상업용 모델 제공 여부와 조건은 해당 배포물 확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 출처

[저장소](https://github.com/NVlabs/FoundationStereo)
