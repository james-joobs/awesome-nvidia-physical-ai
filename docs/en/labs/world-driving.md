# Try Cosmos video generation and an Alpamayo driving-model interface

Create a short video from an Isaac Sim image, then run a separate driving model on six camera views from a self-authored intersection. You can inspect the saved model products without a GPU. These are two independent experiments: the Cosmos video is not fed into Alpamayo.

## How it works

### An image is a condition, not a simulated physical state

Cosmos3-Edge receives one RGB image and a description of what should happen. It denoises a latent video and decodes RGB frames. Our input contains a yellow cube, a green cube and a dark block on a workbench.

```text
Isaac Sim camera → one RGB image + motion prompt → Cosmos3-Edge → generated RGB video
                   same image and seed, change only "left" / "right"
```

The requested output has **49 frames at 24 FPS**, about 2.04 seconds. The model does not return a USD scene, contact forces or verified collision events. A decoded video confirms that inference finished; visual review determines whether the requested motion happened. [Official inference contract](https://nvidia.github.io/cosmos-framework/inference/)

### Give the world model explicit camera actions

The action-conditioned example adds a `float32 [60, 9]` sequence to the same image. Each row carries **three native normalized translation channels and a 6D rotation representation**. These values are already prepared for the model; they are not raw displacements in meters and must not be normalized again. We preserve NVIDIA's published camera example unchanged, verify its SHA-256 (`547b977c…83c5595`), and let Framework pad the nine channels to its model action width. [Pinned official camera example](https://github.com/NVIDIA/cosmos-framework/blob/afd7d4c4087a8929c84523ff60172642fd11690b/inputs/omni/action_forward_dynamics_camera.json)

```text
Our RGB image + NVIDIA's 60×9 camera-action sequence → forward_dynamics → 61 RGB frames
                                                                        30 FPS
```

The first frame is the observation; the following 60 are predicted views. The recorded output is **832×464**, after the model's padding/cropping, at the requested `480` resolution tier. It changes the camera view visibly. It still provides generated RGB, not a reconstructed 3D scene or a physics-based guarantee that the requested camera path is exact.

### Camera history becomes a proposed trajectory

Alpamayo2-Edge combines camera observations, recent ego motion and navigation text. Its vision-language backbone generates driving reasoning, and its action expert predicts motion. The upstream decoder integrates its predicted acceleration and curvature into future poses. Our intersection uses original primitive geometry and no gated driving recordings. [Official model card](https://huggingface.co/nvidia/Alpamayo2-Edge)

```text
6 cameras / 22 RGB frames ─┐
20 historical ego poses ───┼→ Alpamayo2-Edge → reasoning text + 64 future poses
"Continue straight..." ───┘                  → inspect the saved tensors
```

| Data in this lab | Shape and meaning |
|---|---|
| Camera images | CPU `uint8 [22, 1, 3, 360, 640]`; 22 frames, one frame per entry, RGB, height, width. |
| Camera IDs and timestamps | `int64 [22]`; IDs `0/1/2/3/5/6` have `3/5/3/3/3/5` frames. The two front cameras cover −2, −1, −0.5, −0.1 and 0 seconds; other views cover −1, −0.1 and 0 seconds. |
| Position history | `float32 [1, 20, 3]`; ego-frame XYZ at 0.1-second steps, accompanied by `[1, 20, 3, 3]` rotation matrices. Our synthetic camera rig moves at 5 m/s. |
| Predicted positions | `[1, 1, 1, 64, 3]`; one batch, one trajectory set, one candidate, 64 XYZ poses from 0.1 to 6.4 seconds. Rotation output is `[1, 1, 1, 64, 3, 3]`. |

For example, a predicted position `[5.0, 0.4, 0.0]` means 5 m forward and 0.4 m left of the reference ego pose. This example explains the coordinate convention; it is not a measured prediction. Our rendered road is a **synthetic interface test**, outside the model's real driving-data evaluation. It checks actual weight loading and valid outputs. It does not test a car in closed loop.

## Run

### 1. Prepare a dedicated model folder on a Linux GPU machine

Open a terminal in this repository on the GPU machine. Check [GPU and driver setup](../onboarding/nvidia-linux.md), then choose an empty folder outside the repository for model weights and virtual environments. The recorded machine has an RTX 5090 with 32 GiB. The commands pin the source and model revisions in [model-pins.json](../../../labs/world-driving/model-pins.json).

```bash
export WORLD_DRIVING_ROOT="$HOME/physical-ai-experiments/world-driving"
bash labs/world-driving/setup.sh
```

Setup creates separate Cosmos and Alpamayo environments. Cosmos uses the locked CUDA 13.0 inference dependencies; Alpamayo uses its Python 3.12 lockfile. The public weights total about 13.5 GiB; the recorded environments add about 16 GiB, with caches and a separately downloaded VAE requiring more space. Allow at least 60 GiB for this subset. Read the exact checkpoint terms before using the weights. [Cosmos setup](https://nvidia.github.io/cosmos-framework/setup/) · [Alpamayo setup](https://github.com/NVlabs/alpamayo2-edge#setup)

### 2. Generate two videos from one image

Run each line in the same terminal. Both runs use seed 19 and the same bundled, self-authored simulator image. Only the requested slide direction changes. Each script waits for the session's shared GPU lock, so it can run alongside other queued labs without competing for GPU memory.

```bash
bash labs/world-driving/run_cosmos.sh right
bash labs/world-driving/run_cosmos.sh left
```

Open `outputs/cosmos-right/workbench-right/vision.mp4` under `WORLD_DRIVING_ROOT`. Keep both clips, even if one does not follow its prompt. The script turns off the optional guardrail models for this controlled synthetic input; deployed applications need their own guardrail configuration.

To add the explicit camera actions, run this third command. It downloads only the pinned 12 KB action sidecar, checks its digest and shape, then calls the same released Edge checkpoint.

```bash
bash labs/world-driving/run_camera_action.sh
```

### 3. Render your own driving-model inputs in Isaac Sim

Set `ISAAC_LAB_PYTHON` to a Python executable with Isaac Lab and Isaac Sim installed. The recorded input-rendering environment uses **Isaac Sim 6.1.0.0 / Isaac Lab 17.0.2** and `AppLauncher --viz kit`. It is separate from the site's Isaac Sim 6.2 workbench guide. Follow the simulator's license prompt on first use.

```bash
export ISAAC_LAB_PYTHON="/path/to/IsaacLab/.venv/bin/python"
flock /tmp/physical-ai-four-domains.gpu.lock \
  "$ISAAC_LAB_PYTHON" labs/world-driving/make_driving_scene.py \
  --viz kit --output "$WORLD_DRIVING_ROOT/inputs/synthetic-intersection"
```

The GUI opens the road scene and renders 22 images from the camera positions and times in the table. The folder also receives `input.json` and `synthetic-intersection.usda`. To record the actual simulator window on Linux X11, add `--record-window /absolute/path/to/ffmpeg`. Use a terminal in your graphical desktop session so `DISPLAY` and `XAUTHORITY` refer to that session.

### 4. Run the released driving-model weights

This reads your generated camera images and history, loads the pinned BF16 checkpoint and writes both reasoning and trajectories. It uses the default PyTorch SDPA attention backend, without accelerated-inference compilation.

```bash
python3 labs/cli.py --json run alpamayo-synthetic \
  --python "$WORLD_DRIVING_ROOT/alpamayo2-edge/.venv/bin/python" \
  --input "$WORLD_DRIVING_ROOT/inputs/synthetic-intersection" \
  --model "$WORLD_DRIVING_ROOT/checkpoints/Alpamayo2-Edge" \
  --seed 19 --output "$WORLD_DRIVING_ROOT/outputs/alpamayo-cli"
```

Open `outputs/alpamayo-cli/output.json` for reasoning and `output.safetensors` for numeric predictions. The receipt records GPU, package versions, memory and exact input/output shapes. The runner verifies both weight shards against their published SHA-256 values before loading. In the recorded run the adaptive reasoning output is `<NOMINAL>`, rather than a longer explanation. To perform an actual closed-loop driving evaluation, use the separate [AlpaSim guide](../workflows/alpasim-closed-loop.md) and obtain the required scene access.

## Check the result

### Inspect saved products on a CPU

You only need Python and FFmpeg/FFprobe for the checker. Point it at a generation folder or an Alpamayo output folder. It fully decodes the video, checks requested frame count and FPS, and independently reads the saved trajectory tensors to reject nonfinite coordinates or wrong shapes.

```bash
python3 labs/world-driving/check.py \
  --cosmos labs/world-driving/evidence/cosmos-camera-actions \
  --alpamayo labs/world-driving/evidence/alpamayo-synthetic
```

The command uses bundled results and needs no model installation. After a GPU run, replace the paths with your own output folders.

Open `evidence/prediction-scene/alpamayo-trajectory.usda` to replay the 64 predicted poses in Isaac Sim. For control-and-observation feedback, continue to the [AlpaSim lab](../workflows/alpasim-closed-loop.md). [Replay generator](../../../labs/world-driving/make_prediction_scene.py).

### Compare the right things

- **Cosmos:** compare the initial and last frames, cube direction, camera motion and object identity. Report a prompt-following failure even when `sample_outputs.json` says `success`.
- **Alpamayo:** check that all weights loaded, the saved tensors are finite, and positions use the documented ego frame. A plausible explanation and a curved path do not establish safe driving.


[Source and version pins](../../../labs/world-driving/model-pins.json) · [Cosmos](../cosmos.md) · [Alpamayo](../alpamayo.md) · [AlpaSim closed loop](../workflows/alpasim-closed-loop.md)
