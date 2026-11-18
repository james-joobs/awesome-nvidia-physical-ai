# Choose and evaluate a robot foundation model

[← Model catalog](../../CATALOG.md#robot-foundation-models-and-vlas) · [한국어](../ko/robot-foundation-models.md)

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

### Can a different robot act on the same instruction?

A VLA typically takes camera observations, an instruction, and any robot state the checkpoint expects. An **action chunk** covers several future steps. An illustrative `[8, 7]` array contains seven values per step for eight steps. The configuration defines the order, units, normalization, and whether each command is an absolute target or a delta.

GR00T N1.6-DROID follows the DROID interface. The π family also uses checkpoints and observation adapters matched to the task. Two arrays with the same shape can command different motions under different conventions. Check the observation keys and shapes on one saved sample, then verify task success in simulation. [GR00T data configuration](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_config.md) · [Physical Intelligence openpi](https://github.com/Physical-Intelligence/openpi)

### Follow a GR00T N1.7 simulation workflow

The public, Apache-2.0 reference workflow records Isaac Lab demonstrations, converts them to LeRobot data, and fine-tunes a policy. G1 walks to an apple and puts it on a plate. H2 Plus passes the apple between hands before placing it. The G1 model and dataset require Hugging Face access. The H2 Plus artifacts are downloadable, and the workflow README reports that learned-policy evaluation for H2 Plus still awaits validation. [Official workflow](https://nvidia-isaac.github.io/GR00T-E2E-Reference-Workflow/) · [G1 model card](https://huggingface.co/nvidia/GR00T-E2E-Reference-Workflow-SIM-G1-N1.7-AppletoPlate-Model) · [H2 Plus model card](https://huggingface.co/nvidia/GR00T-E2E-Reference-Workflow-SIM-H2-N1.7-AppleHandoverPlate-Model)

## Cosmos Policy

The original [Cosmos Policy](https://github.com/NVlabs/cosmos-policy) post-trains Cosmos-Predict2 for visuomotor control. Its ALOHA planning path uses future observations and value estimates to compare candidate actions. The [LIBERO checkpoint](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B#license) uses the NVIDIA One-Way Noncommercial License. The source code has its own [Apache-2.0 license](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LICENSE).

[Cosmos 3 Edge Policy DROID](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) and [Nano Policy DROID](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID) are newer DROID action-policy checkpoints under OpenMDW-1.1. The [Cosmos 3 interactive simulation checkpoints](https://huggingface.co/blog/nvidia/cosmos-interactive-world-simulation) generate observations from actions or simulation controls. For example, Sim-Bimanual takes robot or camera actions and predicts video that a policy can consume as its next observation.

## Other VLAs

- **OpenVLA** provides a 7B manipulation baseline with inference and fine-tuning code. The model card lists MIT and the repository also identifies inherited Llama 2 terms. [Model card](https://huggingface.co/openvla/openvla-7b) · [Upstream terms](https://github.com/openvla/openvla#pretrained-vlas)
- **MolmoAct 2** includes base and embodiment-specific checkpoints and supports depth-aware manipulation. Use the checkpoint paired with your robot or evaluation environment. [Model card](https://huggingface.co/allenai/MolmoAct2)
- **X-VLA** conditions on embodiment-specific soft prompts. Verify the supported observations and action mode in the implementation you run. [Base model card](https://huggingface.co/2toINF/X-VLA-Pt) · [LeRobot integration](https://huggingface.co/docs/lerobot/xvla)

## World action models

A video-action model uses features learned from video to predict how a scene may change and to produce robot commands. In the published **FLUX-mimic** design, a task caption and recent camera frames condition the video backbone. The action expert reads intermediate video features and the robot state to predict a trajectory. The training objective covers video and actions. A single denoising step can provide the features for control without rendering a full video. [Industrial manipulation report and architecture](https://www.mimicrobotics.com/blog/video-action-models-for-data-efficient-industrial-manipulation)

| Name | What is available as of November 17, 2026 |
|---|---|
| **FLUX 3** | Black Forest Labs’ multimodal backbone for image, video, and audio. It underpins FLUX-mimic-x, FLUX-mimic, and FLUX 3 Action. [FLUX 3 × mimic announcement](https://bfl.ai/blog/flux-3-mimic) |
| **FLUX-mimic-x** | mimic robotics previewed a 7B model based on FLUX 3 and its updated mimic-video recipe on November 16 UTC. The team reports first place among real-time “System 1” models on RoboLab. The public leaderboard snapshot did not list the exact model under that name when checked. Public code, weights, and terms for this preview remain unverified. [mimic preview](https://x.com/mimicrobotics/status/2122343940653224018) · [NVIDIA RoboLab leaderboard](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html) |
| **FLUX-mimic** | Earlier industrial research model from mimic robotics and Black Forest Labs. The BMW Group study documents joint video-action training and reports on four tasks. Public code and weights for this FLUX-based model remain unverified. [Study](https://arxiv.org/abs/2611.15974) · [Project and demos](https://www.mimicrobotics.com/blog/video-action-models-for-data-efficient-industrial-manipulation) |
| **FLUX 3 Action** | Black Forest Labs’ separate 7B release. Its source is Apache-2.0. The SO-101 and DROID weights require Hugging Face access and follow the FLUX Kommunity License v1.0. BFL credits NVIDIA for Jetson integration and notes that Isaac Lab and RoboLab underpin much of its evaluation. [Release and technical report](https://bfl.ai/models/flux-3-action) · [Code](https://github.com/black-forest-labs/flux-action) · [SO-101](https://huggingface.co/black-forest-labs/flux-3-action-so101) · [DROID](https://huggingface.co/black-forest-labs/flux-3-action-droid) |
| **mimic-video** | Earlier research implementation with Apache-2.0 code built on NVIDIA Cosmos Predict2. The repository documents how to train an action decoder from intermediate features of a frozen video backbone. Check terms separately for each linked checkpoint. [Paper](https://arxiv.org/abs/2512.15692) · [Code](https://github.com/mimic-video/mimic-video) |

### NVIDIA policies and comparable releases

- **Cosmos3-Edge-Policy-DROID (4B)** and **Cosmos3-Nano-Policy-DROID (16B)** are NVIDIA checkpoints for DROID manipulation under OpenMDW-1.1. The official cookbook covers serving a policy and connecting the RoboLab client. [Edge](https://huggingface.co/nvidia/Cosmos3-Edge-Policy-DROID) · [Nano](https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID) · [Policy-serving cookbook](https://nvidia.github.io/cosmos-framework/action_policy_droid_server/)
- **GR00T 2 / Turbo** is NVIDIA’s Cosmos-based WAM family announced November 9. The research page still lists December 2026 for code availability. Downloadable weights and their terms remain unverified. [Research and demos](https://research.nvidia.com/labs/gear/gr00t-2/) · [GR00T guide](groot-model.md)
- **DreamZero-DROID** is NVIDIA GEAR’s video-and-action research baseline. Reference code uses Apache-2.0 and the downloadable 14B checkpoint is labeled CC BY-NC 4.0. [Project](https://dreamzero0.github.io/) · [Code](https://github.com/dreamzero0/dreamzero) · [Checkpoint and terms](https://huggingface.co/GEAR-Dreams/DreamZero-DROID)
- **Praxis-1** is Runway’s 27.3B WAM. It predicts video and actions jointly. Code and base, DROID, and YAM weights use Apache-2.0, with an access step for Hugging Face weights. Its November 11 release has a LeRobot integration and reports tested targets including RTX 5090 and Jetson Thor. [Release](https://runway.com/news/company-news/praxis-1-is-now-available) · [Checkpoint collection](https://huggingface.co/collections/runwayml/praxis-1)

### Read an evaluation like a rollout

**Camera frames + task text + robot state → policy → action chunk → simulator step → next observation.** For example, in a pick-and-place task, the policy receives camera observations and the current pose, then predicts a series of motions toward the object and the container. The evaluation counts where the object ends up after the simulator executes commands and returns observations. The policy’s predicted video is a separate output.

The November 17 RoboLab snapshot shows **555/1,200** successful episodes for Praxis-1, **515/1,200** for FLUX 3 Action, **441/1,200** for Cosmos3-Nano-Policy, and **275/1,200** for Cosmos3-Edge-Policy. Use the policy revision, instruction setting, episode budget, and hardware when comparing runs. These are published simulation results. [RoboLab-120 leaderboard](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html) · [Policy client interfaces](https://github.com/NVlabs/RoboLab/blob/main/policies/README.md) · [Try scoring a recorded GR00T trial](labs/gr00t-placement.md#first-exercise)

For new RoboLab evaluations, v0.3.3 adds seeded object poses and lighting presets. Record the benchmark version, seed, and lighting with the score so another run can use the same conditions. [v0.3.3 release notes](https://github.com/NVlabs/RoboLab/releases/tag/v0.3.3)

## Recent world action research

| Research | What it changes in the pipeline | What you can inspect or reuse |
|---|---|---|
| **ThinkWAM** (November 16) | Proposes a chunk of actions, uses it to update predicted future latents, and feeds those latents into a second pass that refines the actions before execution. | Public original code under MIT, with a bundled SIGReg component under CC BY-NC 4.0. The downloadable checkpoints use Apache-2.0 and have a dedicated evaluation profile. [Paper](https://arxiv.org/abs/2611.21258) · [Code and third-party terms](https://github.com/HaoyunT/Thinkwam#license) · [Checkpoint card](https://huggingface.co/Adrain11/ThinkWAM) |
| **VLALagBench** (November 16 revision) | Injects inference delays while moving-target tasks continue in simulation. It compares synchronous and asynchronous execution in LIBERO and includes an Isaac Sim cross-check. | Public benchmark code and results, with CC BY-NC 4.0 for original code, data, and docs. Model checkpoints and simulator assets have their own terms. [Paper](https://arxiv.org/abs/2611.03103v2) · [Repository and license](https://github.com/codestrongestx/vla-lag-bench#license) |
| **Ego2Sim2Humanoid** (November 14) | Converts egocentric RGB-D recordings into synchronized simulated robot views and executable whole-body trajectories. The paper reports fine-tuning GR00T N1.7 for Unitree G1 locomotion and manipulation with the converted data. | Paper and evaluation figures. Code, dataset, and tuned checkpoint availability unverified. [Paper](https://arxiv.org/abs/2611.19196) |
| **FOVI-Dex** (November 12) | NVIDIA and collaborators concentrate camera detail around the gaze target while keeping peripheral context. This makes large batches of rendered observations cheaper for dexterous grasping reinforcement learning. | NVIDIA publication and evaluation videos are public. Code, weights, and their terms remain unverified. [NVIDIA Research](https://research.nvidia.com/publication/2026-11_fovi-dex-foveation-enables-efficient-perceptive-learning-dexterous-manipulation) · [Project](https://fovi-dex.github.io/) |
| **SWAM** (November 11 revision) | Uses language–video supervision where only video is available and adds action supervision for human or robot demonstrations that contain usable actions. The two branches exchange features through attention. | Public Apache-2.0 code and a downloadable pretraining subset with source-specific terms. A downloadable policy checkpoint and its terms remain unverified. [Paper](https://arxiv.org/abs/2611.12870v2) · [Code](https://github.com/shaaaaron/SWAM) · [Dataset terms](https://huggingface.co/datasets/FreDERicia/SWAM-Pretrain#source-terms-and-attribution) |
| **WISE** (November 2) | Samples candidate video-action rollouts from a frozen WAM and scores action validity, consistency with imagined motion, and task progress. With four candidates, the paper reports a gain from 6% to 24% in its Cosmos 3 Edge RoboLab subset and about 3.4× episode runtime. | Preprint and evaluation protocol. Code availability unverified. [Paper](https://arxiv.org/abs/2611.03585) |
| **DemoStream** (CoRL 2026 workshop) | NVIDIA and collaborators use batched task-and-motion optimization to produce successful simulated demonstrations for policy learning. | Research page and paper. Code and demonstration dataset availability unverified. [NVIDIA Research](https://research.nvidia.com/publication/2026-11_demostream-batched-task-and-motion-plan-optimization-automated-learning) · [Paper](https://arxiv.org/abs/2610.22020) |
| **FlashRT-PAI** (October 2026) | Optimizes end-to-end inference with fused operations and runtime scheduling. The external project covers GR00T N1.7 and Cosmos3-Edge in addition to other policies. | Apache-2.0 code. Verify the supported model, GPU, precision, and runtime before comparing latency. [Paper](https://arxiv.org/abs/2610.24349) · [FlashRT repository](https://github.com/flashrt-project/FlashRT) |
| **ARC** (October 8) | An NVIDIA coauthored study adds action-grounded reasoning labels to DROID demonstrations and uses them to adapt π₀.₅ and Cosmos3-Nano-Policy. | The project lists code, model, dataset, and RoboLab-Reasoning-50 as forthcoming. [Project and status](https://arc-robot-reasoning.github.io/) · [Paper](https://arxiv.org/abs/2610.12386) |

[GR00T model family](groot-model.md) · [Physical Intelligence π](physical-intelligence-pi.md) · [LeRobot](lerobot.md) · [Isaac Lab](isaac-lab.md) · [Alpamayo driving VLA](alpamayo.md)
