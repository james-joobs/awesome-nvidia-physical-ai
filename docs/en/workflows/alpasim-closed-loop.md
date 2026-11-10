# Run a closed-loop driving evaluation with AlpaSim

**English** · [한국어](../../ko/workflows/alpasim-closed-loop.md) · [Catalog](../../../README.md#start-with-what-you-want-to-build)

Run the official AlpaSim baseline on one reconstructed driving scene and inspect the resulting episode. In closed loop, the policy's trajectory affects the simulated ego vehicle, and the next observation is rendered from the updated state. A recorded-video replay keeps the recorded viewpoint. Start with the existing NuRec USDZ so you can check the simulator before attempting your own reconstruction. [AlpaSim architecture](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/DESIGN.md)

## What you need

| Item | Start with |
| --- | --- |
| Host | A Linux host with an NVIDIA GPU. Follow the pinned onboarding guide for CUDA 12.8, the NVIDIA driver and Container Toolkit, Docker Compose/Buildx, Rust, and `uv` 0.9.17 or newer. Check that the container can see the GPU. |
| AlpaSim | Source revision `affc2ea`, local Docker Compose, `topology=1gpu`, the tutorial's VaVAM baseline driver, and the default NuRec renderer. |
| Scene access | Request access to NVIDIA's gated NuRec dataset on Hugging Face, and set a read token as `HF_TOKEN` in the shell. Keep it out of saved commands and run artifacts you share. |
| Scene | Start with the tutorial's `clipgt-02eadd92-02f1-46d8-86fe-a9e338fed0b6` scene. The pinned scene catalog maps it to the 26.01 sample release. |

[Official onboarding](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/ONBOARDING.md) · [NuRec dataset and access terms](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec) · [Scene catalog](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/data/scenes/README.md)

## 1. Run one official scene

Once the host is ready and `HF_TOKEN` is set, use a fresh checkout of the official tutorial revision. The setup script may prompt for tooling. The download step fetches the VaVAM assets, and the wizard fetches the scene when needed.

```bash
git clone https://github.com/NVlabs/alpasim.git
cd alpasim
git checkout affc2eab209fa43bdfa2f26c0f8d437922d78a68
source setup_local_env.sh
bash data/download_vavam_assets.sh --model vavam-b
uv run alpasim_wizard deploy=local topology=1gpu driver=vavam \
  'scenes.scene_ids=[clipgt-02eadd92-02f1-46d8-86fe-a9e338fed0b6]' \
  "wizard.log_dir=$PWD/run-baseline"
```

The first run can include image and model downloads. A `GatedRepoError` means scene access or token permissions need attention. When reusing an existing installation, check the scene-catalog note about stale 26.01 and 26.04 caches. [Official Docker tutorial](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/TUTORIAL.md) · [Scene cache notes](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/data/scenes/README.md)

## 2. Confirm the result and set a baseline

| Check | Where to look |
| --- | --- |
| Did the rollout finish? | Find the `_complete` marker and `metrics.parquet` under the corresponding `run-baseline/rollouts/` episode. Use the service logs to diagnose incomplete rollouts. |
| What did the car see and do? | When evaluation video is enabled, open the clip in `run-baseline/eval/videos/` or the aggregate video directory. Match any event to the same episode in the rollout logs. |
| What should I compare? | Open `run-baseline/aggregate/metrics_results.txt`. Start with at-fault collision and off-road events. One successful run confirms the setup and provides a baseline, with broader conclusions requiring more scenarios. |

For a comparison, use a new output directory and keep the scene artifact UUID, renderer and camera configuration, vehicle/traffic settings, and evaluation settings fixed. Save the resolved wizard configuration, then change only the driver, using policies compatible with the same camera setup. A scene ID can refer to multiple artifacts, so record the selected artifact UUID and Hugging Face revision with the results. [AlpaSim result layout](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/TUTORIAL.md#results-structure) · [Official metrics guide](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/OPERATIONS.md#understanding-driving-quality-metrics)

## 3. Extend to your own driving logs

1. Prepare a short segment with synchronized camera frames, camera calibration, and ego poses. Convert the segment to NCore and check it against the official NuRec input requirements. Map and tracked-actor data depend on the scene and the features you plan to use.
2. Package the reconstruction as a compatible USDZ and check it with the NuRec renderer. Start by re-rendering the original camera viewpoints. Check lane edges, actor timing, and gaps from occlusions before comparing novel views.
3. Prepare the scenario and its route, maps, and simulation metadata for AlpaSim. Check the packaged contents against the official scene schema and renderer version, then run the same evaluation on this scene. Use the original sample run to isolate pipeline problems.

[Prepare data with NCore](https://docs.nvidia.com/nurec/basics/get-data.html) · [Reconstruct an AV scene](https://docs.nvidia.com/nurec/nurec/reconstruct-av-scene.html) · [NuRec scaling and scene layers](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html) · [Dataset scene format](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec#dataset-format)

## Related tools and verification

- **Post-training** · [AlpaGym](../alpagym.md) adds reinforcement learning on supported AlpaSim workflows. [Alpamayo Recipes](https://github.com/NVlabs/alpamayo-recipes) covers model post-training and deployment.
- **Alternative renderer** · [OmniDreams via FlashDreams](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/VIDEO_MODEL.md) is a separate renderer setup with its own scene, camera, checkpoint, and GPU requirements.
- **Licenses** · AlpaSim code is Apache-2.0. VaVAM assets, the gated NuRec data and artifacts, and container components have separate terms. [AlpaSim license](https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/LICENSE) · [NuRec dataset card](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec)
- **Verification status** · The pinned tutorial, scene entry, and output paths were checked against official sources. The GPU rollout and private-log extension have yet to be run for this guide.
