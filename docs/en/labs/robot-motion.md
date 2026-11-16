# Robot motion and generated demonstrations

## How it works

The cuRobo portion plans a Franka trajectory to the same target twice. A cuboid intersects the original path, and cuRobo solves again with the obstacle in its world model. The visualization replays the collision spheres from those paths. The AutoData portion uses MimicGen to generate new cube-stacking demonstrations from an annotated dataset and replays the successful episodes. The other two tiles have their own labs. [GR00T placement](gr00t-placement.md) · [Microduck](microduck.md)

## Run it

Start with the [cuRobo path replay](../../../labs/robot-motion/curobo-clearance.usda) or the [AutoData replay scene](../../../labs/robot-motion/autodata-stack.usda) in Isaac Sim. Select `/World/FilmCamera` and press **Play**.

To compute new plans, install cuRobo V2 at `71ce172` and run the planner with its CUDA Python environment. For AutoData use `4a3d1f3` with its Isaac Lab submodules and the annotated Franka HDF5 from the official quickstart.

```sh
python labs/robot-motion/plan.py ./runs/curobo
bash labs/robot-motion/autodata.sh /path/to/AutoData /path/to/dataset_franka_annotated.hdf5 ./runs/autodata
python labs/robot-motion/audit.py ./runs/autodata/franka-generated.hdf5 ./runs/autodata-audit
```

[cuRobo motion planning](https://nvlabs.github.io/curobo/latest/getting-started/motion_planning.html) · [AutoData first dataset](https://github.com/isaac-sim/AutoData/blob/main/docs/pages/quickstart/first_data_generation.rst)

## Check the result

In the recorded run, the original tool center entered the new obstacle and the replanned path avoided it. The paths had 24 and 26 waypoints with the same endpoints. AutoData got three successful demonstrations in six attempts. Its replay reported three successes, and the audit finds each first success frame. [Recorded results](../../../labs/robot-motion/recorded.json)
