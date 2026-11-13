# Isaac GR00T code

[← Back to catalog](../../README.md) · [한국어](../ko/isaac-gr00t.md)

<p align="center">
  <img src="../../assets/project-marks/isaac-groot.png" width="290" alt="NVIDIA Isaac GR00T wordmark"><br>
  <sub><a href="https://github.com/NVIDIA/Isaac-GR00T/blob/7aa0bca50f1097f8b17f5c274c98264b72a1419f/media/header_compress.png">Official Isaac GR00T repository wordmark</a></sub>
</p>

The Isaac GR00T repository contains the software for adapting, evaluating and serving a robot policy. The N1.7 checkpoint is one input to this workflow. The repository also defines the dataset schema, embodiment-specific preprocessing and interfaces for evaluating or deploying a trained policy.

N1.7 reached general availability on July 7, 2026. NVIDIA announced GR00T 2 and GR00T 2 Turbo at CoRL in November 2026. Its research page lists December 2026 for the GR00T 2 code. [N1.7 GA](https://github.com/NVIDIA/Isaac-GR00T/commit/1a1837f20538b7d7e21f977a11a5aee14f99803c) · [GR00T 2 research](https://research.nvidia.com/labs/gear/gr00t-2/)

## N1.7 architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Dataset and modality mapping** | The N1.7 code reads a LeRobot v2 variant. Images are stored in video files and numerical states and actions in Parquet. The additional `meta/modality.json` maps the stored vectors and video keys to named policy inputs and outputs. |
| **Embodiment and fine-tuning** | The embodiment tag selects the modality configuration and normalization. For a new robot, the data and modality configuration must agree on cameras, state fields and how relative end-effector actions are represented. |
| **Policy interface** | The policy consumes an observation batch and returns an action chunk. It can run in-process or behind a policy server; the client integrates sensors, execution and subsequent observations. |

![The official N1.7 architecture identifies the tensors that the repository’s data and policy interfaces must supply to the model and decode for execution.](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

The official N1.7 architecture identifies the tensors that the repository’s data and policy interfaces must supply to the model and decode for execution. [Official figure source](https://github.com/NVIDIA/Isaac-GR00T)

![The official Unitree G1 demo illustrates a hardware rollout. The repository documents different whole-body interfaces for the G1 and G1 SONIC configurations.](https://media.githubusercontent.com/media/NVIDIA/Isaac-GR00T/main/media/unitree_g1.gif)

The official Unitree G1 demo illustrates a hardware rollout. The repository documents different whole-body interfaces for the G1 and G1 SONIC configurations. [Official figure source](https://github.com/NVIDIA/Isaac-GR00T)

## Worked example

1. Use the bundled SO100 cube-to-bowl sample to inspect a working dataset and its modality mapping. If your own recordings use LeRobot v3, follow the documented v3-to-v2 conversion workflow.
2. Fine-tune using the intended embodiment configuration. Run open-loop comparisons against held-out actions to catch misaligned cameras, vector fields or action scaling.
3. Run closed-loop evaluation in a supported simulator or hardware setup and record task success, reset behavior and failures.

## What to verify

- Check whether actions are relative or absolute and which frame defines the delta. Open-loop action agreement is useful for interface debugging; closed-loop task success measures behavior after errors accumulate.
- Choose a compatible checkpoint and embodiment tag together. Validate the deployed inference backend against the training configuration before connecting a controller.

## Official references and terms

The code uses Apache-2.0. The repository lists the NVIDIA Open Model License for its N1.7 model weights.

- [Repository and supported evaluation examples](https://github.com/NVIDIA/Isaac-GR00T)
- [Code license](https://github.com/NVIDIA/Isaac-GR00T/blob/main/LICENSE)
- [N1.7-3B checkpoint](https://huggingface.co/nvidia/GR00T-N1.7-3B) · [Weight license](https://huggingface.co/nvidia/GR00T-N1.7-3B/blob/main/LICENSE)
- [Dataset preparation](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_preparation.md)
- [Policy API and embodiment tags](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/policy.md)

## Related guides

[N1.7 model architecture](groot-model.md) · [LeRobot dataset format](lerobot.md) · [Isaac ROS Deploy](isaac-ros-deploy.md)
