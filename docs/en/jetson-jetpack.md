# Jetson / JetPack

[← Catalog](../../README.md) · [한국어](../ko/jetson-jetpack.md)

Jetson provides edge compute modules. JetPack supplies the system image and SDK components that run on supported modules.

![JetPack robotics software stack](https://developer.download.nvidia.com/images/jetson/robotics-diagram-update-jetpack7.2-cptx26.png)

*The diagram shows the layers included in the documented JetPack release. Match the layers to the release used on the module.* [Official figure source](https://developer.nvidia.com/embedded/jetpack)

## How it works

At the system layer, Jetson Linux supplies the board support package, drivers and interfaces for sensors and accelerators. Above it, CUDA and TensorRT support compute and inference, with application-level packages such as Isaac ROS or DeepStream on a compatible release. The module, carrier, OS release and runtime libraries constrain which containers and drivers work together.

## A practical workflow

For a mobile robot, start with the target carrier and Jetson Linux release. Verify camera enumeration and timestamps, then deploy a small TensorRT perception pipeline. Log end-to-end latency and power consumption during sustained operation before choosing a power profile.

## What to verify

Check the module and carrier support matrix, architecture of container images, compatibility of camera drivers and engine files, and performance after warm-up under the expected thermal load.

## License and availability

Product and distribution; component terms vary. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Architecture and workflow documentation](https://developer.nvidia.com/embedded/jetpack)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/embedded/jetpack/downloads)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/embedded/jetson-modules)
