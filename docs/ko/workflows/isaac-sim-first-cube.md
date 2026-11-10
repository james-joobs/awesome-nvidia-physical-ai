# 비정상적으로 매우 쉽게 Isaac Sim 써보기

[English](../../en/workflows/isaac-sim-first-cube.md) · **한국어** · [Isaac Sim 가이드](../isaac-sim.md)

같은 큐브를 두 번 떨어뜨립니다. 강체를 적용하면 중력에 따라 떨어지고, 충돌체를 추가하면 바닥과 접촉해 멈춥니다. 기본 도형과 PhysX로 실습합니다.

## 예제 장면 열기

1. [`cube-drop.usda`](../../../assets/lessons/isaac-sim-first-cube/cube-drop.usda)를 GitHub의 **Raw** 또는 다운로드 버튼으로 받습니다. 외부 자산 없이 이 파일 하나로 열 수 있습니다.
2. Isaac Sim에서 파일을 엽니다. 같은 각도에서 비교하려면 뷰포트의 카메라 메뉴에서 **LessonCamera**를 선택합니다.
3. Stage 패널에서 **World**를 선택하고 속성 패널에서 `collider` 변형 세트를 찾습니다. 정지 상태에서 **WithoutCollider**를 선택하고 **Play**를 누릅니다. 초록색 큐브가 회색 바닥을 통과합니다.
4. 정지하고 **WithCollider**로 바꾼 뒤 다시 **Play**를 누릅니다. 이번에는 큐브가 바닥 위에 멈춥니다. 이전 위치가 남아 있다면 파일을 다시 열고 재생 전에 변형을 선택합니다.

두 변형의 시작 높이, 바닥, 카메라, 중력은 같습니다. 큐브의 충돌체만 바뀝니다.

**RTX 5090과 Isaac Sim 6.2.0에서 검증했습니다.** 화면 없이 PhysX 시뮬레이션을 2.5초 실행했을 때 충돌체가 없는 큐브는 바닥을 통과했습니다. 충돌체를 켜면 큐브의 중심이 바닥에서 0.50m 높이에 멈췄습니다.

## 빈 화면에서 직접 만들기

1. 새 장면에 바닥면을 추가합니다. 바닥보다 높은 곳에 Xform을 만들고 그 안에 Cube를 넣습니다.
2. 부모 Xform에 **Rigid Body**를 적용합니다. 한 번 재생한 뒤 정지합니다.
3. 자식 Cube에 **Collider**를 적용하고 다시 재생합니다. 기본 바닥면에는 충돌체가 적용돼 있습니다.
4. 재생을 정지하고 장면을 `.usda`로 저장합니다. 다시 열면 같은 시작 위치에서 비교할 수 있습니다.

[Isaac Sim 6.2 공식 물리 실습](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

## 실행 환경 고르기

- **RTX 워크스테이션** · 지원되는 Windows 또는 Linux에서 Isaac Sim을 실행합니다. [시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html)
- **맥과 원격 RTX 서버** · 서버에서 Isaac Sim을 실행하고 맥용 WebRTC 클라이언트나 비공개로 구성한 브라우저 뷰어로 접속합니다. [원격 화면 접속](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html)
- **로컬 GPU가 없는 경우** · NVIDIA Brev의 Isaac Launchable을 브라우저에서 이용할 수 있습니다. GPU 사용료가 있으며 제공되는 Isaac Sim 버전이 이 가이드와 다를 수 있습니다. [Isaac Launchable](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_advanced_cloud_setup_launchable.html) · [Brev 인스턴스 비용](https://docs.nvidia.com/brev/concepts/gpu-instances)

다음 실습에서는 바닥을 치수를 아는 작업대 자산으로 바꿔 봅니다. [작업대 CAD를 Isaac Sim 장면으로 만들기](workbench-cad-to-isaac-sim.md)
