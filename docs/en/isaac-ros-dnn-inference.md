# Isaac ROS DNN Inference

[← Catalog](../../README.md) · [한국어](../ko/isaac-ros-dnn-inference.md)

Isaac ROS DNN Inference connects ROS 2 data to neural inference runtimes. The graph can use a TensorRT node or a Triton node, depending on deployment.

![DNN inference node graph](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_inference/isaac_ros_dnn_inference_nodegraph.png)

*Read from image encoding through inference to the decoder. Only the decoder gives the tensors application-level meaning.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_inference/index.html)

![DNN inference node graph example](https://media.githubusercontent.com/media/NVIDIA-ISAAC-ROS/.github/release-5.0/resources/isaac_ros_docs/repositories_and_packages/isaac_ros_dnn_inference/isaac_ros_dnn_peoplenet.jpg)

*PeopleNet boxes are an example of decoded outputs, useful for checking frame alignment and confidence thresholds.* [Official figure source](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_inference/index.html)

## How it works

The encoder converts image data into a model tensor with a fixed layout, normalization and input name. The inference node evaluates the network and emits output tensors. A model-specific decoder turns those tensors into ROS messages such as detections. NITROS negotiation can preserve compatible accelerated buffers between nodes.

## A practical workflow

Deploy a camera person detector. First compare encoded inputs and raw outputs against a reference inference run. Then connect the detection decoder and verify boxes are mapped back to the input frame after resize or padding.

## What to verify

Check tensor names, shape profiles, color channel order, model engine compatibility and the resize transform. Profile end-to-end latency including encoding and decoding. Triton model configuration and TensorRT engine artifacts are separate from the ROS graph.

## License and availability

Apache-2.0 code; runtime and models separate.

## Official references

- [Package overview and node graph](https://nvidia-isaac-ros.github.io/v/release-5.0/repositories_and_packages/isaac_ros_dnn_inference/index.html)
- [ROS package source](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_dnn_inference)
