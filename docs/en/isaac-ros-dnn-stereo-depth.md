# Isaac ROS DNN Stereo Depth

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-dnn-stereo-depth.md)

The stereo-depth packages estimate depth from calibrated camera pairs. Their documentation compares different models for throughput and accuracy tradeoffs.

![ESS ROS node graph](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_stereo_depth/isaac_ros_ess_nodegraph.png)

*The graph separates preprocessing, neural disparity and downstream conversion to depth.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html)

![ESS ROS node graph example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_stereo_depth/model_comparison.png)

*The official model comparison helps identify which accuracy and throughput tradeoffs need to be retested on your hardware.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html)

## How it works

Rectification aligns corresponding image points along epipolar rows. The inference node predicts disparity from the left and right frames. Depth follows from focal length × stereo baseline ÷ disparity when units and calibration agree. ESS and FoundationStereo have different model and compute requirements. The resulting depth image can feed [Nvblox](isaac-ros-nvblox.md).

## A practical workflow

Measure a box at several known distances using your stereo rig. Compare depth near the center, occluding edges and reflective surfaces. Replay the same frames through the candidate models to compare latency and valid-pixel coverage.

## What to verify

Validate baseline and units, alignment, expected model input resolution, and handling of invalid or low-confidence pixels. Quantify depth error versus distance before choosing a model or confidence threshold.

## License and availability

Apache-2.0 code; models separate.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_stereo_depth/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_stereo_depth)
