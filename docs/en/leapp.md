# LEAPP

[← Back to catalog](../../README.md) · [한국어](../ko/leapp.md)

LEAPP exports the computation around a trained policy alongside the model. It captures tensor operations for observation construction, policy inference and command processing, then packages executable artifacts and a description of their inputs and outputs.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Trace boundary** | Annotate named input and output tensors around an execution path. LEAPP follows supported tensor operations across helper functions and can capture preprocessing and postprocessing together with inference. |
| **Compiled graph and bundle** | Compilation emits model artifacts, such as ONNX, plus YAML describing tensor names, shapes, dtypes, backends and graph connectivity. Tensor semantics can describe what those values mean to a robot runtime. |
| **Validation and runtime** | Optional compilation validation replays example inputs. Downstream runtimes load the bundle and map graph inputs and outputs to their actual sensor and control interfaces. |

![The official example graph groups normalization, inference and action scaling inside a single exported control node. The edges identify what the target runtime needs to supply and receive.](https://nvidia-isaac.github.io/leapp/_images/getting_started_graph.png)

The official example graph groups normalization, inference and action scaling inside a single exported control node. The edges identify what the target runtime needs to supply and receive. [Official figure source](https://nvidia-isaac.github.io/leapp/getting_started.html)

## Worked example

1. Start with the official joint-control example. Annotate joint position, velocity and context, then expose final joint targets after scaling and clipping.
2. Open the exported graph and YAML together. Check shape and dtype, then compare ONNX outputs with the original Python pipeline on representative sensor states.

## What to verify

- Tracing records the path that executed. Check warnings, data-dependent branches and tensor-to-scalar conversions, then validate with inputs beyond the trace sample.
- Version the model, YAML and optional state artifacts together. Changing sensor ordering or scaling changes the deployed policy interface even with the same model weights.

## Official references and terms

The LEAPP source uses Apache-2.0. Exported weights and runtime dependencies retain their own terms.

- [Source and license](https://github.com/nvidia-isaac/leapp)
- [Official trace example and graph](https://nvidia-isaac.github.io/leapp/getting_started.html)
- [Export options](https://nvidia-isaac.github.io/leapp/guides/export.html)

## Related guides

[Isaac ROS Deploy](isaac-ros-deploy.md) · [WBC-AGILE](wbc-agile.md)
