# Robot motion and generated demonstrations

## How it works

### Turn a tool pose into a path for every joint

The goal specifies the tool’s position and orientation, and the starting state specifies the arm joints. The robot model maps joint values to the tool and link positions. cuRobo finds joint configurations that reach the goal and a path that avoids collision along the way. Adding an obstacle changes which intermediate configurations are feasible even when the goal stays fixed. [cuRobo documentation](https://curobo.org/) · [Lab planner](../../../labs/robot-motion/plan.py)

| Output | How to read it |
| --- | --- |
| `baseline_q` and `obstacle_q` in `motion.npz` | Each row is a waypoint. Columns are joint values in the robot model’s order. |
| `baseline_tool` and `obstacle_tool` | Each row contains tool position `[x, y, z]`. The recorded paths have 24 and 26 rows. |
| `replanned_tool_enters_obstacle` in `result.json` | Checks sampled tool positions against the new box. The planner separately checks the arm’s collision geometry. |

### How does this differ from generating demonstrations?

AutoData runs as a separate exercise. MimicGen reuses segments of a successful demonstration, such as picking up and putting down an object, and adapts them to a changed object arrangement. The simulation checks the resulting attempts before saving successful examples. In the [recorded result](../../../labs/robot-motion/recorded.json), `num_attempts: 6` and `num_success: 3` count attempts and successful demonstrations. `first_success_frame: 243` for `demo_0` marks the first successful frame in that demonstration. [MimicGen project](https://github.com/NVlabs/mimicgen)

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
