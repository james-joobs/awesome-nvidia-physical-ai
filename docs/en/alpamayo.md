# Alpamayo

[← Catalog](../../README.md) · [한국어](../ko/alpamayo.md)

Alpamayo is a family of reasoning and action models for autonomous driving. The R1 research architecture is a useful concrete example. Check the model card before carrying that architecture or input contract over to another release.

![Alpamayo-R1 model architecture](https://arxiv.org/html/2511.00088v2/main_arch_1.png)

*Follow the multiview and ego-motion inputs into the VLM backbone, then distinguish the reasoning tokens from the trajectory decoder’s waypoints.* [Official figure source](https://arxiv.org/html/2511.00088v2#S3)

![Alpamayo-R1 chain of causation labeling pipeline](https://arxiv.org/html/2511.00088v2/labeling_overview_new_2.png)

*This training-data diagram shows how driving clips become labeled examples linked to specific decisions. It is separate from inference.* [Official figure source](https://arxiv.org/html/2511.00088v2#S3)

## How do camera views and ego motion become a driving trajectory?

### Read the anchor time from a real validation manifest

These two fields come from the first entry in NVIDIA’s **Alpamayo 2 Super** public validation manifest.

```json
{
  "clip_id": "003e17f1-7c44-4d82-9f32-d4cd82f6a8e8",
  "t0_us": 2000000
}
```

The ID identifies a PhysicalAI-AV clip. The anchor `t0_us` is **2 seconds** from the start of that clip. The loader aligns images and ego position and rotation to that time. The trajectory profile uses six cameras and four frames per camera. At 10 Hz, the requested image times here are 1.7, 1.8, 1.9, and 2.0 seconds. The loader also retains the timestamps returned by decoding. [Pinned validation manifest](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/examples/public_golden_validation_samples.json) · [Data loader](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/src/alpamayo2_super/load_physical_aiavdataset.py)

### Read input arrays and predicted outputs

| Data | Official trajectory example | Meaning |
|---|---|---|
| `image_frames` | `[6, 4, 3, H, W]` | Selected cameras, frames, RGB channels, height, and width. |
| `ego_history_xyz` | `[1, 1, 16, 3]` | Sixteen ego-frame XYZ positions up to the anchor. Rotation is a separate array. |
| One predicted trajectory | Positions `[64, 3]` and rotations `[64, 3, 3]` | Waypoints from 0.1 to 6.4 seconds after the anchor. |

The vision-language backbone encodes the observations and the action expert samples a conditioned future trajectory. The official example reports reasoning text and a trajectory. For `minADE`, it computes mean XY error against the recorded future for each candidate, then takes the smallest mean. Follow the [AlpaSim lab](workflows/alpasim-closed-loop.md) to inspect collisions or off-road events in closed loop. The numbers above come from NVIDIA’s manifest and documented data contract. [2 Super model card](https://huggingface.co/nvidia/Alpamayo2-Super) · [Official inference script](https://github.com/NVlabs/alpamayo2/blob/59776920bbd981f2c989213bba5ee8594e71ed1d/src/alpamayo2_super/inference_smoke.py)

## Released checkpoints

| Model | What it adds | Model and inference code |
|---|---|---|
| **Alpamayo 2 Edge** · Nov 10, 2026 | Compact adaptive reasoning VLA for DRIVE AGX Thor. The Cosmos 3 Edge backbone takes surround-camera observations, ego-motion history, and navigation text. The model generates future trajectories and uses reasoning when needed. The card lists a 2.45B backbone and a 0.2B action expert. | [Model card](https://huggingface.co/nvidia/Alpamayo2-Edge) · [GitHub](https://github.com/NVlabs/alpamayo2-edge) |
| **Alpamayo 2 Super** · Aug 4, 2026 | 34B-class driving foundation model with a 32B Cosmos 3 Super Reasoner backbone and a diffusion action expert. Supports trajectory prediction, causal reasoning, visual question answering, 2D grounding, and auto-labeling. | [Model card](https://huggingface.co/nvidia/Alpamayo2-Super) · [GitHub](https://github.com/NVlabs/alpamayo2) |
| **Alpamayo 1.5** · Mar 19, 2026 | 10B-class VLA based on Cosmos-Reason2 with navigation guidance, flexible camera counts, and visual question answering. | [Model card](https://huggingface.co/nvidia/Alpamayo-1.5-10B) · [GitHub](https://github.com/NVlabs/alpamayo1.5) |
| **Alpamayo 1 (R1)** | Original 10B-class model pairing Chain-of-Causation reasoning with trajectories. The figures above show this version. | [Model card](https://huggingface.co/nvidia/Alpamayo-R1-10B) · [GitHub](https://github.com/NVlabs/alpamayo) |

## How it works

R1 conditions its reasoning and trajectory predictions on observations such as camera frames and ego-motion history. A vision-language backbone produces driving reasoning and a trajectory generation component produces continuous waypoints. A simulator driver can consume the resulting trajectory to advance the ego vehicle. Reasoning text and motion are separate outputs to inspect.

## A practical workflow

Run an Alpamayo driver in AlpaSim on a scenario with a partly occluded obstacle or a complex merge. The upstream AlpaSim changelog documents `driver=alpamayo2` for **2 Super**. Edge has its own inference repository, and NVIDIA documents its closed-loop reinforcement-learning post-training in AlpaGym. Review reasoning, trajectory, and rollout metrics against a baseline on the same scene and route. [AlpaSim changelog](https://github.com/NVlabs/alpasim/blob/main/CHANGELOG.md) · [Edge technical overview](https://developer.nvidia.com/blog/running-av-reasoning-models-within-onboard-compute-and-latency-limits/)

## What to verify

Check the checkpoint’s accepted cameras, context and coordinate frames, required memory and gated access. Evaluate trajectory quality and behavior independently of whether the explanation sounds plausible.

## License and availability

Edge and Super weights are publicly downloadable on Hugging Face under OpenMDW-1.1. Their inference repositories use Apache-2.0. The Alpamayo 1 and 1.5 cards also link OpenMDW-1.1 and describe non-commercial use with commercial licensing on request. Check the intended-use wording and license of the exact checkpoint and any datasets it requires. [Edge weight license](https://huggingface.co/nvidia/Alpamayo2-Edge/blob/main/LICENSE) · [Super weight license](https://huggingface.co/nvidia/Alpamayo2-Super/blob/main/LICENSE) · [Edge code license](https://github.com/NVlabs/alpamayo2-edge/blob/main/LICENSE) · [Super code license](https://github.com/NVlabs/alpamayo2/blob/main/LICENSE)

## Official references

- [Architecture and workflow documentation](https://research.nvidia.com/labs/avg/publication/2025/12/alpamayo-r1/)
- [R1 model card](https://huggingface.co/nvidia/Alpamayo-R1-10B)
- [AlpaSim driver tutorial](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md)
- [Alpamayo recipes for tuning and deployment](https://github.com/NVlabs/alpamayo-recipes)
- [AlpaJudge model card](https://huggingface.co/nvidia/alpajudge) and [source](https://github.com/NVlabs/alpajudge) for evaluating driving reasoning and supplying training rewards
