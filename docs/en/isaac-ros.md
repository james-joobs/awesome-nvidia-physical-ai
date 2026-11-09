# Isaac ROS

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros.md)

Isaac ROS packages connect accelerated perception, localization and manipulation to ROS 2. The Perceptor reference workflow shows how individually reusable nodes form a complete robot perception stack.

![Isaac Perceptor data flow](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-3.1/resources/isaac_ros_docs/repositories_and_packages/isaac_perceptor/perceptor_diagram.png)

*Follow the stereo input as it splits into odometry and depth and rejoins at Nvblox. The diagram documents Perceptor release 3.1.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-3.1/reference_workflows/isaac_perceptor/technical_details.html)

## How it works

1. **Sensor layer.** Time-synchronized stereo frames can come from Nova cameras, a recording or Isaac Sim. Image pipeline nodes rectify frames.
2. **Parallel geometry branches.** Stereo depth estimates distance along camera rays. Visual SLAM estimates motion and pose from sequences of images.
3. **Map and planner.** Nvblox integrates depth at the estimated pose to build a local voxel map. A 2D costmap plugin makes obstacles available to Nav2. NITROS supports efficient transfer for nodes that negotiate compatible accelerated message formats.

### Component interfaces

| Component | Input | Output |
|---|---|---|
| Stereo acquisition | Synchronized left/right images and camera info | Rectified image topics to depth and SLAM |
| Geometry | Stereo disparity and tracked camera poses | Depth image and world-to-camera relationship to mapping |
| Local planning | Voxel reconstruction and configured slice heights | Costmap layer queried by Nav2 |

## A practical workflow

Replay a warehouse rosbag first. Inspect rectified images, then visualize odometry and the depth image separately. Add Nvblox and check that a stationary pallet stays in one place in the map as the robot moves. Connect the costmap to Nav2 once localization and obstacle marking agree.

## What to verify

Confirm topic remaps, timestamp synchronization, camera calibration and TF connectivity. Measure sensor-to-costmap latency and watch for conversions across CPU/GPU boundaries. Start with a release-specific reference launch and compatible drivers.

## License and availability

Package terms vary; check licenses for each repository and distribution.

## Official references

- [Isaac Perceptor data flow](https://nvidia-isaac-ros.github.io/v/release-3.1/reference_workflows/isaac_perceptor/technical_details.html)
- [Isaac for Manipulation reference architecture](https://nvidia-isaac-ros.github.io/v/release-4.6/reference_workflows/isaac_for_manipulation/reference_architecture.html)
- [Related official resource · nvidia-isaac-ros.github.io](https://nvidia-isaac-ros.github.io/)
- [Related official resource · github.com](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common)
