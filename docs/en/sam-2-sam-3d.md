# SAM 2 / SAM 3D Objects

[← Catalog](../../README.md) · [한국어](../ko/sam-2-sam-3d.md)

SAM 2 segments objects in images and video. SAM 3D Objects estimates 3D object geometry and appearance from image evidence. Their interfaces serve different stages of a reconstruction workflow.

![SAM 2 model and memory](https://raw.githubusercontent.com/facebookresearch/sam2/main/assets/model_diagram.png)

*Follow frame features and memory into the mask prediction path.* [Official figure source](https://github.com/facebookresearch/sam2)

![SAM 3D Objects architecture](https://raw.githubusercontent.com/facebookresearch/sam-3d-objects/main/doc/arch.png)

*The reconstruction conditions on the target region and predicts 3D properties. Compare its output boundary with SAM 2’s 2D mask.* [Official figure source](https://github.com/facebookresearch/sam-3d-objects)

## How it works

**SAM 2.** A prompt encoder represents points or boxes. An image encoder supplies frame features, and the mask decoder emits a segmentation. Video inference uses memory from earlier interactions and predicted masks to condition later frames.

**SAM 3D Objects.** A target mask and image condition a reconstruction pipeline for shape and appearance. Its output is a 3D prediction whose invisible surfaces depend on learned priors.

## A practical workflow

Label an object in an early video frame, propagate the mask with SAM 2, and correct drift at occlusion boundaries. Choose a clear frame and mask for SAM 3D Objects. Inspect its result from unseen angles before using it as a visualization asset.

## What to verify

Measure mask quality before reconstruction. Confirm geometry scale, orientation and suitability for downstream tasks. Use independently measured geometry when dimensions or collision accuracy are critical. Review the separate SAM 2 and SAM 3D Objects terms.

## License and availability

SAM 2 code and model terms must be checked independently. SAM 3D Objects code and checkpoints are governed by the SAM License; review its terms and dependencies.

## Official references

- [Official technical reference](https://github.com/facebookresearch/sam2)
- [SAM 3D Objects architecture and demo](https://github.com/facebookresearch/sam-3d-objects)
