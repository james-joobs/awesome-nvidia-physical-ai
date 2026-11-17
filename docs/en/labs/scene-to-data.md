# From a CAD workbench to sensor data

## How it works

### Move a pixel into the 3D scene

Find the ID labeled `part` in the JSON lookup, select those pixels, and keep their finite positive depths. Each pixel identifies a direction from the camera. The USD focal length and sensor width determine that direction, and the depth locates the visible surface along it. The script assumes a centered camera and square pixels.

```text
Select part in the mask → read column u, row v, and depth
                                     ↓
                          point in camera coordinates
                                     ↓ USD camera position and rotation
                                world (x, y, z)
```

At pixel `(u=613, v=231)` in the first saved frame, the depth is about `3.164 m` and the semantic ID is `2`. That frame’s JSON maps `2` to `part`, so the pixel contributes to the cube point cloud. A background or workbench pixel is excluded even when it has valid depth. [Backprojection script](../../../labs/scene-to-data/backproject.py) · [Source RGB-D frames](../../../labs/scene-to-data/replicator-data.zip)

### Why subtract the first frame?

The cloud contains the visible surface. The apparent center of those visible points can be offset from the cube’s physical center. The checker subtracts frame 0’s median X coordinate to estimate relative motion. In the [saved frame 1 result](../../../labs/scene-to-data/recorded.json), `estimated_relative_x_m ≈ -0.300` and `authored_relative_x_m = -0.305`. The minus sign means world X decreased, and the two displacements differ by about 5.27 mm.

## Run it

**Before you start** · Open a terminal on any computer with Python 3.12. This part uses saved captures, so it runs without a GPU.

### 1. Prepare Python for the point cloud

Enter this repository’s folder. A separate virtual environment keeps these libraries apart from other Python projects.

```sh
python3.12 -m venv .venv-workbench
source .venv-workbench/bin/activate
python -m pip install -r labs/scene-to-data/requirements-check.txt
```

### 2. Read four saved camera frames

In the same terminal, run the command below. `--recorded` uses the bundled USD and [camera captures](../../../labs/scene-to-data/replicator-data.zip). The checker saves the files and results under `runs/workbench-replay`.

```sh
python labs/scene-to-data/check_workbench.py runs/workbench-replay --recorded
```

Open `check/frame-00.png` in that folder to see the photo, depth, and mask side by side. In `check/point-cloud/result.json`, `estimated_relative_x_m` shows the X movement in meters. To make new captures, continue to the [workbench capstone](workbench-capstone.md). [Workbench USD](../../../labs/scene-to-data/workbench_scene.usda) · [Point-cloud replay](../../../labs/scene-to-data/rgbd-surface.usda) · [12-frame Replicator lab](replicator-outputs.md)

## Check the result

The STEP round trip checks a 1,200 × 600 × 40 mm tabletop. In our run the cube center stopped at 0.8615 m. The four recorded point clouds recovered relative X displacement with a maximum error of about 5.3 mm. It compares the visible surface to the first frame, so the measurement describes movement of the surface rather than absolute cube-center position. [Recorded measurements](../../../labs/scene-to-data/recorded.json)
