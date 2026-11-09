# TAO Toolkit

[← Catalog](../../README.md) · [한국어](../ko/tao-toolkit.md)

TAO Toolkit provides predefined workflows for adapting vision models to task-specific data and exporting them for deployment.

![TAO Toolkit overview](https://docs.nvidia.com/tao/tao-toolkit/latest/_images/tao_overview_image.png)

*Use the official overview to locate training and export in the deployment workflow.* [Official figure source](https://docs.nvidia.com/tao/tao-toolkit/latest/text/overview.html)

![TAO software stack](https://docs.nvidia.com/tao/tao-toolkit/latest/_images/tao_stack.png)

*The stack shows how TAO’s workflow sits above the accelerated software underneath.* [Official figure source](https://docs.nvidia.com/tao/tao-toolkit/latest/text/overview.html)

## How it works

The training specification chooses the model, dataset and optimization settings. A supported pretrained checkpoint initializes training. Evaluation checks the adapted model against labeled validation data. Export produces an artifact whose format depends on the task. TensorRT and DeepStream can consume compatible exports using the documented deployment instructions.

## A practical workflow

Generate labeled images with [Replicator](replicator.md), then fine-tune a detector for parts on a conveyor. Reserve a real camera validation set and compare the pretrained and adapted models on it before exporting. Reproduce a few predictions after deployment.

## What to verify

Check class definitions, dataset format, train/test scene leakage and real camera coverage. Keep exported preprocessing and postprocessing consistent with training. Verify compatibility and model terms for the selected workflow.

## License and availability

Product/SDK; check model and component terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Architecture and workflow documentation](https://docs.nvidia.com/tao/tao-toolkit/latest/text/overview.html)
- [Related official resource · docs.nvidia.com](https://docs.nvidia.com/tao/tao-toolkit/latest/text/reference_workflows/index.html)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/tao-toolkit)
