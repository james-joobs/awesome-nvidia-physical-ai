# RGB, depth and masks from the same camera

## How it works

Replicator attaches three annotators to one render product at `/World/SensorCamera`. The script varies cube position, light intensity and camera location, and places an occluder in front of the cube in every fourth frame. It writes RGB as PNG, depth in meters and semantic IDs as NumPy arrays, and the ID-to-label map as JSON. [Input USD scene](../../../labs/replicator-outputs/replicator-live.usda)

## Run it

Use an Isaac Lab environment with Isaac Sim 6.1, NumPy and Pillow. With the GUI available, run these commands from the repository root. To record the window on Linux X11, append `--record-window "$(command -v ffmpeg)"` to the first command. The optional third command assembles a sample and preview from the captured data using FFmpeg.

```sh
python labs/replicator-outputs/capture.py labs/replicator-outputs/replicator-live.usda ./runs/replicator --viz kit
python labs/replicator-outputs/check_capture.py ./runs/replicator
python labs/replicator-outputs/preview_dataset.py ./runs/replicator
```

[NVIDIA Replicator tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/tutorial_replicator_getting_started.html)

## Check the result

Look for 12 distinct 960 × 540 triplets. The checker reads the arrays, compares the RGB hashes and semantic pixel counts to the manifest, and checks that cube pixels have finite, positive depth. Occluded frames 03, 07 and 11 contain fewer visible cube pixels. [Recorded manifest](../../../labs/replicator-outputs/recorded.json)
