# 비정상적으로 매우 쉽게 Isaac Sim 써보기

[English](../../en/workflows/isaac-sim-first-cube.md) · **한국어** · [Isaac Sim 가이드](../isaac-sim.md)

같은 큐브를 두 번 떨어뜨리면서 **무엇이 물체를 움직이게 하고, 무엇이 바닥에 닿게 하는지** 확인합니다. 처음에는 예제 장면을 그대로 열고, 두 번째에는 같은 조건을 직접 만듭니다.

## 같은 큐브가 왜 한 번은 바닥을 통과할까요?

### USD는 시작 상태를 담고, PhysX는 다음 상태를 계산합니다

`cube-drop.usda`의 부모 프림 `/World/DropBody`는 물리 속성을 가진 강체입니다. `xformOp:translate = (0, 0, 3.5)`는 시작할 때의 큐브 중심을, `metersPerUnit = 1`은 좌표 한 단위가 1m임을 뜻합니다. `upAxis = "Z"`이므로 높이는 세 번째 값으로 읽습니다. [실습의 USD 파일](../../../assets/lessons/isaac-sim-first-cube/cube-drop.usda)

| 역할 | 어디에 설정하나요? |
| --- | --- |
| 화면에 보이는 큐브 | 자식 프림 `/World/DropBody/Cube`의 크기 `1` |
| 큐브를 움직이는 상태 | 부모의 `PhysicsRigidBodyAPI`와 질량·초기 위치 |
| 바닥과 접촉하는 형상 | 바닥의 충돌체와, `WithCollider`에서 자식에 붙는 `PhysicsCollisionAPI` |

### 멈출 높이를 먼저 예측해 보세요

바닥 윗면은 Z=0이고 한 변이 1m인 큐브의 중심은 아랫면보다 0.5m 위에 있습니다. 충돌체를 켜면 큐브 중심은 **약 0.5m**에 머물 것으로 예상할 수 있습니다. 충돌체를 꺼도 강체에는 중력이 작용하지만 큐브와 바닥 사이의 접촉은 계산할 수 없습니다. 두 변형을 재생해 예측을 확인합니다. [공식 물리 구성 요소](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

## 실행 환경 고르기

Isaac Sim을 아직 열어 본 적이 없다면 [GUI·CLI 시작하기](../onboarding/isaac-sim-tools.md)에서 설치와 첫 실행을 먼저 합니다. RTX 워크스테이션은 [시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html)을, Mac에서 원격 RTX를 쓸 때는 [WebRTC 접속 방법](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html)을 확인하세요. 브라우저로 원격 GPU를 쓰려면 [Isaac Launchable](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_advanced_cloud_setup_launchable.html)도 있으며 [GPU 사용료](https://docs.nvidia.com/brev/concepts/gpu-instances)와 제공 버전을 확인해야 합니다.

## 예제 장면 열기

1. [`cube-drop.usda` 받기](../../../assets/lessons/isaac-sim-first-cube/cube-drop.usda)를 누릅니다. 장면에 필요한 도형이 이 파일에 들어 있습니다.
2. Isaac Sim에서 **File → Open**으로 파일을 선택합니다. 뷰포트의 카메라 메뉴에서 **LessonCamera**를 고르면 두 실행을 같은 각도로 볼 수 있습니다.
3. **Stage → World**를 선택하고 **Property**에서 `collider` 변형 세트를 찾습니다. 정지 상태에서 **WithoutCollider → Play** 순으로 고릅니다. 큐브가 바닥 높이를 지나가는지 살펴보세요.
4. **Stop**을 누른 뒤 **WithCollider → Play**로 반복합니다. 두 번째 큐브가 어디에 멈추는지 비교합니다. 이전 위치가 남아 있다면 파일을 다시 열고 재생 전에 변형을 선택합니다.

두 변형의 시작 높이, 바닥, 카메라, 중력은 같습니다. 큐브의 충돌체만 바뀝니다.

## 빈 화면에서 직접 만들기

1. 새 장면에 바닥면을 추가합니다. 바닥보다 높은 곳에 Xform을 만들고 그 안에 Cube를 넣습니다.
2. 부모 Xform에 **Rigid Body**를 적용합니다. 한 번 재생한 뒤 정지합니다.
3. 자식 Cube에 **Collider**를 적용하고 다시 재생합니다. 기본 바닥면에는 충돌체가 적용돼 있습니다.
4. 재생을 정지하고 장면을 `.usda`로 저장합니다. 다시 열면 같은 시작 위치에서 비교할 수 있습니다.

[Isaac Sim 6.2 공식 물리 실습](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

## 두 실행 비교하기

**WithoutCollider**에서는 큐브가 바닥을 지나가고, **WithCollider**에서는 바닥에 멈추면 됩니다. RTX 5090과 Isaac Sim 6.2.0에서 PhysX를 2.5초 실행했을 때, 충돌체를 켠 큐브의 중심이 바닥 위 0.50m에 멈췄습니다.

다음 실습에서는 바닥을 치수를 아는 작업대 자산으로 바꿔 봅니다. [작업대 CAD를 Isaac Sim 장면으로 만들기](workbench-cad-to-isaac-sim.md)
