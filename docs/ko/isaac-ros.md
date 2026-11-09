# Isaac ROS

[← 전체 목록](../../README.ko.md) · [English](../en/isaac-ros.md)

Isaac ROS는 가속 인식·위치 추정·조작 기능을 ROS 2에 연결하는 패키지 모음입니다. Perceptor 참조 워크플로에서는 개별 노드를 조합해 로봇 인식 시스템을 구성합니다.

![Isaac Perceptor 데이터 흐름](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-3.1/resources/isaac_ros_docs/repositories_and_packages/isaac_perceptor/perceptor_diagram.png)

*스테레오 입력이 깊이와 오도메트리로 갈라진 뒤 Nvblox에서 합쳐지는 부분을 보세요. Perceptor 3.1 문서의 그림입니다.* [공식 그림 출처](https://nvidia-isaac-ros.github.io/v/release-3.1/reference_workflows/isaac_perceptor/technical_details.html)

## 어떻게 동작하나

1. **센서 계층.** Nova 카메라, 기록 파일, Isaac Sim에서 동기화된 스테레오 프레임을 받아 영상 노드에서 정류합니다.
2. **병렬 기하 처리.** 스테레오 깊이는 카메라 광선 방향의 거리를 구합니다. Visual SLAM은 연속 영상으로 로봇의 움직임과 자세를 추정합니다.
3. **지도와 경로 계획.** Nvblox는 추정 자세를 이용해 깊이를 로컬 복셀 지도에 통합합니다. 2D 비용 지도 플러그인이 장애물을 Nav2에 전달합니다. 가속 메시지 형식에 합의한 노드 사이에서는 NITROS로 데이터 이동을 효율화할 수 있습니다.

### 구성 요소별 입출력

| 구성 요소 | 입력 | 출력 |
|---|---|---|
| 스테레오 수집 | 동기화 좌우 영상과 카메라 정보 | 깊이·SLAM에 정류 영상 토픽 전달 |
| 기하 처리 | 스테레오 시차와 추적한 카메라 자세 | 깊이 영상과 월드·카메라 좌표 관계를 지도에 전달 |
| 로컬 계획 | 복셀 재구성과 단면 높이 설정 | Nav2가 조회하는 비용 지도 계층 |

## 실전 워크플로

창고 rosbag을 먼저 재생합니다. 정류 영상, 오도메트리, 깊이 영상을 각각 확인한 뒤 Nvblox를 연결합니다. 로봇이 움직여도 정지한 팔레트가 지도에서 같은 위치에 나타나는지 확인하고 Nav2를 연결합니다.

## 검증할 항목

토픽 리매핑, 타임스탬프 동기화, 카메라 보정, TF 연결을 확인합니다. 센서부터 비용 지도까지의 지연과 CPU·GPU 경계에서의 데이터 변환을 측정합니다. 사용 릴리스의 참조 실행 구성과 호환 드라이버로 시작합니다.

## 공개 범위와 라이선스

패키지별 조건 상이; 공통 저장소와 배포물의 개별 라이선스 확인.

## 공식 자료

- [Isaac Perceptor 데이터 흐름](https://nvidia-isaac-ros.github.io/v/release-3.1/reference_workflows/isaac_perceptor/technical_details.html)
- [Isaac for Manipulation 참조 아키텍처](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)
- [관련 공식 자료 · nvidia-isaac-ros.github.io](https://nvidia-isaac-ros.github.io/)
- [관련 공식 자료 · github.com](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common)
