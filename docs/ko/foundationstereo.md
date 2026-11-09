# FoundationStereo

[← 전체 목록](../../README.ko.md) · [English](../en/foundationstereo.md)

FoundationStereo는 정류한 스테레오 영상의 밀집 시차를 예측합니다. 보정 파라미터로 시차를 미터 단위 깊이로 바꿉니다.

![FoundationStereo 네트워크 개요](https://nvlabs.github.io/FoundationStereo/static/images/overview.jpg)

*특징 추출부터 비용 필터링과 반복 시차 보정까지 따라가 보세요.* [공식 그림 출처](https://nvlabs.github.io/FoundationStereo/)

![FoundationStereo 깊이 예시](https://nvlabs.github.io/FoundationStereo/static/images/intro.jpg)

*입력 영상과 복원 깊이를 대조하고 깊이가 급변하는 경계의 세부 형상을 확인해 보세요.* [공식 그림 출처](https://nvlabs.github.io/FoundationStereo/)

## 어떻게 동작하나

논문의 네트워크는 CNN의 세밀한 국소 특징과 DepthAnythingV2의 단안 단서를 결합합니다. 혼합 비용 볼륨은 좌우 영상에서 가능한 대응을 표현합니다. 어텐션 기반 필터링이 영상 위치와 시차 방향의 문맥을 모으고, 반복 갱신 단계가 비용 및 상관 특징으로 시차 추정을 개선합니다.

### 구성 요소별 입출력

| 구성 요소 | 입력 | 출력 |
|---|---|---|
| 특징 추출 | 정류 좌우 RGB 영상 | CNN과 단안 사전 정보 특징 |
| 대응 및 보정 | 좌우 특징 | 영상 좌표의 밀집 시차 |
| 투영 | 시차와 스테레오 보정값 | 미터 단위 깊이 또는 점군 |

## 실전 워크플로

무광·유광·투명 물체가 있는 상자를 보정된 카메라로 촬영합니다. 시차를 깊이로 바꿔 3D 점으로 투영하고 알려진 물체 거리와 비교합니다. 물체 경계와 배경의 오차를 나눠 살펴봅니다.

## 검증할 항목

모델을 비교할 때 카메라 보정과 간격을 고정합니다. 유효 깊이 비율, 거리별 오차와 배포 해상도에서의 지연을 측정합니다. 벤치마크 결과는 데이터셋과 장비에 따라 달라집니다.

## 공개 범위와 라이선스

연구 코드 비상업적 제한; 별도 상업용 모델 제공 여부와 조건은 해당 배포물 확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [연구 아키텍처와 벤치마크 예제](https://nvlabs.github.io/FoundationStereo/)
- [관련 공식 자료 · github.com](https://github.com/NVlabs/FoundationStereo)
