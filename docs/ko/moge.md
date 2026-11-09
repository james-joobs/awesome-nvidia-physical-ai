# MoGe

[← 전체 목록](../../README.ko.md) · [English](../en/moge.md) · [공식 소스](https://github.com/microsoft/MoGe) · [공식 문서 / 관련 프로젝트](https://github.com/microsoft/MoGe)

한 장의 이미지에서 3D 기하를 추정하는 Microsoft 연구 모델 계열입니다.

**공개 및 이용 조건:** 각 모델 버전의 코드·체크포인트와 의존성 라이선스를 별도로 확인하세요.

## 구성과 활용 흐름

```mermaid
flowchart LR
    A["RGB 이미지"] --> B["기하 추정 모델"] --> C["깊이 / 포인트 맵"] --> D["기하 검토"]
```

*이 안내서의 개념도이며, 지원 구현은 공식 자료를 확인하세요.*

선택한 체크포인트로 이미지를 처리하고 깊이 또는 포인트 맵을 검토한 뒤 지원되는 기하 결과를 내보냅니다. 출력은 모델 버전별로 다릅니다.

## 활용 사례

대략적인 장면 기하 복원이나 후속 시각 공간 추론에 활용할 수 있습니다.

## 연계 기술

Video-to-Data와 복원 흐름의 입력이 될 수 있으나 단일 이미지 추정의 크기와 기하 오차를 검토해야 합니다.

## 공식 자료

- [프로젝트 자료](https://github.com/microsoft/MoGe)
- [공식 문서 / 관련 프로젝트](https://github.com/microsoft/MoGe)
