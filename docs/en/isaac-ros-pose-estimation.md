# Isaac ROS Pose Estimation

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-pose-estimation.md)

The pose estimation packages estimate a rigid object’s translation and orientation. Their different model backends have different input contracts.

![Pose estimation node graph](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_pose_estimation/isaac_ros_pose_estimation_nodegraph.png)

*Follow the inputs for one backend rather than assuming every pose estimator accepts the same observations.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_pose_estimation/index.html)

## How it works

The FoundationPose route combines calibrated RGB-D, a target mask and object geometry. Pose candidates are refined and scored before tracking follows a previously estimated pose. Other documented backends, such as DOPE, use RGB features and a trained object model. The pose is expressed in a camera or configured frame before TF transforms it to the robot base.

## A practical workflow

Register a known part on a table, move it to a second measured position, and compare the reported transform against fiducials or a fixture. Transform the pose to the base frame and visualize the planned grasp before running the arm.

## What to verify

Verify depth units, mesh scale and origin, frame convention, symmetry, mask quality and occlusion. Check registration separately from tracking, and reinitialize tracking after loss.

## License and availability

Apache-2.0 code; models separate.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_pose_estimation/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_pose_estimation)
