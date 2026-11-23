# 영상으로 보고 따라 하는 피지컬 AI 실습

[RTX 5090 한 장으로 RGB 도로 복원하기](../docs/ko/labs/rgb-reality-view.md) · [데이터·차량 모델 출처와 사용 조건](rgb-reality-view/SOURCES.md)


[English](README.md) · [한국어 영상 갤러리](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/showcase/)

관심 있는 영상에서 시작하세요. 실습마다 구현 방법과 실행 명령, 소스 코드, 촬영 당시 테스트 결과를 함께 볼 수 있습니다.

| 관심 분야 | 먼저 해 볼 실습 | 확인할 내용 |
| --- | --- | --- |
| 로봇 학습·제어 | [GR00T 집기](../docs/ko/labs/gr00t-placement.md), [cuRobo 장애물 회피](../docs/ko/labs/robot-motion.md) | 카메라 관측, 행동 묶음, 로봇 경로와 배치 성공 여부. |
| 물리 엔진 | [Newton 천·케이블](../docs/ko/labs/newton-materials.md), [PhysX 접촉 실험](../docs/ko/labs/physics.md) | 점의 좌표, 물체의 변형, 미끄러진 거리와 튀어 오른 높이. |
| 3D 세계·월드 모델 | [3DGS 광장](../docs/ko/labs/spatial-reconstruction.md), [Infinigen 집](../docs/ko/labs/scene-generation.md), [도구 비교](../docs/ko/spatial-worlds.md) | 복원한 공간을 탐색하고 생성한 메시를 살펴본 뒤 Cosmos 영상 출력과 비교합니다. |
| 자율주행 | [CARLA 운전자 카메라](../docs/ko/labs/carla-ego.md), [Alpamayo](../docs/ko/labs/world-driving.md), [AlpaSim](../docs/ko/workflows/alpasim-closed-loop.md) | 네 도로 환경과 차량 경로, 학습 모델 추론과 정책 평가를 구분해 봅니다. |

[실습 CLI로 실행하고 검증하기](cli/README.ko.md). 실제 시뮬레이터와 모델을 실행하며 명령어·로그·결과 파일 해시를 남깁니다. 플랫폼마다 실행 환경은 따로 준비합니다.

[실험 12가지와 현재 결과 살펴보기](EXPERIMENTS.ko.md) · [GPU 한 대에서 네 분야 실행 영상](../site/public/showcase/four-domain-grid.mp4)

FFmpeg와 Pillow가 있으면 GPU 없이도 도구 이름이 표시된 비교 영상을 다시 만들 수 있습니다.

```sh
python3 labs/render_grid.py --output ./runs/four-domain-grid.mp4
```

장면을 만드는 과정부터 배우려면 [CAD 작업대 → Isaac Sim → Replicator](../docs/ko/labs/workbench-capstone.md)에서 설치와 캡처, GPU 없는 결과 검사까지 따라 할 수 있습니다.

```sh
git clone https://github.com/james-joobs/awesome-nvidia-physical-ai.git
cd awesome-nvidia-physical-ai
```

| 실습 | 사용한 도구 | 먼저 해볼 것 |
| --- | --- | --- |
| [로봇 동작](../docs/ko/labs/robot-motion.md) | cuRobo, AutoData, MimicGen, Isaac Lab, Newton, GR00T | Franka 팔의 두 경로를 재생해 비교합니다. |
| [물리 비교](../docs/ko/labs/physics.md) | Isaac Sim, PhysX, OpenUSD, SimReady, Newton | 충돌체가 어긋난 씬을 열고 Play를 누릅니다. |
| [Newton 천·케이블](../docs/ko/labs/newton-materials.md) | Newton, Warp, OpenUSD, Isaac Sim | 천과 케이블을 계산하고 검토용 장면을 GUI에서 엽니다. |
| [월드·주행 모델](../docs/ko/labs/world-driving.md) | Cosmos3-Edge, Alpamayo2-Edge, Isaac Sim | 영상을 생성하고 자체 카메라 입력에서 예측한 차량 자세 64개를 검사합니다. |
| [CAD에서 센서 데이터까지](../docs/ko/labs/scene-to-data.md) | CadQuery, OpenUSD, Isaac Sim, PhysX, Replicator | 동봉된 카메라 데이터로 큐브의 이동량을 계산합니다. |
| [책상 주변 실험](../docs/ko/labs/everyday-robots.md) | Isaac Sim, PhysX, OpenUSD, OpenCV | 알람, 서랍, 책상 정리, 카트 중 하나를 재생합니다. |
| [GR00T 집기·놓기](../docs/ko/labs/gr00t-placement.md) | GR00T N1.6-DROID, Isaac Lab-Arena, Isaac Sim | 테스트 기록에서 들기와 놓기 성공 시점을 확인합니다. |
| [Replicator 출력](../docs/ko/labs/replicator-outputs.md) | Isaac Sim, Replicator, OpenUSD | 같은 프레임의 RGB·깊이·분할 데이터 12세트를 생성합니다. |
| [Microduck 보행](../docs/ko/labs/microduck.md) | Isaac Lab, Newton, RSL-RL | 보행 정책을 학습하고 체크포인트를 재생합니다. |
| [Warp 입자](../docs/ko/labs/warp-particles.md) | NVIDIA Warp, CUDA, OpenGL | 입자 충돌을 계산하고 결과를 확인합니다. |

이 레포의 최상위 폴더에서 `python3 labs/verify.py`를 실행하면 NVIDIA GPU 없이도 동봉된 결과와 코드 연결을 검사할 수 있습니다. 시뮬레이션을 새로 실행하는 데 필요한 환경은 각 가이드에 적었습니다.

## 도로의 새 시점과 주행 예측 경로

직접 만든 도로를 촬영해 NuRec으로 새 시점을 렌더링하고 Harmonizer 적용 전후를 비교합니다. 원본 여섯 카메라의 영상은 Alpamayo 2 Edge에 따로 넣습니다. 영문·한국어 20초 영상, 정답·복원·보정 이미지와 CPU 검사를 제공합니다.

[한국어 실습](../docs/ko/labs/reality-view.md) · [English lab](../docs/en/labs/reality-view.md) · [코드와 실행 결과](reality-view/)
