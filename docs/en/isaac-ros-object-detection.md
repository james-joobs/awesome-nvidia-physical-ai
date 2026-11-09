# Isaac ROS Object Detection

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-object-detection.md)

The object detection packages publish model-specific 2D detections from ROS camera streams. They supply perception results to downstream tracking or manipulation.

![Object detection node graph](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_object_detection/isaac_ros_object_detection_nodegraph.png)

*The output boundary is a set of 2D detections. Downstream nodes decide how to consume them.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_object_detection/index.html)

![Object detection node graph example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_object_detection/isaac_ros_object_detection_example_bbox.png)

*The overlay shows class boxes placed back on an input image.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_object_detection/index.html)

## How it works

The documented graph starts with an image encoder and a neural runtime. A detector-specific decoder produces 2D boxes, confidence and class labels. For example, a fixed-class detector uses its trained label set. An application can pass a detected box to a promptable segmentation node or use it to select an object region.

## A practical workflow

Use a bench camera to detect totes. Inspect images with overlays, then match detection timestamps against RGB frames and record false positives around similar packaging. If you need grasp coordinates, add depth and pose estimation.

## What to verify

Confirm trained label IDs, confidence and suppression settings, box coordinate conventions and model licensing. Evaluate detection under the actual viewing distance, occlusion and lighting.

## License and availability

Apache-2.0; models separate.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_object_detection/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_object_detection)
