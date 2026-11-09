# FoundationPose

[← Catalog](../../README.md) · [한국어](../ko/foundationpose.md)

FoundationPose estimates and tracks the 6D pose of an object that was unseen during training. A CAD mesh or reference views provide the instance-specific geometry.

![FoundationPose method diagram](https://nvlabs.github.io/FoundationPose/static/images/pipeline.jpg)

*The mesh and reference-view branches converge before candidate refinement and scoring.* [Official figure source](https://nvlabs.github.io/FoundationPose/)

![FoundationPose research results](https://nvlabs.github.io/FoundationPose/static/images/intro.jpg)

*Use these overlays as a reference for checking whether pose and geometry agree with the image.* [Official figure source](https://nvlabs.github.io/FoundationPose/)

## How it works

The model-based path renders the mesh. In the paper’s model-free path, an object-centric neural field renders novel RGB-D views from reference observations. Both use the same render-and-compare stages: initialize pose hypotheses, refine each candidate against the observation, score the refined poses, then select the best. Tracking uses the prior frame’s pose as a starting point.

## A practical workflow

Prepare a calibrated RGB-D sequence, object mask and correctly scaled mesh. Overlay the rendered silhouette from the first pose on the RGB image. Track across frames and deliberately occlude the object to decide when to register again. In a robot application, transform the object-to-camera pose into the base frame before computing a grasp.

## What to verify

Use measured poses or a fixture for reference. Check mask quality, depth units, mesh origin, camera intrinsics and object symmetries. Record initialization and tracking failures separately.

## License and availability

Research repository code restricts commercial use; separately distributed models have separate terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Research project, architecture and examples](https://nvlabs.github.io/FoundationPose/)
- [FoundationPose paper](https://arxiv.org/abs/2312.08344)
- [Related official resource · github.com](https://github.com/NVlabs/FoundationPose)
- [Related official resource · huggingface.co](https://huggingface.co/nvidia/foundationpose)
