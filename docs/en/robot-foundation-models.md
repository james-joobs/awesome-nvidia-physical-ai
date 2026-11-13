# Choose and evaluate a robot foundation model

[← Model catalog](../../README.md#robot-foundation-models-and-vlas) · [한국어](../ko/robot-foundation-models.md)

Start with the robot and task you can evaluate. A checkpoint for a specific camera setup, gripper, or benchmark gives you a reproducible baseline before you collect data or fine-tune a generalist model.

| What you have | Start with | First result to verify |
|---|---|---|
| SO-100 or SO-101 demonstrations | [SmolVLA in LeRobot](https://huggingface.co/docs/lerobot/smolvla) or [MolmoAct 2](https://huggingface.co/allenai/MolmoAct2) with the matching embodiment | An action chunk with the expected joint order and gripper convention |
| A LIBERO simulation benchmark | [π₀.₅-LIBERO](physical-intelligence-pi.md) or [Cosmos Policy LIBERO](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B) | A rollout on the benchmark task used by that checkpoint |
| A DROID observation sample | [GR00T N1.7](groot-model.md), [π₀.₅-DROID](physical-intelligence-pi.md), or [Cosmos 3 Edge Policy DROID](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) | A correctly decoded trajectory for the sample's observation schema |
| An Isaac Lab manipulation task | [Isaac Lab-Arena](isaac-lab-arena.md) with a supported policy interface | Success rate across fixed scene variants and repeatable resets |

## From observations to evaluated actions

1. **Match the inputs.** Check camera names and order, image preprocessing, task text, robot state fields, and normalization against the checkpoint and its example.
2. **Decode actions before closing the loop.** Check units, coordinate frame, absolute or relative targets, joint order, and gripper convention. Record how many actions a prediction returns and how many the controller executes before requesting the next observation.
3. **Run the official example and keep a baseline.** Record checkpoint revision, embodiment, action rate, inference latency, success criteria, and reset conditions. Then vary one task condition, such as object pose or lighting, while keeping the evaluation procedure fixed.
4. **Compare access and terms.** Read the license for the code and the exact model card for the checkpoint, along with its backbone and data terms when applicable. A public research page, a hosted API, and downloadable weights offer different ways to reproduce a result.

## Cosmos Policy

The original [Cosmos Policy](https://github.com/NVlabs/cosmos-policy) post-trains Cosmos-Predict2 for visuomotor control. Its ALOHA planning path uses future observations and value estimates to compare candidate actions. The [LIBERO checkpoint](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B#license) uses the NVIDIA One-Way Noncommercial License. The source code has its own [Apache-2.0 license](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LICENSE).

[Cosmos 3 Edge Policy DROID](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) and [Nano Policy DROID](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID) are newer DROID action-policy checkpoints under OpenMDW-1.1. The [Cosmos 3 interactive simulation checkpoints](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation) generate observations from actions or simulation controls. For example, Sim-Bimanual takes robot or camera actions and predicts video that a policy can consume as its next observation.

## Other VLAs

- **OpenVLA** provides a 7B manipulation baseline with inference and fine-tuning code. The model card lists MIT and the repository also identifies inherited Llama 2 terms. [Model card](https://huggingface.co/openvla/openvla-7b) · [Upstream terms](https://github.com/openvla/openvla#pretrained-vlas)
- **MolmoAct 2** includes base and embodiment-specific checkpoints and supports depth-aware manipulation. Use the checkpoint paired with your robot or evaluation environment. [Model card](https://huggingface.co/allenai/MolmoAct2)
- **X-VLA** conditions on embodiment-specific soft prompts. Verify the supported observations and action mode in the implementation you run. [Base model card](https://huggingface.co/2toINF/X-VLA-Pt) · [LeRobot integration](https://huggingface.co/docs/lerobot/xvla)
## World action models

- **Praxis-1** predicts future video jointly with robot actions. Its base and DROID/YAM checkpoints use Apache-2.0 and require Hugging Face access. [Release announcement](https://runway.com/news/company-news/praxis-1-is-now-available) · [Base checkpoint](https://huggingface.co/runwayml/praxis-1-base)

- **FLUX 3 Action** offers checkpoint variants for DROID and SO-101. The source code uses Apache-2.0, and the weights use the FLUX Kommunity License. [Project](https://bfl.ai/models/flux-3-action) · [SO-101 weight license](https://huggingface.co/black-forest-labs/flux-3-action-so101/blob/main/LICENSE.md)

[GR00T model family](groot-model.md) · [Physical Intelligence π](physical-intelligence-pi.md) · [LeRobot](lerobot.md) · [Isaac Lab](isaac-lab.md) · [Alpamayo driving VLA](alpamayo.md)
