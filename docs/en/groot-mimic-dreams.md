# GR00T-Mimic / GR00T-Dreams

[← Back to catalog](../../README.md) · [한국어](../ko/groot-mimic-dreams.md)

GR00T-Mimic and GR00T-Dreams both expand robot-learning data, with different inputs. The published Mimic blueprint augments recorded demonstrations in simulation. The DreamGen implementation of Dreams generates robot videos with a Cosmos world model and infers corresponding action labels.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Mimic blueprint** | Teleoperation provides seed actions and scenes. Isaac Lab and Isaac Sim generate adapted trajectories and visual observations. The published blueprint also describes Cosmos-based visual augmentation before policy learning. |
| **DreamGen video stage** | A robot scene image and language instruction condition a video world model. The repository documents Cosmos Predict2 post-training and generation, whose output is a set of synthetic MP4 clips. |
| **DreamGen action stage** | An inverse dynamics model (IDM) estimates robot actions from video. The documented scripts support specific embodiments and convert the results into LeRobot-format data for policy fine-tuning. |

![The Mimic blueprint shows how teleoperation seeds feed simulated trajectory and image generation, followed by data augmentation and training.](https://developer-blogs.nvidia.com/wp-content/uploads/2025/01/nvidia-isaac-groot-blueprint-architecture-1024x446.png)

The Mimic blueprint shows how teleoperation seeds feed simulated trajectory and image generation, followed by data augmentation and training. [Official figure source](https://developer.nvidia.com/blog/building-a-synthetic-motion-generation-pipeline-for-humanoid-robot-learning/)

![The Dreams reference architecture distinguishes generated video from inferred actions. The latter are necessary if the target policy needs robot action supervision.](https://raw.githubusercontent.com/NVIDIA/GR00T-Dreams/main/reference_architecture/reference_architecture_diagram.png)

The Dreams reference architecture distinguishes generated video from inferred actions. The latter are necessary if the target policy needs robot action supervision. [Official figure source](https://github.com/NVIDIA/GR00T-Dreams/blob/main/reference_architecture/reference_architecture.md)

## Worked example

1. For a pick-and-place task with existing demonstrations and editable scenes, adapt seed trajectories under object pose variation using the Mimic approach.
2. To explore a new environment from a starting image, try the DreamGen path with a supported robot embodiment. Filter the generated videos and inspect inferred actions before training.

## What to verify

- Review instruction following and physical plausibility separately. An image sequence can look coherent even when the inferred robot motion is infeasible.
- The DreamGen instructions target the model versions listed in that repository. Check the action schema and checkpoint compatibility before reusing output for another GR00T release.

## Official references and terms

The GR00T-Dreams repository provides the DreamGen implementation under Apache-2.0. Check the underlying model and dataset terms separately. The Mimic blueprint describes a combination of tools with component-specific terms.

- [NVIDIA GR00T-Mimic blueprint and worked example](https://developer.nvidia.com/blog/building-a-synthetic-motion-generation-pipeline-for-humanoid-robot-learning/)
- [GR00T-Dreams implementation and supported embodiments](https://github.com/NVIDIA/GR00T-Dreams)
- [DreamGen research and benchmark](https://research.nvidia.com/labs/gear/dreamgen/)

## Related guides

[MimicGen](mimicgen.md) · [Cosmos Predict2](cosmos-predict2.md) · [Isaac GR00T](isaac-gr00t.md)
