# 자율주행·영상·월드 모델 데이터

[전체 목록](../../README.ko.md) · [English](../en/datasets-driving-world-model.md)

실제 주행 센서 기록, 재구성 장면, 합성 물리 상호작용, 영상 추론 벤치마크가 섞여 있다. 데이터 종류에 따라 유효한 입력과 평가 방법을 구분한다.

## 작업 기준으로 선택하기

| 필요한 작업 | 대표 자료 | 먼저 확인할 것 |
|---|---|---|
| 실측 센서 데이터 처리 | [PhysicalAI-Autonomous-Vehicles](#physicalai-autonomous-vehicles), [NCore](#physicalai-autonomous-vehicles-ncore) | 센서 종류, 클립 ID, 타임스탬프, 보정 및 접근 |
| 재구성 장면 렌더링 | [AV NuRec](#physicalai-autonomous-vehicles-nurec) | 장면 형식, 렌더러 호환성, 기준 카메라 자세 |
| 시각 이해 평가 | [VANTAGE-Bench](#physicalai-vantage-bench) | 과제 폴더, 제출 형식, 과제별 지표 |
| 1인칭 동작과 언어 탐색 | [Human-1M](#physicalai-human-1m-100k) | 카메라 유무, 시간, 추적 신뢰도, T1과 T2 라벨 |

![VANTAGE-Bench의 공식 작업 분류](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench/resolve/main/assets/vantage_bench_tasks.png)

공식 그림은 의미, 시간, 공간, 시공간 과제를 나눈다. 카드에는 시간 위치 추정의 구간 mIoU, 영상 질의응답의 정확도처럼 과제별 지표가 지정돼 있다. 공식 평가에 필요한 정답 주석은 서버에서 관리한다. [공식 VANTAGE 카드와 제출 정보](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench#evaluation)

## 활용 예시 — 재생과 생성의 출처 보존

원본 ID를 확인한 주행 클립 하나에서 시작한다. 재생할 때는 시간과 카메라 외부 파라미터를 확인하고, 새 시점을 요청하기 전에 원래 자세에서 먼저 렌더링한다. 영상을 변형할 때는 원본 ID, 생성 조건, 모델 버전과 시드를 기록한다. 파생 영상은 원본과 같은 분할에 둔다. 영상 이해 성능은 생성 라벨에 의존하기보다 별도 규약이 있는 벤치마크로 평가한다. [공식 NuRec 장면 가이드](https://docs.nvidia.com/nurec/nurec/model.html) · [NuRec](nurec.md) · [Human-1M Explorer](human-1m-explorer.md)

## 데이터셋 상세

<a id="physicalai-autonomous-vehicles"></a>
### PhysicalAI-Autonomous-Vehicles

실제 자율주행 다중 센서 데이터.

**라이선스·접근:** 별도 약관 확인; 로그인·접근 동의 필요.  
**공식 데이터셋 카드:** [PhysicalAI-Autonomous-Vehicles](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)

<a id="physicalai-autonomous-vehicles-nurec"></a>
### PhysicalAI-Autonomous-Vehicles-NuRec

NuRec으로 재구성한 주행 장면.

**라이선스·접근:** 별도 약관 확인; 로그인·접근 동의 필요.  
**공식 데이터셋 카드:** [PhysicalAI-Autonomous-Vehicles-NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec)

<a id="nurec-av-object-benchmark"></a>
### NuRec-AV-Object-Benchmark

자율주행 물체 중심 3D 재구성 벤치마크.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [NuRec-AV-Object-Benchmark](https://huggingface.co/datasets/nvidia/NuRec-AV-Object-Benchmark)

<a id="physicalai-autonomous-vehicles-ncore"></a>
### PhysicalAI-Autonomous-Vehicles-NCore

NCore 기반 자율주행 센서 데이터.

**라이선스·접근:** 별도 약관 확인; 로그인·접근 동의 필요.  
**공식 데이터셋 카드:** [PhysicalAI-Autonomous-Vehicles-NCore](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NCore)

<a id="physicalai-autonomous-vehicles-foundation4d"></a>
### PhysicalAI-Autonomous-Vehicles-Foundation4D

4D 재구성을 위한 자율주행 데이터.

**라이선스·접근:** 별도 약관 확인; 로그인·접근 동의 필요.  
**공식 데이터셋 카드:** [PhysicalAI-Autonomous-Vehicles-Foundation4D](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-Foundation4D)

<a id="physicalai-autonomous-vehicle-cosmos-drive-dreams"></a>
### PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams

Cosmos 기반 합성 주행 데이터.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams)

![PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams official example](https://cdn-uploads.huggingface.co/production/uploads/658529d61c461dfe88afe8e8/ACduHba6o1VY4ApXpglAo.png)

이미지 출처: [PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams)

<a id="physicalai-autonomous-vehicle-cosmos-synthetic"></a>
### PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic

합성 주행 데이터; 데이터 카드에서 Cosmos Drive Dreams 참조.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic)

<a id="physicalai-smartspaces"></a>
### PhysicalAI-SmartSpaces

사람과 이동 장비 추적을 위한 다중 카메라 영상.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-SmartSpaces](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces)

![PhysicalAI-SmartSpaces official example](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces/resolve/main/demo.gif)

이미지 출처: [PhysicalAI-SmartSpaces](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces)

<a id="physicalai-traffic-anomaly-reasoning"></a>
### PhysicalAI-Traffic-Anomaly-Reasoning

교통 이상 상황 추론·평가 데이터.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Traffic-Anomaly-Reasoning](https://huggingface.co/datasets/nvidia/PhysicalAI-Traffic-Anomaly-Reasoning)

<a id="physicalai-human-1m-100k"></a>
### PhysicalAI-Human-1M-100K

동작·언어 주석이 포함된 사람의 1인칭 영상.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Human-1M-100K](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)

![Human-1M egocentric capture and reconstruction](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K/resolve/main/assets/carousel-preview.webp)

이미지 출처: [PhysicalAI-Human-1M-100K](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)

<a id="physicalai-spatial-intelligence-warehouse"></a>
### PhysicalAI-Spatial-Intelligence-Warehouse

창고 장면의 공간 지능 데이터.

**라이선스·접근:** CC-BY-4.0; 로그인·접근 동의 필요.  
**공식 데이터셋 카드:** [PhysicalAI-Spatial-Intelligence-Warehouse](https://huggingface.co/datasets/nvidia/PhysicalAI-Spatial-Intelligence-Warehouse)

<a id="physicalai-robotics-nurec"></a>
### PhysicalAI-Robotics-NuRec

로봇용 신경 재구성 데이터.

**라이선스·접근:** CC-BY-4.0; 로그인·접근 동의 필요.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-NuRec)

<a id="physicalai-nurec-ppisp"></a>
### PhysicalAI-NuRec-PPISP

재구성·이미지 처리를 위한 장면 촬영 데이터.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-NuRec-PPISP](https://huggingface.co/datasets/nvidia/PhysicalAI-NuRec-PPISP)

<a id="physicalai-spatialintelligence-lyra-sdg"></a>
### PhysicalAI-SpatialIntelligence-Lyra-SDG

공간 지능 연구용 합성 데이터.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-SpatialIntelligence-Lyra-SDG](https://huggingface.co/datasets/nvidia/PhysicalAI-SpatialIntelligence-Lyra-SDG)

<a id="physicalai-worldmodel-synthetic-autonomous-driving-scenarios"></a>
### PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios

월드 모델용 합성 자율주행 장면.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios)

<a id="physicalai-worldmodel-synthetic-embodied-robot-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes

월드 모델용 합성 로봇 장면.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes)

![PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes official example](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes/resolve/main/PhysicalAI-Cosmos-SDG-RobotSim-manipulation-mimicgen.gif)

이미지 출처: [PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes)

<a id="physicalai-worldmodel-synthetic-digital-human-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes

합성 디지털 휴먼 영상 장면.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes)

<a id="physicalai-worldmodel-synthetic-physical-interaction-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes

물리 시뮬레이션 기반 다중 물체 상호작용.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes)

![PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes official example](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes/resolve/main/PhysicalAI-Cosmos-SDG-PhysxSim.gif)

이미지 출처: [PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes)

<a id="physicalai-worldmodel-synthetic-warehouse-operations-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes

합성 창고 운영 및 안전 이벤트 영상.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes)

![PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes official example](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes/resolve/main/assets/hero_2x2.webp)

이미지 출처: [PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes)

<a id="physicalai-event-videos"></a>
### PhysicalAI-Event-Videos

영상 이상 상황·안전 이벤트 및 주석.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Event-Videos](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos)

![PhysicalAI-Event-Videos official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos/resolve/main/physicalai_event_videos_highlights_3x3.gif)

이미지 출처: [PhysicalAI-Event-Videos](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos)

<a id="physicalai-vantage-bench"></a>
### PhysicalAI-VANTAGE-Bench

고정 카메라 영상 이해 벤치마크.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-VANTAGE-Bench](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench)

<a id="physicalai-vantage-bench-subset"></a>
### PhysicalAI-VANTAGE-Bench-Subset

고정 카메라 영상 벤치마크의 부분집합.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)

![PhysicalAI-VANTAGE-Bench-Subset official example](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset/resolve/main/assets/vantage_bench_tasks.png)

이미지 출처: [PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)
