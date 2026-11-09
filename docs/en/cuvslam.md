# cuVSLAM

[← Catalog](../../README.md) · [한국어](../ko/cuvslam.md)

cuVSLAM is the CUDA-accelerated odometry and mapping library used by the separate Isaac ROS Visual SLAM package. It also exposes native and Python interfaces.

![cuVSLAM Python workflow](https://media.githubusercontent.com/media/nvidia-isaac/cuVSLAM/main/examples/assets/pycuvslam_overview.jpg)

*The official example shows calibration and sensor configuration around the tracking call.* [Official figure source](https://github.com/nvidia-isaac/cuVSLAM)

## How it works

Initialize a rig with calibrated camera models, extrinsics and a tracking mode. New timestamped images, and optional IMU or depth in supported modes, update the tracked pose. Stereo establishes metric scale using the baseline. The monocular configuration has scale ambiguity. A mapping layer can use the tracked trajectory for global localization and loop closure.

## A practical workflow

Run the official multicamera example on recorded data. Plot the incremental path and compare against a measured loop. Inspect missed frames and compare blur under slower and faster motion. Use [Isaac ROS Visual SLAM](isaac-ros-visual-slam.md) for ROS messages and TF.

## What to verify

Validate time synchronization, exposure, calibration and supported sensor modes. Track drift, loss of tracking and relocalization as separate behaviors.

## License and availability

NVIDIA Community License restricts use to NVIDIA platforms; distinct from its ROS wrapper. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Modes, calibration and examples](https://github.com/nvidia-isaac/cuVSLAM)
- [cuVSLAM technical report](https://arxiv.org/html/2506.04359v3)
