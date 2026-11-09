# cuRobo

[← Back to catalog](../../README.md) · [한국어](../ko/curobo.md)

cuRobo generates motions for a robot to reach a target pose under geometric and robot constraints. It takes a robot model, a description of the environment and a start state, and returns a planned trajectory for a separate controller to execute. The cuRobo and cuRoboV2 publications describe different planner designs.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Robot and collision geometry** | Kinematics describe the joints and links. Collision geometry approximates the robot and models obstacles in the world frame used by the planner. |
| **Inverse kinematics and trajectory optimization** | For a Cartesian goal, inverse kinematics generates candidate joint goals. The original planner evaluates and refines candidate trajectories on the GPU, taking collision and motion costs into account. |
| **cuRoboV2** | The V2 publication describes torque-aware B-spline optimization, GPU-native depth-fused distance fields and whole-body kinematics and dynamics. Check which API and collision backends your installed version exposes. |

![The Franka illustration shows the link-attached collision spheres used for planning. Check whether the approximations cover the actual links, gripper and any held object.](https://raw.githubusercontent.com/NVlabs/curobo/main/docs/images/franka_spheres.png)

The Franka illustration shows the link-attached collision spheres used for planning. Check whether the approximations cover the actual links, gripper and any held object. [Official figure source](https://github.com/NVlabs/curobo)

![The cuRoboV2-Fast deployment figure connects scene perception, grasp proposal and torque-limited motion planning. The object surface and the collision-distance map take different paths through the system.](https://arxiv.org/html/2611.06913v1/deployment_graph.png)

The cuRoboV2-Fast deployment figure connects scene perception, grasp proposal and torque-limited motion planning. The object surface and the collision-distance map take different paths through the system. [Official paper, figure 17](https://arxiv.org/html/2611.06913v1#S4.F17)

## Worked example

1. For a pick-and-place transit, provide the current joint state, target tool pose and obstacles in a common frame. Inspect the planned trajectory in simulation first.
2. Pass the accepted trajectory to the controller and check tracking and clearance separately. Replan if the scene changes.

## What to verify

- Check orientation conventions, joint names and collision margins. Incomplete collision geometry can produce a path that is clear only in the model.
- Read the planner status and benchmark the workload on the target GPU. Planning latency and physical controller tracking measure separate stages.

## Official references and terms

The repository code uses Apache-2.0. Review LICENSE_ASSETS and component terms when using robot assets or integrations.

- [Repository and version-specific releases](https://github.com/NVlabs/curobo)
- [Original cuRobo paper](https://arxiv.org/abs/2310.17274)
- [cuRoboV2 architecture and evaluation](https://arxiv.org/abs/2603.05493)
- [Current cuRobo documentation and release notes](https://nvlabs.github.io/curobo/latest/)

## Related guides

[SkillGen](skillgen.md) · [Isaac Manipulator](isaac-manipulator.md)
