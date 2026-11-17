# Train and replay Microduck in Isaac Lab and Newton

## How it works

The walking policy starts out without knowing how to follow a speed command. Isaac Lab runs many copies of the exercise, **Newton** computes foot contact, and **RSL-RL** updates the policy using a score for how well it does. A **checkpoint** saves what the policy learned.

## Run it

**Before you start** · Train on an RTX machine. Follow the [NVIDIA Microduck setup](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real) for the Isaac Lab `d7e49f0` environment and `uv`. The commands below assume your Isaac Lab checkout is in your home folder.

### 1. Train a walking policy

Open a terminal in this repository. Change the first path if you cloned Isaac Lab elsewhere. Watch the terminal for iteration counts and rewards. The example uses 512 simulated environments and runs for 500 iterations.

```sh
ISAAC_LAB_DIR="$HOME/IsaacLab"
bash labs/microduck/train.sh "$ISAAC_LAB_DIR"
```

### 2. Replay the learned policy

When the prompt returns, find the `model_499.pt` path in the training output. Replace the example path with the full path to that file, then run both lines in the same terminal. The viewer will use the learned policy to make the robot walk.

```sh
CHECKPOINT="/actual/training/path/model_499.pt"
bash labs/microduck/play.sh "$ISAAC_LAB_DIR" "$CHECKPOINT"
```

The [ONNX export](../../../labs/microduck/policy.onnx) carries the policy to another runtime. Use the training `.pt` checkpoint for the Isaac Lab replay above.

## Check the result

Check whether the reward rises during training and whether the robot follows the requested speed when you replay it. Reward is the score for following the task.

**Check the saved training log on a CPU.** From this repository, run the command below to compute averages for the first and last 50 iterations.

```sh
python3 labs/microduck/read_training.py labs/microduck/training-metrics.txt ./runs/microduck-metrics
```

In the filmed run, mean reward rose from 0.65 to 23.46, and mean episode length from 35.50 to 320.94 steps. [Recorded training measurements](../../../labs/microduck/recorded.json)
