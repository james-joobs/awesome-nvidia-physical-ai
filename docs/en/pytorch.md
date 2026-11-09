# PyTorch

[← Catalog](../../README.md) · [한국어](../ko/pytorch.md)

PyTorch supplies tensor computation, automatic differentiation and neural-network building blocks used by many model projects in this catalog.

![PyTorch autograd computation graph](https://docs.pytorch.org/tutorials/_images/comp-graph.png)

*The forward operations define dependencies used to propagate gradients during backpropagation.* [Official figure source](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)

## How it works

A dataset and loader supply batches of tensors. A module computes predictions, a loss scores them, and autograd tracks differentiable operations to compute gradients. An optimizer updates parameters from those gradients. A deployment workflow can serialize a checkpoint or export supported computation to a separate runtime.

## A practical workflow

Fine-tune a detector on labeled robot-camera images. Overfit a tiny batch first to check labels and gradient flow. Save the preprocessing settings with the model and compare predictions before and after deployment export.

## What to verify

Check device, dtype, tensor layout and train/eval modes. Test gradients independently from the data loader. Check export operator coverage and numeric agreement before deploying.

## License and availability

PyTorch is BSD-style licensed; models, packages, CUDA runtimes and other dependencies have their own conditions.

## Official references

- [Official technical reference](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)
- [Related official resource · github.com](https://github.com/pytorch/pytorch)
- [Related official resource · docs.pytorch.org](https://docs.pytorch.org/docs/stable/index.html)
