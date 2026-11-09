# nvblox

[← 전체 목록](../../README.ko.md) · [English](../en/nvblox.md)

Nvblox는 GPU 매핑 라이브러리입니다. 핵심 C++ 라이브러리는 형상과 자세를 처리하며 Isaac ROS 패키지가 토픽, TF, 내비게이션 연동을 추가합니다.

![Nvblox 매핑 구성도](https://media.githubusercontent.com/media/nvidia-isaac/nvblox/public/docs/images/system_diagram.png)

*입력과 내부 표현이 경로 계획용 출력과 어떻게 연결되는지 보여줍니다.* [공식 그림 출처](https://github.com/nvidia-isaac/nvblox/tree/public)

![Nvblox 거리장 예시](https://media.githubusercontent.com/media/nvidia-isaac/nvblox/public/docs/images/esdf_example.gif)

*거리장은 계획기가 조회할 수 있는 형상까지의 거리를 시각화합니다.* [공식 그림 출처](https://github.com/nvidia-isaac/nvblox/tree/public)

## 어떻게 동작하나

보정 깊이와 카메라→지도 변환으로 측정값을 희소 복셀 블록에 넣습니다. TSDF는 표면 근처에서 관측을 융합합니다. 메시는 시각화에, ESDF는 경로 계획에서 표면까지의 거리를 확인하는 데 사용합니다. 계층 해상도와 통합 설정이 지도 세부 표현과 갱신 비용을 결정합니다.

## 실전 워크플로

깊이 프레임과 알려진 자세를 넣어 작업대나 통로를 재구성합니다. 메시 치수를 실측과 대조합니다. 충돌 계획기에 주기 전에 거리장 단면을 확인합니다. Nav2에 붙일 때는 [Isaac ROS Nvblox](isaac-ros-nvblox.md)를 사용합니다.

## 검증할 항목

첫 프레임에서 깊이 스케일과 자세 방향을 확인합니다. 이동 중 오래된 복셀, 드리프트, 지도 경계와 GPU 메모리를 관찰합니다. 메시의 시각 품질과 거리값 정확도를 따로 확인합니다.

## 공개 범위와 라이선스

코드 공개; 저장소의 혼합 라이선스 범위 미확인. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [Nvblox 라이브러리와 계층 예제](https://github.com/nvidia-isaac/nvblox/tree/public)
- [관련 공식 자료 · github.com](https://github.com/nvidia-isaac/nvblox)
