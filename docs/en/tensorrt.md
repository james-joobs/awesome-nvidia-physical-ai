# TensorRT public code

[← Catalog](../../README.md) · [한국어](../ko/tensorrt.md)

TensorRT builds optimized inference engines from supported networks and runs those engines on NVIDIA devices. The public repository contains plugins, samples and related code.

![TensorRT object lifetimes](https://docs.nvidia.com/deeplearning/tensorrt/latest/_images/trt-object-lifetimes.svg)

*Use the diagram to distinguish build objects from runtime objects and see which owners must outlive their dependents.* [Official figure source](https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/how-trt-works.html)

## How it works

In the build phase a parser or network definition describes layers, shapes and data types. The builder profiles implementation choices and produces a serialized engine. At runtime an execution context manages execution state and, where applicable, runtime shapes. The application binds buffers and enqueues work on a CUDA stream. Plugins extend supported operations when the required implementation is available.

### Component interfaces

| Component | Input | Output |
|---|---|---|
| Build | Model graph, optimization profiles, precision and plugins | Serialized engine for compatible targets |
| Load | Engine file and compatible runtime | Deserialized engine and execution context |
| Execute | Input buffers, runtime shapes and CUDA stream | Output buffers for application postprocessing |

## A practical workflow

Export a robot detector as ONNX, build an engine with the deployment input shape, and compare raw outputs with the training framework on identical inputs. Use a warm-up, then measure both inference latency and whole-pipeline latency.

## What to verify

Verify compatibility with the runtime and target GPU, chosen precision, dynamic shapes and required plugins. When evaluating lower precision, check application accuracy and rare cases as well as latency. Plan engine rebuilds for incompatible runtime or target changes.

## License and availability

Repository: Apache-2.0; this does not cover the entire TensorRT binary SDK. Models, data, dependencies and hosted services may have separate terms; check each source before use.

## Official references

- [Architecture and workflow documentation](https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/how-trt-works.html)
- [Related official resource · github.com](https://github.com/NVIDIA/TensorRT)
