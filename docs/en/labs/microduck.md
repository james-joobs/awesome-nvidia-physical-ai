# Train and replay Microduck in Isaac Lab and Newton

## How it works

Isaac Lab supplies the flat-ground velocity task, Newton simulates the robot, and RSL-RL trains the policy. The recorded run uses the `backlash` preset, 512 parallel environments and seed 17. The video plays the trained checkpoint in four simulated environments using Newton's OpenGL viewer.

## Run it

Use [the official Microduck setup](https://huggingface.co/blog/nvidia/microduck-isaac-lab-sim-to-real). The recorded source revision was Isaac Lab `d7e49f0`. Use the wrappers from this repository with the prepared Isaac Lab checkout. Set `CHECKPOINT` to the `model_499.pt` path printed by the training job.

```sh
bash labs/microduck/train.sh /path/to/IsaacLab
bash labs/microduck/play.sh /path/to/IsaacLab "$CHECKPOINT"
```

The supplied [ONNX export](../../../labs/microduck/policy.onnx) is the portable exported policy. The Isaac Lab play command expects the training checkpoint in `.pt` format.

## Check the result

Our run completed 500 learning iterations. The final 50 iterations averaged 23.46 reward and 320.94 steps per episode, up from 0.65 and 35.50 during the first 50. Recalculate these numbers on a CPU with `python labs/microduck/read_training.py labs/microduck/training-metrics.txt ./runs/microduck-metrics`. [Recorded training measurements](../../../labs/microduck/recorded.json)
