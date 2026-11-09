# GR00T-VisualSim2Real

[← Back to catalog](../../README.md) · [한국어](../ko/gr00t-visualsim2real.md)

GR00T-VisualSim2Real contains code for the VIRAL and DoorMan research systems. Both train a humanoid in simulation and target physical deployment using onboard observations. VIRAL focuses on the teacher-to-visual-policy pipeline; DoorMan studies whole-body interaction with a door.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Simulation teacher** | The VIRAL training stage uses PPO with privileged information available in simulation. It can use simulator state such as task object poses during learning. |
| **Visual student** | The student learns from the teacher with deployable observations such as RGB and proprioception. The project describes scaling training data and visual randomization to bridge differences between rendered and real observations. |
| **Hardware interface** | The deployment path feeds the onboard camera and state into the visual policy, then executes predicted robot commands. Camera field-of-view alignment and hardware characterization are separate checks in the official project. |

![VIRAL’s official pipeline shows where simulation-only teacher information gives way to the observations the real robot can supply.](https://viral-humanoid.github.io/static/images/VIRAL-Pipeline.png)

VIRAL’s official pipeline shows where simulation-only teacher information gives way to the observations the real robot can supply. [Official figure source](https://viral-humanoid.github.io/)

![DoorMan’s demonstration shows locomotion, contact with the door and passage through the opening as parts of one task.](https://media.githubusercontent.com/media/NVlabs/GR00T-VisualSim2Real/main/media/doorman-teaser.gif)

DoorMan’s demonstration shows locomotion, contact with the door and passage through the opening as parts of one task. [Official figure source](https://github.com/NVlabs/GR00T-VisualSim2Real)

## Worked example

1. For a Unitree G1 study, reproduce the published simulation rollout for a supported task and record teacher/student success separately.
2. Check camera pose and field of view before running the visual policy on hardware. Evaluate the complete task in a controlled setup and record contact failures or target visibility issues.

## What to verify

- Match the project branch and robot model to the reported example. VIRAL and DoorMan have distinct code paths and task definitions.
- Compare field of view, observation timing and physical contact conditions before attributing a deployment failure to the learned policy.

## Official references and terms

The repository code uses Apache-2.0. Check the terms of model checkpoints, simulator assets and robot descriptions separately.

- [Code and branch map](https://github.com/NVlabs/GR00T-VisualSim2Real)
- [VIRAL architecture and experiments](https://viral-humanoid.github.io/)
- [DoorMan project and paper](https://doorman-humanoid.github.io/)

## Related guides

[Isaac Lab](isaac-lab.md) · [WBC-AGILE](wbc-agile.md)
