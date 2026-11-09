# MimicGen

[← Back to catalog](../../README.md) · [한국어](../ko/mimicgen.md)

MimicGen reuses parts of existing robot demonstrations to create new imitation-learning episodes. It relies on observed object poses and task boundaries so recorded robot motions can be adapted when an object starts in a different place.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Task interface** | The environment exposes reference object poses and signals that identify the ends of subtasks. For example, a grasp signal can mark the transition from grasping to placing. |
| **Source selection and transformation** | The generator chooses source segments, expresses their end-effector trajectories relative to the relevant object, and transforms them using the current object pose. A transition joins the current robot pose to the adapted trajectory. |
| **Execution and acceptance** | The simulation executes each adapted segment. Task success conditions determine which trials become successful demonstration episodes. |

![The official overview shows how a few source demonstrations can generate episodes under varied scene configurations. The object-relative segments explain which parts of motion can be transferred.](https://mimicgen.github.io/resources/overview.png)

The official overview shows how a few source demonstrations can generate episodes under varied scene configurations. The object-relative segments explain which parts of motion can be transferred. [Official figure source](https://mimicgen.github.io/)

## Worked example

1. Break a pick-and-place task into a segment relative to the object being picked and another segment relative to its placement target. Supply the pose and termination signals in the simulator.
2. Randomize the two starting poses and inspect both accepted and failed rollouts. Train a policy on accepted episodes, then test it in placements excluded from generation.

## What to verify

- The first transition of each task termination signal must represent the actual semantic boundary. Wrong timing can transfer the wrong motion relative to an object.
- Count attempted and successful generations separately. Changes in robot morphology, reach and scene constraints affect which demonstrations can be reused.

## Official references and terms

The repository publishes source under the NVIDIA Source Code License. Refer to the repository terms for permitted uses.

- [Research project and overview diagram](https://mimicgen.github.io/)
- [Source and license](https://github.com/NVlabs/mimicgen)
- [Custom task interface](https://github.com/NVlabs/mimicgen/blob/main/docs/tutorials/datagen_custom.md)

## Related guides

[DexMimicGen](dexmimicgen.md) · [AutoData](autodata.md) · [SkillGen](skillgen.md)
