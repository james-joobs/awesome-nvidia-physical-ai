# SkillGen / SkillMimicGen

[← Back to catalog](../../README.md) · [한국어](../ko/skillgen.md)

SkillGen generates demonstrations by combining reusable local skills with planned motion between them. The research is published as SkillMimicGen. The Isaac Lab tutorial integrates the generation workflow with Isaac Lab Mimic and cuRobo for tasks such as cube stacking.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Local skill segments** | A recorded demonstration is annotated into object-relative contact-rich skills and transit motion. The skill boundaries determine what gets reused and where new planning begins. |
| **Motion-planned transit** | In a new scene reset, the generator adapts the local skill to the object pose, then uses the planner to reach the new start. Planning accounts for collision geometry along the transit. |
| **Rollouts and policies** | The simulator executes the planned transitions and local skill trajectories and records successful demonstrations. The paper also studies learning skill initiation, control and termination for planning-based execution; the Isaac Lab tutorial includes behavior cloning. |

![The official research figure separates reusable local skills from transit motion that can be planned again. This is the key distinction when adapting a demonstration to a different scene.](https://skillgen.github.io/resources/overview.png)

The official research figure separates reusable local skills from transit motion that can be planned again. This is the key distinction when adapting a demonstration to a different scene. [Official figure source](https://skillgen.github.io/)

![The Isaac Lab obstacle avoidance example demonstrates the motion planner’s role in the transit segment.](https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/obstacle_avoidance_curobo.gif)

The Isaac Lab obstacle avoidance example demonstrates the motion planner’s role in the transit segment. [Official figure source](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/features/imitation-learning/skillgen.html)

## Worked example

1. Use the official Franka cube-stacking example and label transitions around grasp and placement. Try the small generation run with visualization before scaling.
2. For the bin-stacking variant, inspect obstacle avoidance and whether the robot reaches the intended skill start. Compare generation success with downstream behavior-cloning success.

## What to verify

- Annotations and collision models strongly affect generation. Validate a small sample before launching a long run and record failure reasons by subtask.
- Follow the version-specific Isaac Lab and cuRobo setup. Check that the task IDs, source dataset and planner settings correspond to the same documented workflow.

## Official references and terms

Check the Isaac Lab implementation and its dependencies individually. The research page and the Isaac Lab tutorial document different parts of the workflow.

- [SkillMimicGen project and research figure](https://skillgen.github.io/)
- [Isaac Lab SkillGen tutorial](https://isaac-sim.github.io/IsaacLab/v3.0.0/source/features/imitation-learning/skillgen.html)
- [Paper and publication details](https://proceedings.mlr.press/v270/garrett25a.html)

## Related guides

[MimicGen](mimicgen.md) · [cuRobo](curobo.md) · [Isaac Lab](isaac-lab.md)
