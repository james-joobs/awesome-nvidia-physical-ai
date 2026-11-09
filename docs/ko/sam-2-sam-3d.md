# SAM 2 / SAM 3D Objects

[← 전체 목록](../../README.ko.md) · [English](../en/sam-2-sam-3d.md) · [공식 소스](https://github.com/facebookresearch/sam2) · [공식 문서 / 관련 프로젝트](https://github.com/facebookresearch/sam-3d-objects)

Meta의 프롬프트 기반 이미지·영상 분할 모델 SAM 2와 3D 물체 복원 모델 SAM 3D Objects입니다.

**공개 및 이용 조건:** SAM 2 코드와 모델 조건은 각각 확인하세요. SAM 3D Objects 코드와 체크포인트는 SAM License가 적용되며 의존성 조건도 확인해야 합니다.

![SAM 2 / SAM 3D Objects official illustration](https://raw.githubusercontent.com/facebookresearch/sam2/main/assets/model_diagram.png)

*이미지 출처: [공식 프로젝트 저장소](https://github.com/facebookresearch/sam2). 원본의 재사용 조건을 확인하세요.*

## 구성과 활용 흐름

```mermaid
flowchart LR
    A["이미지·영상 + 프롬프트"] --> B["분할 마스크"] --> C["선택적 3D 복원"] --> D["검토"]
```

*이 안내서의 개념도이며, 지원 구현은 공식 자료를 확인하세요.*

점·박스 등 지원되는 프롬프트로 물체를 선택해 마스크를 생성하고 검토합니다. 별도의 SAM 3D Objects 흐름은 이미지와 마스크를 사용해 물체를 복원할 수 있습니다.

## 활용 사례

영상 프레임의 물체 분할이나 장면 이해를 위한 3D 물체 복원에 활용할 수 있습니다.

## 연계 기술

Grounding DINO의 박스를 입력으로 활용할 수 있습니다. 두 모델은 별도이며 자동으로 연결되는 단일 파이프라인은 아닙니다.

## 공식 자료

- [프로젝트 자료](https://github.com/facebookresearch/sam2)
- [공식 문서 / 관련 프로젝트](https://github.com/facebookresearch/sam-3d-objects)
