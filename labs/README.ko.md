# 영상으로 보고 따라 하는 피지컬 AI 실습

[English](README.md) · [한국어 영상 갤러리](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/showcase/)

관심 있는 영상에서 시작하세요. 실습마다 구현 방법과 실행 명령, 소스 코드, 촬영 당시 테스트 결과를 함께 볼 수 있습니다.

**처음부터 끝까지 한 번에 실습하기.** [CAD 작업대 → Isaac Sim → Replicator](../docs/ko/labs/workbench-capstone.md)에서 설치와 캡처부터 GPU 없는 결과 검사까지 따라 할 수 있습니다.

```sh
git clone https://github.com/james-joobs/awesome-nvidia-physical-ai.git
cd awesome-nvidia-physical-ai
```

| 실습 | 사용한 도구 | 먼저 해볼 것 |
| --- | --- | --- |
| [로봇 동작](../docs/ko/labs/robot-motion.md) | cuRobo, AutoData, MimicGen, Isaac Lab, Newton, GR00T | Franka 팔의 두 경로를 재생해 비교합니다. |
| [물리 비교](../docs/ko/labs/physics.md) | Isaac Sim, PhysX, OpenUSD, SimReady, Newton | 충돌체가 어긋난 씬을 열고 Play를 누릅니다. |
| [CAD에서 센서 데이터까지](../docs/ko/labs/scene-to-data.md) | CadQuery, OpenUSD, Isaac Sim, PhysX, Replicator | 동봉된 카메라 데이터로 큐브의 이동량을 계산합니다. |
| [책상 주변 실험](../docs/ko/labs/everyday-robots.md) | Isaac Sim, PhysX, OpenUSD, OpenCV | 알람, 서랍, 책상 정리, 카트 중 하나를 재생합니다. |
| [GR00T 집기·놓기](../docs/ko/labs/gr00t-placement.md) | GR00T N1.6-DROID, Isaac Lab-Arena, Isaac Sim | 테스트 기록에서 들기와 놓기 성공 시점을 확인합니다. |
| [Replicator 출력](../docs/ko/labs/replicator-outputs.md) | Isaac Sim, Replicator, OpenUSD | 같은 프레임의 RGB·깊이·분할 데이터 12세트를 생성합니다. |
| [Microduck 보행](../docs/ko/labs/microduck.md) | Isaac Lab, Newton, RSL-RL | 보행 정책을 학습하고 체크포인트를 재생합니다. |
| [Warp 입자](../docs/ko/labs/warp-particles.md) | NVIDIA Warp, CUDA, OpenGL | 입자 충돌을 계산하고 결과를 확인합니다. |

이 레포의 최상위 폴더에서 `python3 labs/verify.py`를 실행하면 NVIDIA GPU 없이도 동봉된 결과와 코드 연결을 검사할 수 있습니다. 시뮬레이션을 새로 실행하는 데 필요한 환경은 각 가이드에 적었습니다.
