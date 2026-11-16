# GR00T picks up a cube and places it in a bowl

## How it works

Isaac Lab-Arena runs the DROID pick-and-place environment in Isaac Sim. It sends camera images, robot state, and the instruction to GR00T N1.6-DROID, then applies the returned joint and gripper targets. Arena records lifting and stable placement as separate events. The two configs reproduce the 24-second and 70-second trial limits in the comparison. [24-second config](../../../labs/gr00t-placement/droid-24s.yaml) · [70-second config](../../../labs/gr00t-placement/droid-70s.yaml)

## Run it

Set up [Isaac Lab-Arena and the GR00T server](https://isaac-sim.github.io/IsaacLab-Arena/release/0.3.1/pages/quickstart/running_a_real_policy/gr00t.html). The filmed run used Arena `c7edf3a` and the pinned GR00T submodule `e29d8fc`. Start the policy server from that submodule.

If the pinned revision returns a 404 for staging assets, apply the [asset URL patch](../../../labs/gr00t-placement/arena-production-assets.patch) to Arena with `git apply --unidiff-zero`. It points the same asset paths to NVIDIA's production mirror, as in the filmed run.

```sh
uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.6-DROID \
  --embodiment-tag OXE_DROID --device cuda --host 127.0.0.1 --port 5555
```

With the Arena Python environment active and this repository as your current directory, run the environment. The checkpoint and original Arena scene assets are fetched through their upstream projects.

```sh
bash labs/gr00t-placement/run_arena.sh /path/to/IsaacLab-Arena 70 ./runs/gr00t
python labs/gr00t-placement/check_result.py ./runs/gr00t/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

## Check the result

The three 24-second trials recorded two lifts and zero placements. The two 70-second trials placed the cube at 34.73 and 38.27 simulated seconds. The starting layouts differed, so the recordings tell you where each trial stopped. They do not isolate the effect of the time limit. Run the same parser on [recorded-24s.jsonl](../../../labs/gr00t-placement/recorded-24s.jsonl) and [recorded-70s.jsonl](../../../labs/gr00t-placement/recorded-70s.jsonl) to see the milestones without a GPU.
