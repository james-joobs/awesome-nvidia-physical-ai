# Isaac GR00T / GR00T N1.7

[← Back to catalog](../../README.md) · [한국어](../ko/groot-model.md)

GR00T N1.7 is a vision-language-action (VLA) checkpoint for robot manipulation. Its visual-language backbone embeds the scene and instruction, while its action head predicts a continuous sequence conditioned on the robot’s current state and embodiment. The trained model and its surrounding deployment software have separate release and license information.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Vision and language** | Robot camera frames and a text instruction condition a Cosmos Reason2-based visual-language backbone. See the N1.7 repository for the backbone change from N1.6. |
| **Proprioception and embodiment** | An embodiment-indexed MLP encodes robot state. Padding and named modality fields let the architecture handle different state dimensions while preserving per-robot semantics. |
| **Flow-matching action head** | A diffusion transformer estimates the flow that turns a noisy action sequence into an action chunk. Embodiment-specific projections encode and decode control vectors. |
| **Controller boundary** | Relative end-effector targets express motion with respect to the configured current pose. The execution stack converts the selected actions into commands compatible with the robot’s controller. |

![The architecture diagram separates visual-language conditioning from action generation. Read the state and embodiment inputs alongside the action path to see where the robot’s control semantics enter the model.](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

The architecture diagram separates visual-language conditioning from action generation. Read the state and embodiment inputs alongside the action path to see where the robot’s control semantics enter the model. [Official figure source](https://huggingface.co/nvidia/GR00T-N1.7-3B)

## Worked example

1. Start with a released model and a supported DROID observation sample. Provide the declared camera keys, state fields, instruction and embodiment tag.
2. Inspect the resulting action chunk in the expected coordinate and normalization conventions. Run a closed-loop rollout with a compatible controller before assessing success on the target task.

## What to verify

- The number and order of action dimensions depend on the embodiment configuration. Check the controller and modality definitions before interpreting values as motor commands.
- Evaluate new tasks and environments separately from those covered by published checkpoints. Track latency and task success as well as numerical action error.

## Official references and terms

N1.7 model weights use the NVIDIA Open Model License. The Isaac GR00T repository separately licenses its code under Apache-2.0.

- [N1.7 model card, architecture and terms](https://huggingface.co/nvidia/GR00T-N1.7-3B)
- [N1.7 software and relative action interface](https://github.com/NVIDIA/Isaac-GR00T)

## Related guides

[Isaac GR00T code](isaac-gr00t.md) · [GR00T-H](gr00t-h.md)
