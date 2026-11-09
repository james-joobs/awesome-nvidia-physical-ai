# Isaac GR00T code
[← Back to catalog](../../README.md) · [한국어](../ko/isaac-gr00t.md)

Training, inference, and deployment code for GR00T robot policies.

**Official sources:** [Repository](https://github.com/NVIDIA/Isaac-GR00T)  
**License and scope:** Code: Apache-2.0; models and weights have separate terms.

![Isaac GR00T robot demonstration](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/header_compress.png)
*Image source: [Repository](https://github.com/NVIDIA/Isaac-GR00T)*

## Architecture and workflow

The following is an illustrative workflow, not an official architecture or a claim of automatic integration.

**Robot demonstrations and embodiment configuration → train or fine-tune policy → infer actions → evaluate and deploy**

## Components and official architecture

![GR00T model architecture](https://raw.githubusercontent.com/NVIDIA/Isaac-GR00T/main/media/model-architecture.png)

*Image source: [Official repository](https://github.com/NVIDIA/Isaac-GR00T)*

The repository combines policy training and inference code with model-specific configurations. Robot observations and language instructions are processed for action prediction; available model versions and embodiment interfaces determine the exact inputs, outputs and setup. Check weight terms separately from the repository code.

## Example use case

Adapt a generalist robot policy to a manipulation task using suitable demonstrations.

## Related technologies

Isaac Capture, Isaac Lab, LeRobot.

Check version compatibility, data formats, and model and dependency terms in the official sources for your setup.
