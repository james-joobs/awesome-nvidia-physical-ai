# Physics you can see

## How it works

### Visible geometry and contact geometry

A **mesh** describes what the renderer draws. A **collider** is the geometry the physics engine uses to calculate distances and contacts. A simple box collider can save work, but its position and dimensions have to match the object closely enough for the task. A **rigid body** has state including position, orientation, and velocity. At each step, the engine advances motion under gravity and resolves contacts when shapes meet. Friction affects sliding along the surface, while restitution affects how the body bounces after impact. [Isaac Sim physics components](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/physics/simulation_fundamentals.html#simulation-components)

### Where does a collider offset show up?

| Collider setting | Value in the [recorded run](../../../labs/physics/recorded.json) | What to look for |
| --- | --- | --- |
| Aligned with the visible table | `aligned ≈ 0.80 m` | The probe meets the visible tabletop. |
| Collider raised by 12 cm | `raised ≈ 0.92 m` | The probe appears to stop in midair. |
| Table collider disabled | `disabled ≈ 0 m` | The probe passes the table and reaches the floor. |

These values are the final world Z coordinates at each probe’s **bottom face**. For friction, compare **distance traveled** before stopping. For restitution, compare **peak center height** after the first contact. The separate PhysX/Newton experiment runs for 240 steps at 120 Hz, or two simulated seconds. A similar final height can still accompany different horizontal positions. [Shared initial conditions](../../../labs/physics/scene.json)

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
