# Robot motion and generated demonstrations

## How it works

An arm may need a different path to reach the same goal once a box blocks its way. **cuRobo** computes a sequence of joint positions that avoids the obstacle. Demonstration generation is a separate exercise. **AutoData** uses a recorded example to generate more demonstrations under changed starting conditions.

## Run it

### 1. View two paths in Isaac Sim

Open the [cuRobo path scene](../../../labs/robot-motion/curobo-clearance.usda) via **File → Open**. Select **FilmCamera** and press **Play**. Identify which path goes around the box. The scene replays saved paths and does not need the planner installed.

### 2. Compute new paths in a terminal

Set up [cuRobo V2](https://nvlabs.github.io/curobo/latest/getting-started/motion_planning.html) at `71ce172` on your RTX machine. Enter this repository in a terminal with the cuRobo Python environment active. The script writes waypoint arrays to `motion.npz` and the comparison to `result.json`.

```sh
python labs/robot-motion/plan.py ./runs/curobo
```

### 3. Generate demonstrations with AutoData if needed

Use the [official AutoData example](https://github.com/isaac-sim/AutoData/blob/main/docs/pages/quickstart/first_data_generation.rst) to set up revision `4a3d1f3`, its Isaac Lab submodules, and the annotated Franka HDF5. HDF5 keeps a set of trials and their joint and object states together. In the AutoData environment, replace the paths in the first two lines before running the block.

```sh
AUTODATA_DIR="$HOME/AutoData"
DEMO_FILE="$HOME/dataset_franka_annotated.hdf5"
bash labs/robot-motion/autodata.sh "$AUTODATA_DIR" "$DEMO_FILE" ./runs/autodata
python labs/robot-motion/audit.py ./runs/autodata/franka-generated.hdf5 ./runs/autodata-audit
```

You can also start by opening the [AutoData replay scene](../../../labs/robot-motion/autodata-stack.usda). [GR00T placement](gr00t-placement.md) · [Microduck](microduck.md)

## Check the result

In the recorded run, the original tool center entered the new obstacle and the replanned path avoided it. The paths had 24 and 26 waypoints with the same endpoints. AutoData got three successful demonstrations in six attempts. Its replay reported three successes, and the audit finds each first success frame. [Recorded results](../../../labs/robot-motion/recorded.json)
