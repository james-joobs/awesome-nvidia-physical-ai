# 자율주행·영상·월드 모델 데이터

[전체 목록](../../README.ko.md) · [English](../en/datasets-driving-world-model.md)

공식 데이터셋 카드를 기준으로 형식, 접근 조건과 라이선스를 각각 확인한다. 공개 접근과 제한 없는 이용 권한은 다르다.

## 선택 및 활용 흐름

이 그림은 개념적 사용 흐름이다.

```mermaid
flowchart LR
  S0["시나리오와 모달리티 선택"]
  S1["접근 조건 확인"]
  S2["영상 또는 장면 처리"]
  S3["학습 또는 평가"]
  S0 --> S1 --> S2 --> S3
```

## 데이터셋별 상세

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

![PhysicalAI-VANTAGE-Bench official example](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench/resolve/main/assets/vantage_bench_tasks.png)

이미지 출처: [PhysicalAI-VANTAGE-Bench](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench)

<a id="physicalai-vantage-bench-subset"></a>
### PhysicalAI-VANTAGE-Bench-Subset

고정 카메라 영상 벤치마크의 부분집합.

**라이선스·접근:** 별도 약관 확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)

![PhysicalAI-VANTAGE-Bench-Subset official example](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset/resolve/main/assets/vantage_bench_tasks.png)

이미지 출처: [PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)

