# 작업대 CAD를 Isaac Sim 장면으로 만들기

[English](../../en/workflows/workbench-cad-to-isaac-sim.md) · **한국어** · [목표별 카탈로그](../../../README.ko.md#만들고-싶은-것부터-시작하세요)

작업대 모델 하나를 두 가지 작업에 사용합니다. STEP 파일을 OpenUSD로 변환하고 치수와 충돌체를 확인한 다음, 라벨이 붙은 카메라 데이터를 만들거나 로봇팔 집기를 실행합니다. 변환과 두 가지 Isaac Sim 기본 예제는 공식 문서에 있으며, 아래 가이드는 이를 한 작업대 장면에 적용합니다.

## 준비물

| 항목 | 시작 기준 |
| --- | --- |
| CAD 입력 | 치수를 아는 STEP 파일 하나. 직접 만든다면 CAD 편집기에서 1,200 × 600 × 40 mm 직육면체를 만든 뒤 `workbench.step`으로 내보냅니다. 상판만으로도 실습할 수 있습니다. |
| 변환 도구 | AIF Pipeline Samples 리비전 `4103896`과 HOOPS 변환기를 포함한 Kit/USD Composer. 공식 설치 문서를 따라 설정하고 Kit 빌드를 기록합니다. |
| 시뮬레이터 | 이 가이드는 Isaac Sim 6.1 문서를 기준으로 합니다. 설치한 빌드에 맞는 요구사항과 예제를 사용합니다. NVIDIA RTX가 있는 지원 Linux 또는 Windows 워크스테이션에서 시작합니다. |
| 로봇팔 집기용 추가 입력 | 공식 매니퓰레이터 예제의 URDF, 그리퍼, 제어기. 작업대 상판은 로봇 모델과 별개로 준비합니다. |

[AIF 설치](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/docs/get-started/setup.md) · [Isaac Sim 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html) · [워크스테이션 설치](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_workstation.html)

## 1. USD로 변환하고 검증하기

아래 샘플 리비전을 받은 뒤 환경에 맞게 [설치와 Kit 경로 설정](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/docs/get-started/quickstart.md)을 마칩니다.

```bash
git clone https://github.com/NVIDIA-Omniverse/aif-pipeline-samples.git
cd aif-pipeline-samples
git checkout 41038967ef0a2459b128a225161f8d59beb3b424
```

샘플 저장소에서 입력을 `cad_source/workbench.step`에 두고 변환을 실행합니다. 기본 제공 HOOPS 프리셋은 STEP을 지원합니다.

```bash
mkdir -p usd_converted validation_reports
uv run aif-pipeline config show
uv run aif-pipeline convert ./cad_source/workbench.step ./usd_converted/workbench.usdc \
  --spec scripts/data/creo_spec.json
uv run aif-pipeline validate ./usd_converted/workbench.usdc ./validation_reports/
```

변환한 자산을 열어 CAD 원본과 상판 치수를 비교합니다. 예제의 실제 치수는 USD에 기록된 단위 설정과 관계없이 **1.2 × 0.6 × 0.04 m**여야 합니다. 위쪽 축과 프림 계층을 확인하고, 검증 보고서에서 끊긴 참조가 있는지 봅니다. 형상 정리나 단위·축 정규화가 필요하면 공식 최적화 단계를 적용한 뒤 다시 측정합니다. [공식 CAD → USD 워크플로](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/docs/get-started/cad-to-usd-workflow.md) · [Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/)

## 2. 재사용할 작업대 장면 구성하기

1. Isaac Sim에서 새 장면을 만들고 변환된 자산을 `/World/Workbench` 같은 프림 아래에 참조로 추가합니다. 장면에서 치수와 위쪽 축을 다시 확인합니다. 자산과 장면의 단위 또는 축이 다르면 자산을 먼저 정규화하거나 변환값을 적용합니다. 형상 파일 옆에 `workbench_scene.usd`를 따로 저장해 변환 결과와 시뮬레이션 설정을 분리합니다.
2. 상판에 정적 충돌체를 적용합니다. 평평한 상판이라면 치수에 맞춘 상자형 충돌체로 충분합니다. 그 위에 충돌체가 있는 작은 동적 큐브를 놓고 시뮬레이션을 실행합니다.
3. 큐브가 상판 위에 멈추고 상판은 움직이지 않는지 확인합니다. 매번 같은 위치에서 시작할 수 있도록 초기 상태로 되돌린 뒤 장면을 저장합니다.

작은 장면에 SimReady 원칙을 적용한 예시입니다. 연결할 도구가 특정 SimReady 프로파일을 요구하면 해당 규격을 따로 확인합니다. 디지털 트윈으로 확장할 때는 같은 USD를 더 큰 배치에 참조하고, 실제 치수와 장비 사이 여유 공간을 대조할 수 있습니다. [OpenUSD 길이 단위](https://openusd.org/release/api/group___usd_geom_linear_units__group.html) · [Isaac Sim 물리 기본](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/physics/simulation_fundamentals.html) · [SimReady 요구사항](https://docs.omniverse.nvidia.com/simready/latest/simready-faq.html)

## 3A. 라벨이 붙은 카메라 데이터 만들기

1. 공식 Replicator 예제를 기본 장면으로 한 번 실행합니다. 그다음 장면을 불러오는 부분에서 로컬 작업대 장면을 참조하고 큐브가 보이도록 카메라를 배치합니다. 첫 테스트에서는 카메라 위치를 고정합니다.
2. 기존 라벨을 초기화하는 단계가 있다면 그 뒤에 큐브에 `part` 같은 의미 클래스를 붙입니다. `BasicWriter`에서 `rgb`, `distance_to_image_plane`(깊이), `semantic_segmentation`을 활성화하고 네 프레임을 기록합니다.
3. 같은 프레임의 RGB 이미지, 깊이, 마스크를 함께 엽니다. 마스크가 큐브를 덮고 `part`에 매핑되는지, 깊이값이 카메라 배치와 맞는지 확인합니다. 그 뒤 물체 위치나 조명을 바꿔 봅니다.

**남길 산출물**은 USD 장면, 카메라 위치·방향, 저장 설정, 출력 샘플입니다. [Replicator 장면 기반 공식 예제](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/tutorial_replicator_scene_based_sdg.html)

## 3B. 로봇팔로 물체 집어 옮기기

1. 공식 Isaac Sim 매니퓰레이터 튜토리얼에서 URDF를 가져오고, 예제 로봇과 장면으로 집어 옮기기 동작을 먼저 성공시킵니다.
2. 예제 장면 복사본에 변환한 상판을 참조로 추가합니다. 새 상판의 충돌체를 기존 작업면 높이에 맞추고, 겹치는 기존 받침은 제거하거나 비활성화합니다. 로봇 베이스와 물체를 집고 놓을 자세를 새 작업면과 도달 범위에 맞춥니다.
3. 같은 시작 자세로 초기화해 반복합니다. 그리퍼가 큐브를 들어 올리고 상판에 의도치 않게 접촉하지 않으며 지정 영역 안에 놓는지 확인합니다. 시작 자세와 성공 횟수를 기록합니다.

**남길 산출물**은 작업 장면, 로봇·제어기 설정, 간단한 결과 기록입니다. 카메라 인식이나 ROS 2 모션 플래닝이 필요하면 기본 동작을 확인한 뒤 Isaac ROS 참조 워크플로로 연결합니다. [공식 URDF 집기 튜토리얼](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/robot_setup_tutorials/tutorial_manipulator_workflow.html) · [Isaac for Manipulation 참조 아키텍처](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)

## 관련 도구와 검증 범위

- [OpenUSD](../openusd.md)는 장면 구성에, [OpenUSD Exchange SDK](https://github.com/NVIDIA-Omniverse/usd-exchange)는 USD 교환 파이프라인을 구현하거나 수정할 때 사용합니다. 입력이 작업대 영상이라면 [SimFoundry](https://github.com/NVlabs/SimFoundry)에서 별도로 시작할 수 있습니다.
- AIF 샘플 코드는 MIT입니다. CAD 변환기, Kit/Isaac Sim 배포물, CAD·로봇·자산 파일은 각자의 이용 조건이 적용됩니다. [AIF 라이선스](https://github.com/NVIDIA-Omniverse/aif-pipeline-samples/blob/41038967ef0a2459b128a225161f8d59beb3b424/LICENSE) · [Isaac Sim 라이선스 범위](../isaac-sim.md)
- **검증 상태** · 공식 예제와 명령을 대조했습니다. 작업대 통합 절차의 RTX 워크스테이션 실행 검증은 아직 하지 않았습니다.
