# PyTorch

[← All projects](../../README.md) · [한국어](../ko/pytorch.md) · [Official source](https://github.com/pytorch/pytorch) · [Documentation / related project](https://docs.pytorch.org/docs/stable/index.html)

An open-source machine-learning framework for tensor computation and automatic differentiation.

**Availability and terms:** PyTorch is BSD-style licensed; models, packages, CUDA runtimes and other dependencies have their own conditions.

![PyTorch official illustration](https://raw.githubusercontent.com/pytorch/pytorch/main/docs/source/_static/img/tensor_illustration.png)

*Illustration: [official project repository](https://github.com/pytorch/pytorch); check source reuse terms.*

## Architecture and workflow

```mermaid
flowchart LR
    A["Data"] --> B["tensors and model"] --> C["training / inference"] --> D["outputs"]
```

*Conceptual illustration for this guide; refer to official sources for supported implementations.*

Load data into tensors, define a model and loss, train using automatic differentiation, and evaluate or export the result.

## Use cases

Train vision models, robot policies, and physics-informed models.

## Connections

Many ecosystem models and tools use PyTorch; TensorRT can be used in supported deployment paths.

## Official references

- [Project source](https://github.com/pytorch/pytorch)
- [Documentation / related project](https://docs.pytorch.org/docs/stable/index.html)
