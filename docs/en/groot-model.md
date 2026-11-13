# Isaac GR00T model family

[← Back to catalog](../../README.md) · [한국어](../ko/groot-model.md)

| Version | Model type and role | Availability as of November 13, 2026 |
|---|---|---|
| **GR00T 2 / GR00T 2 Turbo** | Cosmos-based world-action models (WAMs). They jointly predict future video and an action sequence from observations, an instruction and robot state. Turbo is designed for on-robot whole-body control. | Announced at CoRL on November 9. NVIDIA Research lists code availability in December 2026. Public weights and their terms were unverified on November 13. [Research and demos](https://research.nvidia.com/labs/gear/gr00t-2/) · [CoRL announcement](https://blogs.nvidia.com/blog/robotics-simulation-advancements-corl/) |
| **GR00T N1.7-3B** | Cross-embodiment vision-language-action (VLA) model for robot manipulation. | Generally available since [July 7, 2026](https://github.com/NVIDIA/Isaac-GR00T/commit/1a1837f20538b7d7e21f977a11a5aee14f99803c). Apache-2.0 reference code and NVIDIA Open Model License for the weights. [Code](https://github.com/NVIDIA/Isaac-GR00T) · [Base checkpoint](https://huggingface.co/nvidia/GR00T-N1.7-3B) · [Weight license](https://huggingface.co/nvidia/GR00T-N1.7-3B/blob/main/LICENSE) |

## N1.7 architecture and data flow

N1.7’s vision-language backbone embeds the scene and instruction, and its action head predicts a continuous sequence conditioned on robot state and embodiment.

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

On November 11, NVIDIA confirmed that it had replaced older noncommercial license files for N1.7-3B and its official Bridge, Fractal, DROID and LIBERO checkpoints. The corrected NVIDIA Open Model License permits commercial use subject to its terms. [NVIDIA clarification](https://forums.developer.nvidia.com/t/gr00t-n1-7-license-clarification-model-card-says-commercial-use-but-license-file-in-hf-repo-says-non-commercial/387959/3)

- [N1.7 code license](https://github.com/NVIDIA/Isaac-GR00T/blob/main/LICENSE)
- [N1.7 benchmark checkpoints and embodiment tags](https://github.com/NVIDIA/Isaac-GR00T#model-checkpoints--embodiment-tags)

## Related guides

[Isaac GR00T code](isaac-gr00t.md) · [GR00T-H](gr00t-h.md)
