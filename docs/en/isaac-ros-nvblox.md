# Isaac ROS Nvblox

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-nvblox.md)

Isaac ROS Nvblox adapts the GPU voxel mapping library to ROS 2 and provides a costmap layer for Nav2.

![Depth and pose into mapping and Nav2](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_nvblox/isaac_ros_nvblox_nodegraph.png)

*Follow depth and pose into the reconstruction node, then follow the planner-facing slice separately from visualization.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_nvblox/index.html)

![Depth and pose into mapping and Nav2 example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_nvblox/isaac_sim_nvblox_humans.gif)

*The simulator example shows people in a mapped scene. Inspect the map and costmap together when testing dynamic obstacles.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_nvblox/index.html)

## How it works

Depth and camera intrinsics give 3D measurements. Pose or TF places each measurement into a shared map frame. Nvblox integrates measurements into a voxel reconstruction and derives distances to obstacles. Nav2 receives a 2D costmap slice. Optional RGB contributes color to visualization, while the mesh is a separate output from the costmap.

## A practical workflow

Bring up depth and TF in a small simulated aisle. Set the slice height for the obstacle geometry the robot must avoid. Place a low box and an overhanging shelf and compare what the mesh sees with what the planner sees.

## What to verify

Check depth scale, matching camera intrinsics, TF delays, voxel resolution and the slice height. Smaller voxels increase detail and GPU memory use. Dynamic human handling depends on the selected pipeline and its supported inputs.

## License and availability

Apache-2.0; dependencies separate.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_nvblox/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox)
