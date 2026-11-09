# CUDA / TensorRT / ONNX

[← Catalog](../../README.md) · [한국어](../ko/cuda-tensorrt-onnx.md)

CUDA, TensorRT and ONNX are distinct layers in deployment. CUDA supplies accelerated computation, TensorRT builds and executes inference engines, and ONNX describes a portable model graph.

![ONNX example model graph](https://onnx.ai/onnx/_images/linreg1.png)

*The small official graph illustrates how inputs, constants and operators define model computation.* [Official figure source](https://onnx.ai/onnx/intro/concepts.html)

## How it works

An ONNX graph encodes tensors, operators, initializers and operator set versions. A compatible TensorRT parser turns it into a network for the builder. The builder chooses target implementations and emits an engine. Execution uses device buffers and CUDA streams. Applications still supply model preprocessing and interpret output tensors.

## A practical workflow

Export a model and save a fixed input/output fixture. Run the ONNX graph with a compatible runtime and compare against the source framework, then build and compare the TensorRT engine. This narrows down whether a mismatch begins at export or engine execution.

## What to verify

Confirm operator and shape coverage, plugin requirements, precision and device compatibility. Preserve labels and transforms alongside the graph. Check separately distributed CUDA and TensorRT terms.

## License and availability

ONNX code and specification have their own terms. CUDA and TensorRT product distributions, drivers and third-party components have separate NVIDIA or third-party conditions.

## Official references

- [Official technical reference](https://onnx.ai/onnx/intro/concepts.html)
- [TensorRT build and runtime](https://docs.nvidia.com/deeplearning/tensorrt/latest/architecture/how-trt-works.html)
- [Related official resource · github.com](https://github.com/onnx/onnx)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/tensorrt)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/cuda-toolkit)
- [Related official resource · onnx.ai](https://onnx.ai/)
