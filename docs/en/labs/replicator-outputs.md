# Advanced Replicator lab · RGB, depth, and masks in 12 frames

**Optional advanced lab.** Use Isaac Sim 6.1 and Isaac Lab with this example’s own USD and checker to generate 960 × 540 data. If you are new to camera capture, start with the [Isaac Sim 6.2 workbench capstone](workbench-capstone.md).

## How it works

A photo shows the cube's color. Depth gives its distance from the camera plane, and segmentation says which pixels belong to it. Replicator knows the simulated scene, so it can export all three for one capture. The mask is an array of class IDs, one per pixel.

## Run it

**Before you start** · Activate the Isaac Lab Python environment paired with Isaac Sim 6.1 on your RTX machine. See the [Isaac Sim setup guide](../onboarding/isaac-sim-tools.md) for the available installation types. This script uses Isaac Lab’s app launcher, which a generic Python environment with NumPy does not provide.

### 1. Open the stage and capture the frames

From this repository in a terminal on the simulator machine, run the block below. The first path is the USD scene to open. The second is where the script saves the capture. `--viz kit` opens the window. Use a fresh output directory on a second run.

```sh
python labs/replicator-outputs/capture.py \
  labs/replicator-outputs/replicator-live.usda ./runs/replicator --viz kit
```

### 2. Read the first frame’s files

After the run, use the same terminal for the commands below. Open `rgb.png` in an image viewer and `semantic_labels.json` in a text editor. The two `.npy` files contain numeric arrays, which the checker can read. It checks that the three channels share the same dimensions and that the cube’s depth pixels are valid.

```sh
ls ./runs/replicator/frames/00
python labs/replicator-outputs/check_capture.py ./runs/replicator
```

With FFmpeg installed, run `python labs/replicator-outputs/preview_dataset.py ./runs/replicator` for a side-by-side preview. [NVIDIA Replicator tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/tutorial_replicator_getting_started.html)

## Check the result

Look for 12 distinct 960 × 540 triplets. The checker reads the arrays, compares the RGB hashes and semantic pixel counts to the manifest, and checks that cube pixels have finite, positive depth. Occluded frames 03, 07 and 11 contain fewer visible cube pixels. [Recorded manifest](../../../labs/replicator-outputs/recorded.json)
