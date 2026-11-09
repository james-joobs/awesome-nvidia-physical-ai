# WBC-AGILE

[← Back to catalog](../../README.md) · [한국어](../ko/wbc-agile.md)

WBC-AGILE is an Isaac Lab training and deployment stack for humanoid control. Its published examples range from velocity and body-height tracking to recovering from the ground and coordinating upper-body motion during locomotion.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Task and simulation environment** | Robot articulation and contacts are simulated in Isaac Lab. The selected task defines observations, commands, rewards and termination conditions for the policy. |
| **Policy coordination** | AGILE examples include separate upper- and lower-body policies. The lower body must maintain locomotion and balance while upper-body targets change, so the observations and command interfaces depend on the selected policy configuration. |
| **Export and evaluation** | Supported checkpoints can be exported with LEAPP. The deployment workflow uses the bundle with Isaac ROS Deploy for simulation-to-simulation and simulation-to-real evaluation. |

![The upper/lower-body policy diagram shows how the separate control paths share the robot. The split concerns the illustrated policy configuration.](https://media.githubusercontent.com/media/nvidia-isaac/WBC-AGILE/main/docs/figures/separate_upper_lower_body_policy_diagram.png)

The upper/lower-body policy diagram shows how the separate control paths share the robot. The split concerns the illustrated policy configuration. [Official figure source](https://github.com/nvidia-isaac/WBC-AGILE)

![The Unitree G1 example demonstrates velocity and body-height tracking on hardware. Compare it with the paired simulation example in the repository.](https://media.githubusercontent.com/media/nvidia-isaac/WBC-AGILE/main/docs/videos/unitree_g1_vel_height_sim2real.gif)

The Unitree G1 example demonstrates velocity and body-height tracking on hardware. Compare it with the paired simulation example in the repository. [Official figure source](https://github.com/nvidia-isaac/WBC-AGILE)

## Worked example

1. Reproduce a published Unitree G1 or Booster T1 rollout using the matching task and checkpoint. Export with the official LEAPP script if the checkpoint is supported.
2. Run the exported policy in simulation before trying hardware. Compare command tracking, fall or recovery behavior and the loop frequency across runtimes.

## What to verify

- Keep the export directory intact. Its YAML refers to the exported model and, when needed, state artifacts via relative paths.
- Validate the target joint order, control mode and action scaling for the hardware. Simulated recovery behavior can depend on contact and actuator assumptions.

## Official references and terms

The project uses Apache-2.0 and identifies BSD-3-Clause RSL-RL patches. Check checkpoint and robot asset terms separately.

- [Repository, policy diagrams and demonstrations](https://github.com/nvidia-isaac/WBC-AGILE)
- [AGILE deployment and export](https://nvidia-isaac.github.io/WBC-AGILE/deploy-policies.html)

## Related guides

[Isaac Lab](isaac-lab.md) · [LEAPP](leapp.md) · [Isaac ROS Deploy](isaac-ros-deploy.md)
