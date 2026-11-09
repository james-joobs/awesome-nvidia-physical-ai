# Isaac ROS DNN Inference
[← Back to catalog](../../README.md) · [한국어](../ko/isaac-ros-dnn-inference.md)

TensorRT and Triton inference integrations for ROS 2.

**Official sources:** [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference)  
**License and scope:** Apache-2.0 code; runtime and models separate.

![Isaac ROS DNN Inference official example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_inference/isaac_ros_dnn_peoplenet.jpg)
*Image source: [Repository](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference)*

## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**ROS 2 input tensors → TensorRT or Triton inference → output tensors → task-specific decoding**

## Example use case

Run a perception network inside a ROS 2 application.

## Related technologies

TensorRT, Triton, Isaac ROS.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
