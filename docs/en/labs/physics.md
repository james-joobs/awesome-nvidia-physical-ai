# Physics you can see

## How it works

A **collider** is the shape the physics engine uses to detect contact. Two crates may look the same, yet an object can stop at different heights depending on where their colliders are. Start by keeping the visible shape and camera fixed and comparing just the colliders.

## Run it

**Before you start** · Use Isaac Sim 6.1 and keep the files in the [scene folder](../../../labs/physics/scenes) together. See [how to open a USD scene](../onboarding/isaac-sim-tools.md) if you are new to the GUI.

### 1. Compare collision shapes in the GUI

1. In Isaac Sim, choose **File → Open** and open `labs/physics/scenes/simready-live.usda`. Keep `simready-before.usda` and `simready-after.usda` next to it, as the scene references both.
2. Choose **FilmCamera** from the viewport’s camera menu and press **Play**. Look for whether the two objects stop at the same height.
3. Press **Stop** to reset. Open `collider-live.usda` to compare an aligned, raised, and disabled collider.

### 2. Write the measurements to disk

To record on Linux X11, activate the Isaac Lab Python environment and enter this repository in the terminal. Check that `command -v ffmpeg` returns a path. Paste the following block. The `--takes simready offset` option selects the two scenes you just viewed.

```sh
python labs/physics/capture_gui.py labs/physics/scenes ./runs/physics "$(command -v ffmpeg)" \
  --plan labs/physics/takes.json --takes simready offset --viz kit
```

To compare the two solvers numerically, run the [PhysX](../../../labs/physics/run_physx.py) and [Newton](../../../labs/physics/run_newton.py) scripts in their respective Python environments. Both accept an output folder, read the same [`scene.json`](../../../labs/physics/scene.json), and write position arrays. [SimReady validation](https://github.com/NVIDIA/simready-foundation/blob/main/nv_core/sr_specs/docs/guides/validate_workflow.md) · [PhysX](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/simulation_control/simulation_control.html) · [Newton XPBD](https://newton-physics.github.io/newton/latest/api/_generated/newton.solvers.SolverXPBD.html)

## Check the result

The SimReady probes ended 14 cm apart. The aligned, raised and disabled colliders left the test object's bottom at about 0.80, 0.92 and 0 m. As friction increased, travel fell from 57.0 to 25.5 to 11.4 cm. Increasing restitution raised the first rebound. Compare your `capture.json` and per-take physics samples with the [recorded measurements](../../../labs/physics/recorded.json).
