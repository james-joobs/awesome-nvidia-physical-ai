# Isaac ROS Image Segmentation

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-image-segmentation.md)

The image segmentation packages turn camera images into pixel-level masks. A semantic mask labels classes by pixel, while instance-oriented pipelines can separate objects for downstream tasks.

![Image segmentation node graph](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_image_segmentation/isaac_ros_image_segmentation_nodegraph.png)

*Look at the decoder where a model tensor becomes a pixel mask.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_image_segmentation/index.html)

![Image segmentation node graph example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_image_segmentation/isaac_ros_image_segmentation_example_seg.png)

*The mask overlay shows pixel regions instead of a single bounding box per object.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_image_segmentation/index.html)

## How it works

An encoder converts the image to tensors. The inference runtime evaluates the segmentation model, and decoding yields masks aligned to image coordinates. The downstream consumer may use labels for scene understanding or pass the mask for one object to a pose estimator. The exact message and class mapping depend on the package and model.

## A practical workflow

For a bin with a target object, inspect the masks against a few hand-labeled RGB frames. Compare object edges and holes, then verify the chosen mask and depth frame are aligned before feeding [pose estimation](isaac-ros-pose-estimation.md).

## What to verify

Check class IDs, interpolation when resizing masks, alignment with the depth frame, and time synchronization. Measure downstream pose stability with partial masks and reflective or occluded targets.

## License and availability

Apache-2.0; models separate.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_image_segmentation/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_image_segmentation)
