# 3D assets and environments

[Catalog](../../README.md) · [한국어](../ko/datasets-3d-assets.md)

These resources supply reusable geometry, scenes, or objects for simulation. Choose a package by the simulator and task. A warehouse scenario, a graspable prop, and a library of MJCF objects have different integration requirements.

## From catalog to usable scene

| Stage | What to inspect |
|---|---|
| Select assets | File format, package dependencies, asset class, labels and license |
| Compose | Relative references and payloads, up axis and stage units, and available semantic labels |
| Configure physics | Collider shape, mass, rigid body or articulation and contact behavior |
| Validate | Load in the target simulator, render and run one short interaction before preparing a batch |

![NVIDIA Isaac Sim stage view for adding rigid bodies](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01/resolve/main/images/PhysicalAI_Dataset_02.png)

In the warehouse card's official walkthrough, select the top-level asset Xform in the stage. The USD scene uses payloads to compose individual assets. The documented scene ships with colliders, and assets that should move can be configured with rigid bodies as shown in the card. Its CSV catalog maps asset paths to classification, semantic Q-codes and approximate masses. [Official warehouse card and setup](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01#how-to-use)

## Worked example — test a shelf pick

Select a small set of warehouse props using the catalog. Load the USD scene and use one object to test grasp contact and gravity. Check its scale against the gripper, verify that its mass and collider suit the task, and confirm the camera can see the object before randomizing placement. For an MJCF kitchen benchmark, use the compatible object package and inspect mesh and contact settings in the target environment. [Kitchen MJCF card](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF) · [SimReady](simready.md)

## Dataset details

<a id="simready-assets"></a>
### simready-assets

SimReady 3D props and objects.

**License and access:** CC BY 4.0; public.  
**Official dataset card:** [simready-assets](https://huggingface.co/datasets/nvidia/simready-assets)

<a id="simready-dsx"></a>
### simready-dsx

SimReady assets for AI factory digital twins.

**License and access:** CC BY 4.0; public.  
**Official dataset card:** [simready-dsx](https://huggingface.co/datasets/nvidia/simready-dsx)

<a id="isaacsim-assets"></a>
### isaacsim-assets

Isaac Sim assets and sample content.

**License and access:** License unverified.  
**Official dataset card:** [isaacsim-assets](https://huggingface.co/datasets/nvidia/isaacsim-assets)

<a id="physicalai-simready-warehouse-01"></a>
### PhysicalAI-SimReady-Warehouse-01

OpenUSD warehouse scene for simulation.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-SimReady-Warehouse-01](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01)

![SimReady warehouse simulation scene](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01/resolve/main/images/PhysicalAI_Dataset_01.png)

Image source: [PhysicalAI-SimReady-Warehouse-01](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01)

<a id="physicalai-digitalcousin-assets"></a>
### PhysicalAI-DigitalCousin-Assets

Assets for simulated GR1 tabletop environments.

**License and access:** CC-BY-NC-4.0; public.  
**Official dataset card:** [PhysicalAI-DigitalCousin-Assets](https://huggingface.co/datasets/nvidia/PhysicalAI-DigitalCousin-Assets)

<a id="physicalai-robotics-manipulation-objects-kitchen-mjcf"></a>
### PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF

MJCF kitchen object assets.

**License and access:** CC-BY-4.0; public.  
**Official dataset card:** [PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF)

![PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF/resolve/main/4x4_collage_images.png)

Image source: [PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF)

<a id="physicalai-robotics-physicalassets-vomp"></a>
### PhysicalAI-Robotics-PhysicalAssets-VoMP

Assets for vision-based robot motion planning research.

**License and access:** License unverified; public.  
**Official dataset card:** [PhysicalAI-Robotics-PhysicalAssets-VoMP](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP)

<a id="physicalai-robotics-physicalassets-vomp-eval"></a>
### PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval

Evaluation assets for vision-based motion planning.

**License and access:** License unverified; public.  
**Official dataset card:** [PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval)
