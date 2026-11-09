# Jetson / JetPack

[← All projects](../../README.md) · [한국어](../ko/jetson-jetpack.md)

## Overview

Edge AI hardware / software development kit.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Select Jetson hardware"] --> n1
    n1["install JetPack"] --> n2
    n2["optimize model"] --> n3
    n3["run edge inference"]
```

## Workflow and use

Select Jetson hardware → install JetPack → optimize model → run edge inference. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** running robot perception on an edge device. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** TensorRT, Isaac ROS, DeepStream.

## Architecture and example

Jetson is the embedded compute hardware family. JetPack supplies the software stack, including Jetson Linux and compatible versions of CUDA and TensorRT; support depends on the hardware and release.

Deploy a robot camera perception pipeline on a supported Jetson module and measure latency on the target hardware.

[Official technical source](https://developer.nvidia.com/embedded/jetpack/downloads)

## Availability and terms

Product and distribution; component terms vary. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[Jetson](https://developer.nvidia.com/embedded/jetson-modules) · [JetPack](https://developer.nvidia.com/embedded/jetpack)
