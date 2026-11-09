# Isaac ROS Visual SLAM

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-visual-slam.md)

Isaac ROS Visual SLAM wraps cuVSLAM as a ROS 2 component for estimating robot motion from cameras.

![Odometry and Nav2 interfaces](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_visual_slam/vslam_odometry_nav2_diagram.png)

*Trace where the pose estimate enters Nav2. The application can consume odometry without owning the estimator.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_visual_slam/index.html)

![Odometry and Nav2 interfaces example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_visual_slam/cuvslam_ros_3.gif)

*Observe how the tracked path changes as the camera moves.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_visual_slam/index.html)

## How it works

**Input:** synchronized, calibrated camera streams and camera frames in TF. Supported configurations can also use IMU observations. **Estimation:** cuVSLAM tracks visual features across frames and triangulates landmarks to estimate incremental motion. SLAM mode adds a map and loop-closure corrections. **Output:** odometry and pose feed navigation and mapping. Keep continuous local odometry separate from the globally corrected map frame.

## A practical workflow

Record a loop around a warehouse aisle. Replay the same dataset once for odometry and again with mapping enabled, then compare the estimated end pose to the start. Use the pose with the stereo depth output in [Isaac ROS Nvblox](isaac-ros-nvblox.md).

## What to verify

Check image/IMU time alignment, calibration, TF, feature quality and drift. Repeated shelving, low texture, rapid turns and poor exposure can reduce tracking quality. Check how downstream consumers handle a map-frame correction.

## License and availability

Apache-2.0; cuVSLAM has separate terms.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_visual_slam/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam)
