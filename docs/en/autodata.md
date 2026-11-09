# AutoData

[← Back to catalog](../../README.md) · [한국어](../ko/autodata.md)

AutoData expands a small set of successful robot demonstrations into simulated trajectories. A task definition tells the generator how to reset a scene, identify the reference object and judge success. The generated dataset contains robot actions and observations from replay in the simulator.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Source demonstrations** | Annotated episodes define subtask boundaries, the reference object and the demonstrated end-effector motion. A subtask can be expressed relative to its object so it can be reused at another pose. |
| **Generation algorithm** | MimicGen transforms and replays the object-relative segment in the new reset. SkillGen uses cuRobo to plan the transit to the adapted segment before executing the skill. |
| **Simulation and task checks** | The simulator executes target motions and the task applies termination and success checks. The output contains rollouts with actual simulation observations and actions. |

![The official architecture separates input demonstrations, generation logic and simulation. The task and simulator remain involved when a demonstration segment is reused in a changed scene.](https://raw.githubusercontent.com/isaac-sim/AutoData/main/docs/images/System_Architecture.svg)

The official architecture separates input demonstrations, generation logic and simulation. The task and simulator remain involved when a demonstration segment is reused in a changed scene. [Official figure source](https://github.com/isaac-sim/AutoData)

![The repository demonstration visualizes rollouts across scene variations. Compare the changed initial arrangement and the resulting executed paths.](https://media.githubusercontent.com/media/isaac-sim/AutoData/main/docs/images/autodata.gif)

The repository demonstration visualizes rollouts across scene variations. Compare the changed initial arrangement and the resulting executed paths. [Official figure source](https://github.com/isaac-sim/AutoData)

## Worked example

1. Start with successful pick-and-place trajectories and mark grasp and place boundaries and their object references.
2. Move the object or change the fixture position during resets. Choose interpolation or a planned transit based on obstacles in the scene.
3. Replay accepted examples and keep the dataset configuration, task success criteria and asset versions with the generated demonstrations.

## What to verify

- Compare success by reset condition rather than only total accepted episodes. Check whether difficult initial poses are systematically missing from the generated dataset.
- Inspect the join between transit and skill segments for collisions, discontinuities and incorrect gripper timing.

## Official references and terms

The repository code uses Apache-2.0. Check the separate terms of Isaac Sim and any cuRobo components used by your configuration.

- [Repository and official figure](https://github.com/isaac-sim/AutoData)
- [Generation algorithms](https://isaac-sim.github.io/AutoData/main/pages/concepts/algorithms.html)

## Related guides

[MimicGen](mimicgen.md) · [SkillGen](skillgen.md) · [cuRobo](curobo.md) · [Isaac Sim](isaac-sim.md)
