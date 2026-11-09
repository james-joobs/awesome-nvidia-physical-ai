# SAM 2 / SAM 3D Objects

[← 전체 목록](../../README.ko.md) · [English](../en/sam-2-sam-3d.md)

SAM 2는 이미지와 영상에서 물체를 분할합니다. SAM 3D Objects는 영상 단서에서 물체의 3D 형상과 외관을 추정합니다. 재구성에서 두 모델이 맡는 단계가 다릅니다.

![SAM 2 모델과 메모리](https://raw.githubusercontent.com/facebookresearch/sam2/main/assets/model_diagram.png)

*프레임 특징과 메모리가 마스크 예측 경로로 들어가는 모습을 보세요.* [공식 그림 출처](https://github.com/facebookresearch/sam2)

![SAM 3D Objects 아키텍처](https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/main/doc/arch.png)

*목표 영역을 조건으로 3D 속성을 예측합니다. 출력이 SAM 2의 2D 마스크와 어떻게 다른지 확인하세요.* [공식 그림 출처](https://github.com/facebookresearch/sam-3d-objects)

## 어떻게 동작하나

**SAM 2.** 프롬프트 인코더가 점·박스를 표현하고 영상 인코더가 프레임 특징을 제공합니다. 마스크 디코더가 분할 결과를 만듭니다. 영상에서는 이전 상호작용과 예측 마스크의 메모리를 이후 프레임에 사용합니다.

**SAM 3D Objects.** 목표 마스크와 이미지가 형상·외관 재구성의 조건으로 들어갑니다. 가려진 표면은 모델이 학습한 사전 정보로 예측합니다.

## 실전 워크플로

영상의 초반 프레임에서 물체에 표시하고 SAM 2로 마스크를 전파합니다. 가림 경계에서 추적이 벗어나면 수정합니다. 선명한 프레임과 마스크를 SAM 3D Objects에 넣은 뒤 보이지 않던 방향에서 결과를 확인합니다.

## 검증할 항목

재구성 전에 마스크 품질을 측정합니다. 형상 스케일과 방향, 후속 작업 적합성을 확인합니다. 치수와 충돌 정확도가 중요한 경우 실측 형상을 사용합니다. SAM 2와 SAM 3D Objects의 별도 이용 조건을 확인합니다.

## 공개 범위와 라이선스

SAM 2 코드와 모델 조건은 각각 확인하세요. SAM 3D Objects 코드와 체크포인트는 SAM License가 적용되며 의존성 조건도 확인해야 합니다.

## 공식 자료

- [공식 기술 자료](https://github.com/facebookresearch/sam2)
- [SAM 3D Objects 아키텍처와 데모](https://github.com/facebookresearch/sam-3d-objects)
