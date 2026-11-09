# Isaac Manipulator

[← Back to catalog](../../README.md) · [한국어](../ko/isaac-manipulator.md)

Isaac for Manipulation is a reference architecture for coordinating robot-arm perception, planning and execution in ROS 2. Individual packages contribute depth, object poses, obstacle maps and trajectories, which the workflow brings together for tasks such as picking and placing.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Visual input and object pose** | The reference workflow takes camera observations and estimates task object pose. Depending on the configuration, detectors or segmentation identify a region and FoundationPose estimates a pose for the manipulation stack. |
| **Scene collision model** | Stereo depth or another depth source feeds mapping. nvblox maintains local scene geometry and provides collision-relevant information to planning. |
| **Motion planning and execution** | MoveIt and cuMotion can use the current robot state, grasp goal and obstacles to compute a trajectory. Controllers execute the result while the workflow handles task progression. |

![The official reference diagram connects perception outputs to robot planning and execution. Follow the object-pose and obstacle-map paths independently because they solve different planning inputs.](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.2/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_main.png)

The official reference diagram connects perception outputs to robot planning and execution. Follow the object-pose and obstacle-map paths independently because they solve different planning inputs. [Official figure source](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)

![The RViz example gives a view of the scene and robot geometry used in the workflow. It is a practical starting point for verifying transforms before commanding the arm.](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.2/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_rviz.png)

The RViz example gives a view of the scene and robot geometry used in the workflow. It is a practical starting point for verifying transforms before commanding the arm. [Official figure source](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)

## Worked example

1. Set up a supported reference pick-and-place workflow. Confirm object pose and obstacle geometry in the planning frame using RViz.
2. Plan approach, grasp and retreat motions before executing the sequence. Record perception, planning and control failures separately.

## What to verify

- Check camera-to-base transforms, pose timestamps, attached objects and gripper tool frames. A correct camera-frame pose can still become an incorrect goal in the planning frame.
- Verify release-specific hardware and component prerequisites. The packages and model weights are distributed separately and may carry different terms.

## Official references and terms

Isaac ROS packages and model assets are published separately with their own terms.

- [Official reference architecture and figures](https://nvidia-isaac-ros.github.io/v/release-4.2/reference_workflows/isaac_for_manipulation/reference_architecture.html)
- [Isaac ROS Manipulator repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_manipulator)

## Related guides

[FoundationPose](foundationpose.md) · [Isaac ROS Nvblox](isaac-ros-nvblox.md) · [cuRobo](curobo.md)
