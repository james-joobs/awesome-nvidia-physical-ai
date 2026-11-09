# DexMimicGen

[← Back to catalog](../../README.md) · [한국어](../ko/dexmimicgen.md)

DexMimicGen extends demonstration generation to bimanual dexterous tasks. It preserves relationships between two end effectors where the arms need to work together, and orders subtasks when one arm must complete an action before the other starts.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Parallel subtasks** | When each arm can reach its own subgoal independently, the generator selects and adapts segments for the two arms independently. |
| **Coordination subtasks** | When both arms manipulate a shared object or perform a handoff, the generator preserves coordination across the selected motions, using the object pose to transform the relevant segments. |
| **Sequential subtasks and evaluation** | Dependencies define which subtask must finish before another begins. The environment runs the two-arm actions and records the resulting observations and success. |

![The official pipeline figure distinguishes independent, coordinated and ordered motion. This distinction determines how two arms can reuse demonstrations safely under a new arrangement.](https://dexmimicgen.github.io/resources/pipeline.jpg)

The official pipeline figure distinguishes independent, coordinated and ordered motion. This distinction determines how two arms can reuse demonstrations safely under a new arrangement. [Official figure source](https://dexmimicgen.github.io/)

## Worked example

1. For a bimanual handoff, mark the first arm’s grasp, the shared transfer and the second arm’s placement. Declare where the arms must move together or wait for completion.
2. Randomize object or fixture pose. Verify transfer timing, end-effector clearance and the final outcome in the simulated rollouts before selecting episodes for imitation learning.

## What to verify

- Inspect both arm trajectories and finger commands. A completed task can conceal inconsistent handoff timing or implausible contact.
- Review the robot, simulator and dataset terms separately. A result for one embodiment is not a validation of the same subtask configuration on another.

## Official references and terms

The code uses the NVIDIA Source Code License. The published dataset uses CC BY 4.0.

- [Research project and pipeline figure](https://dexmimicgen.github.io/)
- [Code and data terms](https://github.com/NVlabs/dexmimicgen)
- [Paper with the subtask taxonomy](https://arxiv.org/abs/2410.24185)

## Related guides

[MimicGen](mimicgen.md) · [SkillGen](skillgen.md)
