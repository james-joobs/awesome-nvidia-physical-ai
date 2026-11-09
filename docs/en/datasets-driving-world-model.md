# Driving, video, and world-model data

[Catalog](../../README.md) · [한국어](../ko/datasets-driving-world-model.md)

The catalog includes recorded driving sensors, reconstructed scenes, synthetic physical interactions, and video reasoning benchmarks. Use the dataset type to decide what a valid input or evaluation looks like.

## Select by the work you are doing

| Need | Representative resource | Check first |
|---|---|---|
| Work with observed sensor data | [PhysicalAI-Autonomous-Vehicles](#physicalai-autonomous-vehicles) or [NCore](#physicalai-autonomous-vehicles-ncore) | Sensor modalities, clip IDs, timing, calibration and access |
| Render an existing reconstruction | [AV NuRec](#physicalai-autonomous-vehicles-nurec) | Scene asset format, renderer compatibility and reference camera poses |
| Evaluate visual understanding | [VANTAGE-Bench](#physicalai-vantage-bench) | Task folder, submission format and task-specific metric |
| Explore egocentric motion and language | [Human-1M](#physicalai-human-1m-100k) | Camera availability, timestamps, tracking confidence and T1/T2 labels |

![NVIDIA VANTAGE-Bench official task breakdown](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench/resolve/main/assets/vantage_bench_tasks.png)

The official diagram groups semantic, temporal, spatial and spatiotemporal tasks. The card lists separate metrics, such as interval mIoU for temporal localization and accuracy for video QA. Ground-truth annotations for official evaluation are held server-side. [Official VANTAGE card and submission details](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench#evaluation)

## Worked example — preserve provenance across replay and generation

Select one driving clip with a verified source ID. For replay, inspect timestamps and camera extrinsics and render from an original pose before trying a novel view. For video variants, record source ID, condition inputs, model revision and seed. Keep derived versions in the same split as the original. Evaluate understanding on a benchmark with its own protocol instead of treating generated labels as ground truth. [Official NuRec scene guide](https://docs.nvidia.com/nurec/nurec/model.html) · [NuRec](nurec.md) · [Human-1M Explorer](human-1m-explorer.md)

## Dataset details

<a id="physicalai-autonomous-vehicles"></a>
### PhysicalAI-Autonomous-Vehicles

Real-world autonomous-driving multisensor data.

**License and access:** Other terms; check card; Login and access acceptance required.  
**Official dataset card:** [PhysicalAI-Autonomous-Vehicles](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)

<a id="physicalai-autonomous-vehicles-nurec"></a>
### PhysicalAI-Autonomous-Vehicles-NuRec

Driving scenes reconstructed with NuRec.

**License and access:** Other terms; check card; Login and access acceptance required.  
**Official dataset card:** [PhysicalAI-Autonomous-Vehicles-NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec)

<a id="nurec-av-object-benchmark"></a>
### NuRec-AV-Object-Benchmark

Object-centric 3D reconstruction benchmark for driving.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [NuRec-AV-Object-Benchmark](https://huggingface.co/datasets/nvidia/NuRec-AV-Object-Benchmark)

<a id="physicalai-autonomous-vehicles-ncore"></a>
### PhysicalAI-Autonomous-Vehicles-NCore

Autonomous-driving sensor data in the NCore ecosystem.

**License and access:** Other terms; check card; Login and access acceptance required.  
**Official dataset card:** [PhysicalAI-Autonomous-Vehicles-NCore](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NCore)

<a id="physicalai-autonomous-vehicles-foundation4d"></a>
### PhysicalAI-Autonomous-Vehicles-Foundation4D

Autonomous-driving data for 4D reconstruction.

**License and access:** Other terms; check card; Login and access acceptance required.  
**Official dataset card:** [PhysicalAI-Autonomous-Vehicles-Foundation4D](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-Foundation4D)

<a id="physicalai-autonomous-vehicle-cosmos-drive-dreams"></a>
### PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams

Cosmos-based synthetic driving data.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams)

![PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams official example](https://cdn-uploads.huggingface.co/production/uploads/658529d61c461dfe88afe8e8/ACduHba6o1VY4ApXpglAo.png)

Image source: [PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Drive-Dreams)

<a id="physicalai-autonomous-vehicle-cosmos-synthetic"></a>
### PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic

Synthetic driving data; card refers to Cosmos Drive Dreams.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicle-Cosmos-Synthetic)

<a id="physicalai-smartspaces"></a>
### PhysicalAI-SmartSpaces

Multi-camera video for tracking people and mobile equipment.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-SmartSpaces](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces)

![PhysicalAI-SmartSpaces official example](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces/resolve/main/demo.gif)

Image source: [PhysicalAI-SmartSpaces](https://huggingface.co/datasets/nvidia/PhysicalAI-SmartSpaces)

<a id="physicalai-traffic-anomaly-reasoning"></a>
### PhysicalAI-Traffic-Anomaly-Reasoning

Traffic anomaly reasoning and evaluation data.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Traffic-Anomaly-Reasoning](https://huggingface.co/datasets/nvidia/PhysicalAI-Traffic-Anomaly-Reasoning)

<a id="physicalai-human-1m-100k"></a>
### PhysicalAI-Human-1M-100K

Egocentric human video with motion and language annotations.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Human-1M-100K](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)

![Human-1M egocentric capture and reconstruction](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K/resolve/main/assets/carousel-preview.webp)

Image source: [PhysicalAI-Human-1M-100K](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)

<a id="physicalai-spatial-intelligence-warehouse"></a>
### PhysicalAI-Spatial-Intelligence-Warehouse

Spatial intelligence data for warehouse scenes.

**License and access:** CC-BY-4.0; Login and access acceptance required.  
**Official dataset card:** [PhysicalAI-Spatial-Intelligence-Warehouse](https://huggingface.co/datasets/nvidia/PhysicalAI-Spatial-Intelligence-Warehouse)

<a id="physicalai-robotics-nurec"></a>
### PhysicalAI-Robotics-NuRec

Neural reconstruction data for robotics.

**License and access:** CC-BY-4.0; Login and access acceptance required.  
**Official dataset card:** [PhysicalAI-Robotics-NuRec](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-NuRec)

<a id="physicalai-nurec-ppisp"></a>
### PhysicalAI-NuRec-PPISP

Scene captures for reconstruction and image processing.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-NuRec-PPISP](https://huggingface.co/datasets/nvidia/PhysicalAI-NuRec-PPISP)

<a id="physicalai-spatialintelligence-lyra-sdg"></a>
### PhysicalAI-SpatialIntelligence-Lyra-SDG

Synthetic spatial-intelligence research data.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-SpatialIntelligence-Lyra-SDG](https://huggingface.co/datasets/nvidia/PhysicalAI-SpatialIntelligence-Lyra-SDG)

<a id="physicalai-worldmodel-synthetic-autonomous-driving-scenarios"></a>
### PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios

Synthetic autonomous-driving scenes for world models.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Autonomous-Driving-Scenarios)

<a id="physicalai-worldmodel-synthetic-embodied-robot-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes

Synthetic embodied-robot scenes for world models.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes)

![PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes official example](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes/resolve/main/PhysicalAI-Cosmos-SDG-RobotSim-manipulation-mimicgen.gif)

Image source: [PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes)

<a id="physicalai-worldmodel-synthetic-digital-human-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes

Synthetic digital-human video scenes.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Digital-Human-Scenes)

<a id="physicalai-worldmodel-synthetic-physical-interaction-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes

Simulated multi-object physical interactions.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes)

![PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes official example](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes/resolve/main/PhysicalAI-Cosmos-SDG-PhysxSim.gif)

Image source: [PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Physical-Interaction-Scenes)

<a id="physicalai-worldmodel-synthetic-warehouse-operations-scenes"></a>
### PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes

Synthetic warehouse operations and safety events.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes)

![PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes official example](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes/resolve/main/assets/hero_2x2.webp)

Image source: [PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes](https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Warehouse-Operations-Scenes)

<a id="physicalai-event-videos"></a>
### PhysicalAI-Event-Videos

Video anomalies, safety events, and annotations.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-Event-Videos](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos)

![PhysicalAI-Event-Videos official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos/resolve/main/physicalai_event_videos_highlights_3x3.gif)

Image source: [PhysicalAI-Event-Videos](https://huggingface.co/datasets/nvidia/PhysicalAI-Event-Videos)

<a id="physicalai-vantage-bench"></a>
### PhysicalAI-VANTAGE-Bench

Fixed-camera video understanding benchmark.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-VANTAGE-Bench](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench)

<a id="physicalai-vantage-bench-subset"></a>
### PhysicalAI-VANTAGE-Bench-Subset

Subset of the fixed-camera video benchmark.

**License and access:** Other terms; check card; public.  
**Official dataset card:** [PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)

![PhysicalAI-VANTAGE-Bench-Subset official example](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset/resolve/main/assets/vantage_bench_tasks.png)

Image source: [PhysicalAI-VANTAGE-Bench-Subset](https://huggingface.co/datasets/nvidia/PhysicalAI-VANTAGE-Bench-Subset)
