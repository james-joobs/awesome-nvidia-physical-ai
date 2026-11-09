# Robot demonstrations and motion

[Catalog](../../README.md) · [한국어](../ko/datasets-robot-demonstrations.md)

These datasets cover real teleoperation, simulated trajectories, grasps and benchmark tasks. The useful unit for policy training is usually an episode with synchronized observations and actions, tied to an embodiment and task.

## Compare concrete schemas

| Card | Data | Integration check |
|---|---|---|
| [GR00T Teleop G1](#physicalai-robotics-gr00t-teleop-g1) | MP4 and HDF5 with 43-dimensional observation and action vectors. The card documents 640 × 480 RGB at 20 FPS | Confirm full-body and hand joint order and align each video to its matching trajectory |
| [Manipulation Kitchen](#physicalai-robotics-manipulation-kitchen) | LeRobot-format simulated tasks such as opening a drawer or a dishwasher. The card describes a 34-dimensional action and a 13-dimensional object-state observation plus camera streams | Select head, wrist and external cameras deliberately. Match joint and observation definitions to the policy |
| [GraspGen](#physicalai-robotics-graspgen) | Grasp data and object assets | Check the gripper geometry, object frame and units before using grasps as targets |
| [GR00T Eval](#physicalai-robotics-gr00t-eval) | Evaluation assets and tasks | Confirm the protocol and keep evaluation data separate from training |

![Official simulated kitchen world-camera rollout](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen/resolve/main/assets/episode_000004_world.gif)

This official kitchen example shows a world view. The card also provides head and wrist views for comparison. A policy using wrist images sees a different crop and motion pattern from an evaluation replay using the world camera. [Official kitchen camera and schema examples](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen#dataset-format)

## Worked example — test ingestion on one trajectory

Read a single G1 pick-and-place trajectory, decode the matching MP4, and plot or replay several action and observation joints against the contact frame. Check dimension, order, units, sample timing and whether the stored action is compatible with the controller. Before mixing real and simulated data, keep embodiment and source labels and split by original episode or collection session. [Official G1 card](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1) · [GR00T model](groot-model.md)

## Dataset details

<a id="physicalai-robotics-gr00t-x-embodiment-sim"></a>
### PhysicalAI-Robotics-GR00T-X-Embodiment-Sim

Simulated trajectories across robot embodiments for GR00T post-training.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GR00T-X-Embodiment-Sim](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-X-Embodiment-Sim)

<a id="physicalai-gr00t-tuned-tasks"></a>
### PhysicalAI-GR00T-Tuned-Tasks

Multimodal GR1 tabletop manipulation trajectories.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-GR00T-Tuned-Tasks](https://huggingface.co/datasets/nvidia/PhysicalAI-GR00T-Tuned-Tasks)

<a id="physicalai-robotics-gr00t-gr1"></a>
### PhysicalAI-Robotics-GR00T-GR1

Third-person video of GR1 robot tasks.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GR00T-GR1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-GR1)

<a id="physicalai-robotics-gr00t-teleop-g1"></a>
### PhysicalAI-Robotics-GR00T-Teleop-G1

Teleoperated Unitree G1 demonstrations.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GR00T-Teleop-G1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1)

![PhysicalAI-Robotics-GR00T-Teleop-G1 official example](https://cdn-uploads.huggingface.co/production/uploads/67b8da81d01134f89899b4a7/nnQttu2PywkTLVMcuNL42.jpeg)

Image source: [PhysicalAI-Robotics-GR00T-Teleop-G1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1)

<a id="gr00t-n1-7-appletoplate"></a>
### GR00T-N1.7-AppleToPlate

G1 apple pick-and-place teleoperation demonstrations.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [GR00T-N1.7-AppleToPlate](https://huggingface.co/datasets/nvidia/GR00T-N1.7-AppleToPlate)

<a id="physicalai-robotics-gr00t-teleop-sim"></a>
### PhysicalAI-Robotics-GR00T-Teleop-Sim

Simulated teleoperation demonstrations.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GR00T-Teleop-Sim](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-Sim)

<a id="physicalai-robotics-gr00t-teleop-gr1"></a>
### PhysicalAI-Robotics-GR00T-Teleop-GR1

GR1 teleoperation data.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GR00T-Teleop-GR1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-GR1)

<a id="physicalai-robotics-gr00t-eval"></a>
### PhysicalAI-Robotics-GR00T-Eval

GR00T robot evaluation data.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GR00T-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Eval)

![PhysicalAI-Robotics-GR00T-Eval official example](https://huggingface.co/datasets/nvidia/EVAL-175/resolve/main/gr1_behavior/0_Open%20the%20box.png)

Image source: [PhysicalAI-Robotics-GR00T-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Eval)

<a id="physicalai-robotics-manipulation-kitchen"></a>
### PhysicalAI-Robotics-Manipulation-Kitchen

Simulated kitchen manipulation trajectories in LeRobot format.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-Manipulation-Kitchen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen)

![Robot dishwasher manipulation demonstration](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen/resolve/main/assets/episode_000009.gif)

Image source: [PhysicalAI-Robotics-Manipulation-Kitchen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen)

<a id="physicalai-robotics-manipulation-singlearm"></a>
### PhysicalAI-Robotics-Manipulation-SingleArm

Simulated single-arm robot manipulation.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-Manipulation-SingleArm](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-SingleArm)

<a id="physicalai-robotics-manipulation-objects"></a>
### PhysicalAI-Robotics-Manipulation-Objects

Simulated object pick-and-place trajectories.

**License and access:** License unverified; public.  
**Official dataset card:** [PhysicalAI-Robotics-Manipulation-Objects](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects)

![PhysicalAI-Robotics-Manipulation-Objects official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects/resolve/main/assets/episode_000028.gif)

Image source: [PhysicalAI-Robotics-Manipulation-Objects](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects)

<a id="physicalai-robotics-manipulation-augmented"></a>
### PhysicalAI-Robotics-Manipulation-Augmented

Synthetic annotated cube-stacking demonstrations.

**License and access:** License unverified; public.  
**Official dataset card:** [PhysicalAI-Robotics-Manipulation-Augmented](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Augmented)

<a id="physicalai-robotics-manipulation-kitchen-demos"></a>
### PhysicalAI-Robotics-Manipulation-Kitchen-Demos

Human-teleoperated kitchen task demonstrations.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-Manipulation-Kitchen-Demos](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen-Demos)

<a id="physicalai-robotics-graspgen"></a>
### PhysicalAI-Robotics-GraspGen

Candidate grasps for multiple grippers and objects.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-GraspGen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen)

![PhysicalAI-Robotics-GraspGen official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen/resolve/main/assets/cover.png)

Image source: [PhysicalAI-Robotics-GraspGen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen)

<a id="physicalai-robotics-locomanipulation-grail"></a>
### PhysicalAI-Robotics-Locomanipulation-GRAIL

Robot locomotion and manipulation motion data.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-Locomanipulation-GRAIL](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL)

![PhysicalAI-Robotics-Locomanipulation-GRAIL official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL/resolve/main/assets/videos/pickup_table.gif)

Image source: [PhysicalAI-Robotics-Locomanipulation-GRAIL](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL)

<a id="physicalai-robotics-open-h-embodiment"></a>
### PhysicalAI-Robotics-Open-H-Embodiment

Surgical robotics and ultrasound autonomy data initiative.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-Open-H-Embodiment](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment)

<a id="physicalai-robotics-mindmap-gr1-drill-in-box"></a>
### PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box

GR1 drill-in-box task trajectories.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box)

<a id="physicalai-robotics-mindmap-gr1-stick-in-bin"></a>
### PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin

GR1 stick-in-bin task trajectories.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin)

<a id="physicalai-robotics-mindmap-franka-mug-in-drawer"></a>
### PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer

Franka mug-in-drawer task trajectories.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer)

<a id="physicalai-robotics-mindmap-franka-cube-stacking"></a>
### PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking

Franka cube-stacking task trajectories.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking)
