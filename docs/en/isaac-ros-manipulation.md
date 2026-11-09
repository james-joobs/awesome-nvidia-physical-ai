# Isaac ROS Manipulation

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-manipulation.md)

Isaac ROS manipulation workflows connect perception, scene reconstruction and motion planning for robot arms.

![Isaac manipulation reference architecture](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.6/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_main.png)

*Trace the target and obstacle paths to the planner and controller. This is the release 4.6 reference workflow.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)

![Planning scene in RViz](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-4.6/resources/isaac_ros_docs/reference_workflows/isaac_for_manipulation/manipulator_RA_rviz.png)

*The visualization is where you compare the robot model, observed scene and plan before executing motion.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)

## How it works

The documented reference architecture has two perception branches. One produces an obstacle representation from RGB-D through Nvblox. The other produces a target pose from a detector or segmenter and a pose estimator. MoveIt or a cuMotion integration uses robot state, collision geometry and the target to generate a trajectory for the controller.

## A practical workflow

In Isaac Sim, bring up a Franka arm and calibrated camera. Visualize obstacle geometry, target pose and the planned trajectory in RViz. Move a blocking object and rerun planning, then compare success and minimum clearance.

## What to verify

Verify camera-to-base calibration, time alignment and planning scene updates. Check mesh scale and frames. Treat planner output, trajectory tracking and hardware limits as separate validation steps.

## License and availability

Apache-2.0 code; models and dependencies separate.

## Official references

- [Isaac Perceptor data flow](https://nvidia-isaac-ros.github.io/v/release-3.1/reference_workflows/isaac_perceptor/technical_details.html)
- [Isaac for Manipulation reference architecture](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)
- [Related official resource · github.com](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_manipulation)
