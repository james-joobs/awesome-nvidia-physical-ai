# MoGe

[← Catalog](../../README.md) · [한국어](../ko/moge.md)

MoGe predicts dense geometry from a single RGB image. Output contracts differ by model generation, so the repository’s checkpoint examples are the starting point.

![MoGe method overview](https://raw.githubusercontent.com/microsoft/MoGe/main/assets/overview_simplified.png)

*The official figure shows how the RGB input becomes geometry predictions. Read the output contract for your checkpoint.* [Official figure source](https://github.com/microsoft/MoGe)

## How it works

The image encoder extracts features and the geometry heads predict a point map and valid-region information. The original method handles unknown global scale and shift in its formulation. Later versions extend the output, including metric geometry for supported checkpoints. A point map assigns a 3D point to each valid image pixel.

## A practical workflow

Run the model on a tabletop image and visualize the point map from a side view. Exclude invalid pixels and compare estimated distances with a known reference. Use the result as an initial geometry estimate in a reconstruction workflow.

## What to verify

Check coordinate convention, metric scale and valid masks for the checkpoint. Inspect far regions and depth discontinuities. Compare against calibrated stereo or measured geometry before using it for collision checks.

## License and availability

Verify code and checkpoint licenses separately for each model version and its dependencies.

## Official references

- [Official technical reference](https://github.com/microsoft/MoGe)
