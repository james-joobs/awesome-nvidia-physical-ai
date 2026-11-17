# From a CAD workbench to sensor data

## How it works

A photo can show which way a cube moved, but it is hard to measure how many meters it moved from the photo alone. Use the **mask** to select cube pixels. Then use **depth** and the **camera pose** to put those pixels in the 3D scene. The collection of 3D points is a **point cloud**.

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
