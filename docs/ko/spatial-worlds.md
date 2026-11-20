# 3D 세계 생성·렌더링 도구 고르기

[English](../en/spatial-worlds.md) · [카탈로그](../../CATALOG.ko.md)

## 어떤 ‘세계’가 필요한가요?

**직접 공간 생성하기:** [WorldGen 글·이미지 → 3D 장면](labs/worldgen-scenes.md).

카메라 움직임에 맞춰 생성한 영상과 직접 돌아다닐 수 있는 3D 공간은 출력부터 다릅니다. 새 영상 픽셀이 필요한지, 여러 시점에서 다시 그릴 공간인지, 수정할 수 있는 기하 구조인지, 충돌·물리가 있는 환경인지 먼저 정해 보세요.

| 입력과 방식 | 결과 | 다음 단계에서 할 수 있는 일 |
|---|---|---|
| 글·이미지 → 생성형 3D 모델 | Gaussian 장면, 경우에 따라 메시·충돌체 | 새 시점으로 렌더링하거나 지원되는 도구에 가져오기 |
| 카메라 정보가 있는 사진 → 3DGS 복원 | 중심·크기·회전·불투명도·색 | 촬영한 공간을 주변 시점에서 다시 그리기 |
| 시드·규칙 → 절차적 장면 생성 | 메시·재질·조명·카메라 | 기하 구조 편집, 에셋 내보내기, 물리 속성 추가, 데이터 생성 |
| 상태·제어 명령 → 주행 시뮬레이터 | 다음 상태·센서 화면·이벤트 | 폐루프로 차를 움직이고 운전자 시점 기록하기 |
| 이미지·카메라 동작 → 영상 모델 | 시간순 RGB 이미지 | 생성된 움직임 보기. 재사용할 3D 에셋이 생기는 것은 아님 |

**직접 공간 생성하기:** [WorldGen 글·이미지 → 3D 장면](labs/worldgen-scenes.md). **직접 실행한 경로:** [CARLA 운전자 카메라](labs/carla-ego.md) → [촬영한 시점 → fVDB 3DGS → Spark 브라우저 탐색](labs/spatial-reconstruction.md). 별도의 [Infinigen 집 안 둘러보기](labs/scene-generation.md)는 실제 기하 구조를 생성합니다. [Cosmos 영상 생성](labs/world-driving.md)은 다른 종류의 결과로 계속 볼 수 있습니다.

## 도구별 입출력과 공개 범위

### 생성형 3D 세계

**World Labs Marble**은 글과 시각 입력으로 탐색 가능한 세계를 만듭니다. 공식 문서에는 SPZ·PLY splat과 별도의 메시·충돌체 내보내기가 설명되어 있습니다. 호스팅 서비스이며 로컬 오픈소스 모델은 아닙니다. 무료 생성과 파일 내보내기 권한도 다릅니다. 현재 내보내기는 유료 플랜이 필요합니다. 이번 작업에서는 유료 API를 호출하거나 Marble 세계를 생성하지 않았습니다. 대신 World Labs의 오픈소스 렌더러 **Spark**로 직접 복원한 fVDB 장면을 보여줍니다. [Marble 내보내기](https://docs.worldlabs.ai/marble/export/gaussian-splat/index) · [파일 형식](https://docs.worldlabs.ai/marble/export/specs) · [Spark 소스·MIT](https://github.com/sparkjsdev/spark)

**NVIDIA Lyra 1.0**은 생성한 다중 시점 영상 정보와 Gaussian 디코더를 결합해 3D·4D 장면을 출력합니다. 모델 카드의 가중치 조건은 NVIDIA Open Model License입니다. **Lyra 2.0**은 긴 탐색 경로에서 3D 일관성을 유지하는 세계 생성·복원 계열이며, 가중치 조건이 NVIDIA Internal Scientific Research and Development Model License로 다릅니다. 두 구현 코드는 Apache-2.0으로 공개되어 있습니다. 1.0의 모델 조건을 2.0에 그대로 적용하면 안 됩니다. 2.0 공식 설치 환경은 H100으로 검증되어 있으며, 이번 OMEN 업데이트에서는 두 버전 모두 실행하지 않았습니다. [Lyra 소스](https://github.com/nv-tlabs/lyra) · [1.0 모델 카드](https://huggingface.co/nvidia/Lyra) · [2.0 코드·모델 조건](https://github.com/nv-tlabs/lyra/tree/9fffc9adc37004091ecf26ef03abfb3abdf4d59a/Lyra-2)

**WorldGen**은 글·이미지에서 파노라마를 생성하고 DA-2로 거리를 추정한 뒤 splat·메시로 바꿉니다. FLUX 두 모델의 접근 승인 후 OMEN에서 **텍스트 장면 두 개와 카메라 정보가 있는 이미지 장면 한 개**를 실제 생성했습니다. [실습 가이드](labs/worldgen-scenes.md)에 장면별 20초 자유 시점 영상, 직접 불러보는 3D 미리보기, 코드와 형상 검사 방법을 담았습니다. 코드·LoRA는 Apache-2.0이며 FLUX 가중치의 비상업 모델 조건과 사용자별 접근 승인은 별도입니다. 이미지 경로에는 카메라 내부 파라미터를 이용한 투영 보정을 적용했고 내용을 공개했습니다. [WorldGen](https://github.com/ZiYang-xie/WorldGen) · [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) · [FLUX.1-Fill-dev](https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev)

### 촬영한 공간의 복원과 편집 가능한 기하 구조

**fVDB Reality Capture**는 카메라 자세가 있는 사진으로 radiance field를 학습합니다. 이번에는 CARLA의 정확한 카메라와 학습용 깊이로 초기 점군을 만들었습니다. 프롬프트로 새 공간을 만든 결과는 아닙니다. **SHARP**는 사진 한 장으로 주변 시점의 Gaussian을 추정하므로 가려진 영역의 불확실성이 더 큽니다. 코드는 Apple의 별도 소프트웨어 라이선스이고 가중치는 비상업적 연구용입니다. **Infinigen**은 절차적 규칙으로 메시·재질·방 배치를 만듭니다. 신경망 파운데이션 모델은 아닙니다. BSD-3-Clause 코드와 Blender·에셋 의존성의 조건은 각각 확인해야 합니다. [fVDB](https://github.com/openvdb/fvdb-reality-capture) · [SHARP 라이선스](https://github.com/apple-aiml-research/ml-sharp) · [Infinigen](https://github.com/princeton-vl/infinigen)

## 실행 결과와 선택 조건

**2026-11-20** 확인 기준입니다. ‘실행’은 제작자의 홍보 영상을 가져온 것이 아니라 직접 돌려 결과를 저장했다는 뜻입니다.

| 도구 | OMEN에서 확인한 상태 | 볼 수 있는 결과 |
|---|---|---|
| CARLA 0.9.16 / UE4.26 | RTX 5090 실행 | 운전자 시점 네 환경, 원본 추적 카메라·차량 경로 |
| fVDB Reality Capture 0.6.0 | RTX 5090 실행 | 72시점 촬영, 전체 PLY, 3DGS 영상, 6.15MB 브라우저 모델 |
| Apple SHARP | RTX 5090 실행 | 사진 한 장씩 복원한 두 장면의 주변 시점 영상 |
| Infinigen / Blender | 장면 생성·CPU Cycles 렌더링 | 가구가 있는 집, `.blend`, 카메라 경로와 이동 영상 |
| Spark 2.4.0 | 사이트에 연결 | 클릭할 때 불러오는 WebGL2 뷰어. 방문자 기기에서 렌더링 |
| WorldGen / DA-2 | RTX 5090에서 FLUX FP4·offload로 실행 | 생성 공간 3개, Gaussian PLY·메시, 카메라 이동 영상과 웹 미리보기 3개 |
| NVIDIA Lyra 1·2 | 공식 자료·라이선스 검토 | 참고 경로. 이번에는 실행하지 않음 |
| World Labs Marble | 호스팅 서비스 참고 | 계정 생성·결제·API 작업 없음 |

WonderWorld 공식 설치는 GPU 메모리 48GB를 요구해 OMEN의 단일 32GB GPU 조건을 넘습니다. HunyuanWorld 1.0은 커뮤니티 라이선스에서 한국을 제외하므로 이번 실행 후보에서 뺐습니다. 이는 실행 대상을 고른 조건이며 시각적 품질의 우열은 아닙니다. [WonderWorld](https://github.com/KovenYu/WonderWorld) · [HunyuanWorld 1.0 라이선스](https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0/blob/main/LICENSE)

## 어떤 순서로 실습하면 좋을까요?

1. [CARLA로 주행하기](labs/carla-ego.md): 프레임, 동기 스텝, 운전자 카메라 위치를 익힙니다.
2. [광장 복원하기](labs/spatial-reconstruction.md): 카메라 파라미터·좌표 변환·Gaussian과 학습에서 남긴 시점의 검사를 살펴봅니다.
3. [집 생성하기](labs/scene-generation.md): 실제 메시·재질과 공간 안을 지나는 카메라 경로를 확인합니다.
4. [주행 모델의 예측 경로](labs/world-driving.md)를 읽은 뒤 [AlpaSim 정책 평가](workflows/alpasim-closed-loop.md)로 이어 갑니다.

그럴듯한 렌더링만으로 충돌체나 물리적 타당성이 생기지는 않습니다. 도구를 연결할 때 크기·좌표계·이용 조건을 장면과 함께 넘겨 주세요. [fVDB 입출력 설명](fvdb-reality-capture.md) · [미디어 출처](../../site/public/showcase/SPATIAL-CREDITS.md).
