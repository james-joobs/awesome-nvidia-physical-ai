# GR00T-H code

[← Back to catalog](../../README.md) · [한국어](../ko/gr00t-h.md)

GR00T-H adapts the GR00T VLA stack for medical robotics research. The repository documents GR00T-H-N1.7 and the earlier N1.6-derived GR00T-H checkpoint, with different model terms. The N1.7 medical model is post-trained on a surgical subset of Open-H rather than every modality and robot in the full dataset.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Inputs and embodiment** | The policy receives RGB observations, a task instruction and robot state. Model inputs depend on the configured embodiment; the N1.7 model card describes the camera and relative end-effector conventions used for post-training. |
| **Shared VLA architecture** | Cosmos Reason2 encodes images and text. Embodiment-aware projections handle state and actions, and a flow-matching transformer produces a continuous action chunk. |
| **Open-H post-training** | Open-H stores synchronized recordings and kinematics across robot platforms. For GR00T-H-N1.7, the released model card describes a 601-hour surgical subset and standardized relative end-effector actions. |

![The repository reproduces the upstream N1.7 diagram. It explains the inherited model structure; the medical specialization comes from the Open-H post-training described in the model card.](https://raw.githubusercontent.com/NVIDIA-Medtech/GR00T-H/main/media/model-architecture.png)

The repository reproduces the upstream N1.7 diagram. It explains the inherited model structure; the medical specialization comes from the Open-H post-training described in the model card. [Official figure source](https://github.com/NVIDIA-Medtech/GR00T-H)

![The Open-H montage shows the variety of robots and viewpoints in the source dataset. Use the embodiment reference to identify the fields expected by a particular checkpoint.](https://raw.githubusercontent.com/NVIDIA-Medtech/GR00T-H/main/media/open-h-collage.jpg)

The Open-H montage shows the variety of robots and viewpoints in the source dataset. Use the embodiment reference to identify the fields expected by a particular checkpoint. [Official figure source](https://github.com/NVIDIA-Medtech/GR00T-H)

## Worked example

1. Use the official CMR Versius example with recorded trajectories and the matching embodiment tag. Run standalone inference and compare the predicted action sequence against held-out kinematics.
2. When fine-tuning for a different supported research task, verify instrument frames, view availability and annotation coverage before comparing checkpoints.

## What to verify

- Use the model card to distinguish corpus coverage from training coverage. Follow the intended-use and out-of-scope limitations for medical robotics research.
- Code is Apache-2.0. The N1.7 model card points to the NVIDIA Open Model License, while the original GR00T-H weights use the NVIDIA OneWay Noncommercial License.

## Official references and terms

The code uses Apache-2.0. The two model variants and the Open-H dataset carry separate terms.

- [GR00T-H code, examples and version terms](https://github.com/NVIDIA-Medtech/GR00T-H)
- [GR00T-H-N1.7 model card](https://huggingface.co/nvidia/GR00T-H-N1.7)
- [Open-H dataset card](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment)

## Related guides

[GR00T N1.7](groot-model.md) · [LeRobot](lerobot.md)
