# Physics you can see

## How it works

Four OpenUSD stages isolate one change at a time. SimReady adds a convex-hull collider to the same crate mesh. The offset test shifts a collider 12 cm or disables it. The friction and bounce stages bind different PhysX contact materials to otherwise identical setups. The PhysX/Newton tile replays two pose streams from six boxes with the same initial poses and 240 steps at 120 Hz. [USD scenes](../../../labs/physics/scenes) · [Shared solver scene](../../../labs/physics/scene.json)

## Run it

Open any of the [live stages](../../../labs/physics/scenes) in Isaac Sim 6.1, select `/World/FilmCamera` in the viewport, then press **Play**. Keep the two SimReady crate layers beside `simready-live.usda`. To record the same four tests on Linux, use an Isaac Lab environment with Isaac Sim, X11 and FFmpeg.

```sh
python labs/physics/capture_gui.py labs/physics/scenes ./runs/physics "$(command -v ffmpeg)" \
  --plan labs/physics/takes.json --takes simready offset friction bounce --viz kit
```

With each solver's Python environment, run `python labs/physics/run_physx.py ./runs/solvers` and `python labs/physics/run_newton.py ./runs/solvers`. They write separate pose arrays. [SimReady validation](https://github.com/NVIDIA/simready-foundation/blob/main/nv_core/sr_specs/docs/guides/validate_workflow.md) · [PhysX simulation control](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/simulation_control/simulation_control.html) · [Newton XPBD](https://newton-physics.github.io/newton/latest/api/_generated/newton.solvers.SolverXPBD.html)

## Check the result

The SimReady probes ended 14 cm apart. The aligned, raised and disabled colliders left the test object's bottom at about 0.80, 0.92 and 0 m. As friction increased, travel fell from 57.0 to 25.5 to 11.4 cm. Increasing restitution raised the first rebound. Compare your `capture.json` and per-take physics samples with the [recorded measurements](../../../labs/physics/recorded.json).
