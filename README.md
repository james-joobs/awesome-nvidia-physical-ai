<div align="center">

# Awesome NVIDIA Physical AI

**A guide to the simulation, data, and robotics learning ecosystem behind physical AI.**

[![English](https://img.shields.io/badge/English-selected-76B900?style=for-the-badge)](README.md) [![한국어](https://img.shields.io/badge/한국어-switch-555555?style=for-the-badge)](README.ko.md)

[Open-source projects](#1-projects-with-confirmed-open-source-code) · [Platforms and models](#2-platforms-models-products-standards-and-restricted-code) · [External tools](#3-external-models-and-tools) · [How they fit together](#4-how-the-pieces-fit-together)

</div>

---

This guide catalogs the projects and technologies discussed in the source conversation, including related projects outside NVIDIA. It links to official repositories and documentation and distinguishes open-source code from models, products, and source-available code with restrictions.

**Checked:** November 9, 2026. A public repository does not imply that its model weights, datasets, binaries, cloud services, or dependencies share the same license. License notes below describe the linked code where confirmed; check the exact version and individual components before use. “Unverified” means the relevant scope or license could not be established, not that it is closed source.

## 1. Projects with confirmed open-source code

### Physics, 3D, and simulation

| Project | Role | Code license and notes | Official source |
|---|---|---|---|
| Newton | Warp-based GPU physics engine and robotics simulation solvers | Apache-2.0 | [Repository](https://github.com/newton-physics/newton) |
| NVIDIA Warp | Python framework for GPU-accelerated physics and geometry | Apache-2.0 | [Repository](https://github.com/NVIDIA/warp) |
| NVIDIA PhysX | Physics engine for rigid bodies, collisions, and more | BSD-3-Clause; check terms for additional components | [Repository](https://github.com/NVIDIA-Omniverse/PhysX) |
| MuJoCo Warp (MJWarp) | Warp-based acceleration of MuJoCo physics | Apache-2.0; a Google DeepMind project | [Repository](https://github.com/google-deepmind/mujoco_warp) |
| OpenUSD | Framework for composing and exchanging 3D scenes and assets | Modified BSD-style license; distinguish the implementation from the standard and trademarks | [Repository](https://github.com/PixarAnimationStudios/OpenUSD) |
| Isaac Sim | Reference application for simulating robots, sensors, and environments | Repository code: Apache-2.0; distribution and dependencies may have separate NVIDIA terms | [Repository](https://github.com/isaac-sim/IsaacSim) |
| PhysicsNeMo | Framework for physics-informed AI and surrogate models | Apache-2.0 | [Repository](https://github.com/NVIDIA/physicsnemo) |

### Robot learning, capture, and control

| Project | Role | Code license and notes | Official source |
|---|---|---|---|
| Isaac Lab | Robot-learning environments for reinforcement and imitation learning | BSD-3-Clause; backends and dependencies have separate terms | [Repository](https://github.com/isaac-sim/IsaacLab) |
| Isaac Lab-Arena | Composable robot task environments and policy evaluation | Apache-2.0; Isaac Sim and other dependencies have separate terms | [Repository](https://github.com/isaac-sim/IsaacLab-Arena) |
| Isaac Capture (formerly Isaac Teleop) | Teleoperation and egocentric capture, recording, and retargeting | Apache-2.0 by default; EgoPost uses OpenMDW-1.1, while CloudXR and some optional packages have separate proprietary terms | [Repository](https://github.com/NVIDIA/IsaacCapture) |
| AutoData | Expands a small set of demonstrations into trajectories across varied task conditions | Apache-2.0; Isaac Sim and specific cuRobo components have separate terms | [Repository](https://github.com/isaac-sim/AutoData) |
| Video-to-Data (V2D) | Reconstructs scenes and motion from video for robot-learning workflows | Code: Apache-2.0; documentation and skills: CC-BY-4.0; dependent models have separate terms | [Repository](https://github.com/nvidia-isaac/video_to_data) |
| Isaac GR00T code | Training, inference, and deployment code for GR00T robot policies | Code: Apache-2.0; models and weights have separate terms | [Repository](https://github.com/NVIDIA/Isaac-GR00T) |
| cuRobo | GPU-accelerated inverse kinematics and robot motion planning | Repository: Apache-2.0; check terms for specific components distributed with AutoData | [Repository](https://github.com/NVlabs/curobo) |
| LeRobot | Robot datasets and model-training tools; integrates with Capture | Apache-2.0; a Hugging Face project | [Repository](https://github.com/huggingface/lerobot) |
| Isaac ROS | Collection of GPU-accelerated ROS 2 robotics packages | Package terms vary; check licenses for each repository and distribution | [Documentation](https://nvidia-isaac-ros.github.io/) · [Common code](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common) |

### Data generation, processing, and orchestration

| Project | Role | Code license and notes | Official source |
|---|---|---|---|
| Cosmos Data Factory (CDF; formerly Physical AI Data Factory) | Workflows and skills for generating and processing video and images | Code: Apache-2.0; documentation and skills: CC-BY-4.0; models and services have separate terms | [Repository](https://github.com/NVIDIA/cosmos-data-factory) |
| CDF Auto Labeling (formerly paidf-auto-labeling) | Automated video and image annotation workflows | Apache-2.0; models and services have separate terms | [Repository](https://github.com/NVIDIA/cdf-auto-labeling) |
| CDF Augmentation (formerly paidf-augmentation) | Video, image, and text augmentation workflows | Apache-2.0; models have separate terms | [Repository](https://github.com/NVIDIA/cdf-augmentation) |
| CDF Simulation (formerly paidf-simulation) | Synthetic data generation with Isaac Sim and Replicator | Apache-2.0; simulator and assets have separate terms | [Repository](https://github.com/NVIDIA/cdf-simulation) |
| Cosmos Curator | Splits, filters, annotates, and deduplicates video and images | Apache-2.0; models have separate terms | [Repository](https://github.com/NVIDIA/cosmos-curator) |
| Cosmos Evaluator | Evaluates generated video for object consistency, physical plausibility, and other qualities | Apache-2.0; model terms vary by checker | [Repository](https://github.com/NVIDIA/cosmos-evaluator) |
| OSMO | Manages GPU-backed simulation and training workflows | Apache-2.0 | [Repository](https://github.com/NVIDIA/OSMO) |
| TensorRT public code | Samples, plugins, and tools for inference optimization | Repository: Apache-2.0; this does not cover the entire TensorRT binary SDK | [Repository](https://github.com/NVIDIA/TensorRT) |
| Holoscan SDK | Low-latency streaming and sensor AI pipelines | Apache-2.0; external components have separate terms | [Repository](https://github.com/nvidia-holoscan/holoscan-sdk) |

### Autonomous driving

| Project | Role | Code license and notes | Official source |
|---|---|---|---|
| AlpaSim | Closed-loop simulation for autonomous-driving policies | Code: Apache-2.0; models and data have separate terms | [Repository](https://github.com/NVlabs/alpasim) |
| AlpaGym | Reinforcement learning for autonomous-driving policies | Code: Apache-2.0; dependencies and models have separate terms | [Repository](https://github.com/NVlabs/alpagym) |

## 2. Platforms, models, products, standards, and restricted code

Public access alone does not establish an open-source license or permission for commercial use. Unverified terms are identified explicitly.

| Name | Role or category | Availability and license status | Official source |
|---|---|---|---|
| NVIDIA Omniverse | OpenUSD-based 3D development platform | Product, SDK, and publicly available components have different terms | [Official page](https://developer.nvidia.com/omniverse) |
| SimReady | Guidelines and specifications for simulation-ready 3D assets | Asset licenses vary; not a single software project | [Documentation](https://docs.omniverse.nvidia.com/simready/latest/index.html) |
| NuRec | Neural reconstruction and rendering of real environments | Product/technology; complete source and license scope unverified | [Official page](https://developer.nvidia.com/omniverse/nurec) |
| Cosmos and Cosmos 3 | World-model and tooling platform and model family | The [Cosmos repository](https://github.com/NVIDIA/cosmos) specifies OpenMDW-1.1 for its code and models; it is not assumed to be OSI-approved. Other repositories have their own terms | [Repository](https://github.com/NVIDIA/cosmos) |
| Cosmos Predict / Transfer / Reason | Model families for world/video generation, visual transformation, and scene reasoning | Check the terms for each model version and its weights | [Cosmos](https://github.com/NVIDIA/cosmos) |
| Cosmos Embed / Dataset Search | Multimodal embedding model/service and video-search microservices | Complete source availability and license scope unverified | [Documentation](https://docs.nvidia.com/cosmos/cds/latest/introduction.html) |
| Isaac GR00T / GR00T N1.7 | Robot action foundation model and platform | Code and weights have separate licenses; check the model version | [Repository](https://github.com/NVIDIA/Isaac-GR00T) |
| GR00T-Mimic / GR00T-Dreams | Robot demonstration and synthetic-data generation techniques/workflows | Independent project status and terms for implementations and models require individual verification | [GR00T](https://github.com/NVIDIA/Isaac-GR00T) |
| Isaac Manipulator | Reference workflows for robotic-arm perception, grasping, and planning | Isaac ROS packages, models, and components have different terms | [Isaac ROS documentation](https://nvidia-isaac-ros.github.io/) |
| Isaac RLPT | Workflow for improving pretrained policies with reinforcement learning | Independent repository and license unverified | [Isaac Lab](https://github.com/isaac-sim/IsaacLab) |
| Replicator | Synthetic data generation tool within Omniverse/Isaac Sim | Product component; complete source availability and independent license unverified | [Isaac Sim documentation](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/index.html) |
| EgoHand / EgoPost | Capture components for egocentric hand and camera motion | EgoPost uses OpenMDW-1.1; EgoHand's independent license is unverified | [Isaac Capture](https://github.com/NVIDIA/IsaacCapture) |
| MimicGen | Generates varied robot demonstrations from existing demonstrations | Source available under NVIDIA Source Code License; do not assume unrestricted open-source use | [Repository](https://github.com/NVlabs/mimicgen) |
| DexMimicGen | Research on generating bimanual and multi-manipulator demonstrations | Code uses NVIDIA Source Code License; data uses CC-BY-4.0. Check code restrictions | [Repository](https://github.com/NVlabs/dexmimicgen) |
| SkillGen / SkillMimicGen | Connects demonstration segments with motion planning | Check terms for the Isaac Lab implementation and dependencies such as cuRobo separately; paper and implementation names differ | [Isaac Lab documentation](https://github.com/isaac-sim/IsaacLab/blob/main/docs/source/features/imitation-learning/skillgen.rst) |
| Isaac Lab Eureka | Research code for generating reward functions with language models | Public repository; applicable license unverified | [Repository](https://github.com/NVlabs/IsaacLabEureka) |
| FoundationPose | Research code and models for 6D object pose estimation and tracking | Research repository code restricts commercial use; separately distributed models have separate terms | [Code](https://github.com/NVlabs/FoundationPose) · [Model card](https://huggingface.co/nvidia/foundationpose) |
| FoundationStereo | Research code and models for stereo depth estimation | Research code has non-commercial restrictions; check separately distributed commercial models | [Repository](https://github.com/NVlabs/FoundationStereo) |
| nvblox | 3D mapping and obstacle representation | Source is public; scope of mixed repository licenses unverified | [Repository](https://github.com/nvidia-isaac/nvblox) |
| AnomalyGen | Generates defect images from a small number of examples | Public repository; terms for code, models, and adapters unverified | [Repository](https://github.com/NVIDIA/cdf-anomalygen) |
| CDF Orchestration | Runs and manages data factory workflows | Public repository; license and execution-service terms unverified | [Repository](https://github.com/NVIDIA/cdf-orchestration) |
| Alpamayo | Autonomous-driving reasoning and action model family | Access and license terms for weights vary by model version | [AlpaSim model guide](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md) |
| Metropolis / VSS | Video AI platform / video search and summarization workflow | Platform and services; individual SDKs and models have separate terms | [Metropolis](https://developer.nvidia.com/metropolis) |
| DeepStream | Real-time video analytics SDK | Product SDK; samples and binaries have separate terms | [Official page](https://developer.nvidia.com/deepstream-sdk) |
| TAO Toolkit | Vision AI model training and fine-tuning | Product/SDK; check model and component terms | [Official page](https://developer.nvidia.com/tao-toolkit) |
| Jetson / JetPack | Edge AI hardware / software development kit | Product and distribution; component terms vary | [Jetson](https://developer.nvidia.com/embedded/jetson-modules) · [JetPack](https://developer.nvidia.com/embedded/jetpack) |
| NVIDIA DRIVE | Autonomous-driving hardware and software platform | Product/platform; check component terms | [Official page](https://developer.nvidia.com/drive) |
| RTX / DGX Spark | GPU product family / AI computer | Hardware products, not open-source projects | [RTX](https://www.nvidia.com/en-us/geforce/graphics-cards/) · [DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) |

## 3. External models and tools

These were mentioned as components or dependencies in workflows such as V2D. They are not necessarily NVIDIA projects. Code and checkpoint terms may differ.

| Name | Role | Status and official source |
|---|---|---|
| LangGraph | Agent workflow orchestration | [Repository](https://github.com/langchain-ai/langgraph); check version and license |
| SigLIP 2 | Video/image and text representation model | [Model card](https://huggingface.co/google/siglip2-base-patch16-224); model terms vary |
| Grounding DINO | Text-conditioned object detection | [Repository](https://github.com/IDEA-Research/GroundingDINO); weights have separate terms |
| SAM 2 / SAM 3D | Video/image segmentation / 3D reconstruction | [SAM 2](https://github.com/facebookresearch/sam2) · [SAM 3D Objects](https://github.com/facebookresearch/sam-3d-objects); check model terms |
| MoGe | Single-image 3D geometry estimation | [Repository](https://github.com/microsoft/MoGe); check code and weight terms |
| SMPL | Parametric human body shape and pose model family | [Project](https://smpl.is.tue.mpg.de/); model data has separate terms |
| PyTorch | Machine-learning framework | [Repository](https://github.com/pytorch/pytorch); BSD-style license, dependencies separate |
| ROS 2 | Robotics middleware | [Documentation](https://docs.ros.org/en/rolling/); package licenses vary |
| CUDA / TensorRT / ONNX | GPU computing platform / inference SDK / model interchange format | CUDA and TensorRT distributions have separate product terms; [ONNX](https://github.com/onnx/onnx) has a public implementation and standard. TensorRT public code is listed above |
| MCAP / HDF5 / URDF / CAD | Recording format / data format / robot description format / design concept | A format or concept and its implementations have distinct licenses. [MCAP](https://mcap.dev/) · [HDF5](https://www.hdfgroup.org/solutions/hdf5/) · [URDF](https://docs.ros.org/en/rolling/Tutorials/Intermediate/URDF/URDF-Main.html) |

## 4. How the pieces fit together

1. **Capture:** Isaac Capture records teleoperation or egocentric data; V2D reconstructs information from video. Data formats and retargeting compatibility depend on the task.
2. **Generate and augment:** AutoData primarily expands robot trajectories. CDF, Cosmos, and Replicator support the production and processing of visual data. These are composable workflows, not a single automatically connected pipeline.
3. **Simulate and train:** Isaac Lab can use Newton on Warp or other physics backends. Isaac Sim provides sensors, rendering, and robot environments; some Lab workflows run without Isaac Sim. See [Isaac Lab releases](https://github.com/isaac-sim/IsaacLab/releases).
4. **Evaluate and deploy:** Policies such as GR00T can be trained on the data, evaluated in Lab-Arena or a simulator, and integrated with Isaac ROS, TensorRT, and Jetson. OSMO and CDF Orchestration manage workflow execution.

**Names and scope:** Isaac Teleop is an earlier name incorporated into Isaac Capture. The Physical AI Data Factory repository redirects to Cosmos Data Factory, and the three `paidf-*` repositories listed above redirect to `cdf-*` names. GR00T uses zeros. Video Data Augmentation, Event Video Generation, Defect Image Generation, Image Attribute Augmentation, and Autonomous Vehicle Dataset Generation are CDF workflows, not assumed to be independent repositories. Ego Pipeline, Video Ingestion Agent, Reconstruction, Robotic Grounding, and recording/replay are components or workflow stages.

## Verification and limitations

Names were collected from the source conversation and duplicate names were consolidated. Official GitHub repositories were checked against repository responses and README/license information; redirects use the current destination. Official documentation and product links were also checked. Access can change and some sites may restrict automated access, regions, or require login. Repository visibility, a specific version's license, model-weight terms, and third-party dependencies are separate questions: review the applicable LICENSE and model card before adoption. GPU compatibility and model-version claims in the earlier conversation were not established by this license review.
