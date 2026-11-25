# Use GR00T to pick up a cube and place it in a bowl

## How it works

### How does a camera image become a robot action?

Isaac Sim produces the virtual camera views and robot state. Arena packages them in the format expected by the GR00T N1.6-DROID checkpoint and adds the instruction to put the cube in the bowl.

| Data passed along | What it tells the next stage | Consumer |
| --- | --- | --- |
| Camera views | Where the hand, cube, and bowl appear relative to each other. | GR00T vision input |
| Robot state and instruction | How the arm is posed and what task it should complete. | DROID state and language inputs |
| Predicted action sequence | Arm-joint and gripper targets for several future control steps. | Isaac Sim controller through the Arena adapter |

### What happens inside GR00T?

The lab uses the DROID checkpoint, a version of GR00T N1.6-3B fine-tuned on DROID. A vision-language model first turns the camera views and instruction into numeric representations. Conditioned on those representations and the robot state, the action head starts with sampled noise and updates it iteratively to produce a sequence of continuous commands. The training method for learning that transformation is called **flow matching**. Those internal updates produce one action prediction. The steps in the log below count actions applied in the simulated control loop. [NVIDIA N1.6 architecture](https://huggingface.co/nvidia/GR00T-N1.6-3B#model-architecture) · [DROID checkpoint](https://huggingface.co/nvidia/GR00T-N1.6-DROID)

The policy proposes a sequence of actions. The runner applies a configured portion, reads a fresh observation, and queries the policy again. The camera views and joint state change after the arm moves, so subsequent actions can respond to that change. Match the arm’s joint order and normalization to the checkpoint and adapter. [Arena GR00T walkthrough](https://isaac-sim.github.io/IsaacLab-Arena/release/0.3.1/pages/quickstart/running_a_real_policy/gr00t.html) · [GR00T modality configuration](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_config.md)

### Read “lift” and “placement” in a saved episode

Here is a projection of a few fields from the [first 70-second trial](../../../labs/gr00t-placement/recorded-70s.jsonl). JSONL stores one complete trial per line. Within the trial, `progress.events` records which checks passed and at which control steps.

```json
{
  "success": true,
  "episode_length": 521,
  "progress": { "events": [{ "step": 1 }, { "step": 442 }, { "step": 521 }] }
}
```

Step 1 marks the objects settling, step 442 marks the cube reaching the lift height, and step 521 marks placement on the destination. Convert steps to time using the control rate. The checker uses 15 Hz, so `442 ÷ 15 ≈ 29.47 seconds`. In the shorter 24-second runs, a successful lift could still end without a placement. Check for `object_on_destination` and the final outcome when you replay your own episode. [Result checker](../../../labs/gr00t-placement/check_result.py)

### Inspect the action arrays

The two RGB camera inputs are `[1,1,180,320,3]`: batch, time, height, width and RGB. The output is `joint_position[1,32,7]` plus `gripper_position[1,32,1]`. One prediction contains 32 future actions; the runner applies part of them before reading a fresh observation.

## Run it

**Before you start** · Use an RTX Linux machine with a desktop session and `uv`. Follow the [Isaac Sim setup](../onboarding/isaac-sim-tools.md) and prepare the native uv runtime in the [official Arena GR00T guide](https://isaac-sim.github.io/IsaacLab-Arena/release/0.3.1/pages/quickstart/running_a_real_policy/gr00t.html). This example uses Arena `c7edf3a` and GR00T submodule `e29d8fc`. The commands assume both repos are in your home folder. If you cloned them elsewhere, change the `cd` paths and `ARENA_DIR`.

### 1. Start GR00T in terminal A

Move into Arena, fetch its GR00T submodule, and start the model. You can paste the whole block. The first run downloads the model files. Keep this terminal open once the model is ready.

```sh
cd "$HOME/IsaacLab-Arena"
git submodule update --init submodules/Isaac-GR00T
cd submodules/Isaac-GR00T
uv run python gr00t/eval/run_gr00t_server.py --model-path nvidia/GR00T-N1.6-DROID \
  --embodiment-tag OXE_DROID --device cuda --host 127.0.0.1 --port 5555
```

### 2. Run the robot in terminal B on the same machine

Activate Arena’s Python environment, then enter this repository to run its script. The `70` selects the [70-second trial configuration](../../../labs/gr00t-placement/droid-70s.yaml). The Isaac Sim window opens and the arm starts moving. Arena asks the model in terminal A for actions at `127.0.0.1:5555`.

```sh
ARENA_DIR="$HOME/IsaacLab-Arena"
source "$ARENA_DIR/.venv/bin/activate"
cd "$HOME/awesome-nvidia-physical-ai"
bash labs/gr00t-placement/run_arena.sh "$ARENA_DIR" 70 ./runs/gr00t
```

If Arena gets a 404 from its staging asset URL, apply the [asset URL patch](../../../labs/gr00t-placement/arena-production-assets.patch) in the Arena checkout with `git apply --unidiff-zero`, then retry step 2.

### 3. Read your run log in terminal B

When the window closes and the terminal is ready for input again, run the commands below. If the filename differs, use the path printed by `find` in the second line. `lift` is when the robot picked the cube up. `placed` is when it left the cube in the bowl. `no` means the trial did not reach that milestone.

```sh
find ./runs/gr00t -name 'episode_results_*.jsonl'
python labs/gr00t-placement/check_result.py ./runs/gr00t/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

### Record your own live GUI run

Keep the policy server in terminal A running. In terminal B, use the command below **instead of step 2** to save the native Isaac Sim window, an initial USD scene, and object-position samples. This recorder needs an X11 desktop, `ffmpeg`, and `xwininfo`; it does not replay a previously successful trajectory.

```sh
export GR00T_GUI_FFMPEG="$(command -v ffmpeg)"
bash labs/gr00t-placement/run_recorded.sh "$ARENA_DIR" 70 ./runs/gr00t-gui
python labs/gr00t-placement/check_result.py \
  ./runs/gr00t-gui/evaluation/droid_pnp_gr00t/episode_results_rebuild0.jsonl
```

The [GUI recorder](../../../labs/gr00t-placement/record_gui.py) saves the video, initial USD scene and object positions. To inspect model inputs and actions, use the optional [policy recorder](../../../labs/gr00t-placement/record_policy.py) with `GR00T_MODEL_PATH` and `GR00T_POLICY_OUTPUT`.

## Check the result

Watch for two separate milestones: lifting the cube and leaving it in the bowl. The earlier 70-second examples reached placement; two later attempts lifted but missed the bowl. [Watch the later attempt, 2× playback](https://james-joobs.github.io/awesome-nvidia-physical-ai/showcase/gr00t-transfer-check.mp4).

Compare the end position and `object_on_destination` result, rather than stopping the review when the gripper lifts. Run the bundled checks without a GPU:

```sh
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-24s.jsonl
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-70s.jsonl
python3 labs/gr00t-placement/check_result.py labs/gr00t-placement/recorded-2026-11-19.jsonl
```

[Earlier successful episodes](../../../labs/gr00t-placement/recorded-70s.jsonl) · [Later attempts](../../../labs/gr00t-placement/recorded-2026-11-19.jsonl)
