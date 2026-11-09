# EgoHand / EgoPost

[← Back to catalog](../../README.md) · [한국어](../ko/egohand-egopost.md)

EgoHand reconstructs a person’s hands from head-mounted video. EgoPost hosts the post-processing code for this workflow in Isaac Capture. The reconstruction can be inspected in the camera frame or transformed into a world frame when the camera trajectory is available.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Video and calibration** | Supply decoded RGB video and calibration. Each hand also needs a 2D bounding box, either from an optional RT-DETR detector or from supplied per-frame box files. |
| **Hand reconstruction** | The inference pipeline uses hand crops and calibration to estimate SOMA hand poses, 3D joints and meshes. The optional sequence-fitting workflow estimates shared hand identity and scales with per-frame pose and translation. |
| **Camera localization** | A compatible camera localization or SLAM pipeline supplies camera motion for transforming camera-frame hand estimates into world coordinates. |
| **Artifacts for inspection** | Sequence fitting can export `soma_parameters.npz` and diagnostic reports. Overlay videos project the reconstructed joints back into the source image for frame-by-frame review. |

![The pipeline diagram separates hand reconstruction and camera localization. A world-frame hand trajectory depends on both estimates.](https://nvidia.github.io/IsaacCapture/main/_images/egohand-pipeline.svg)

The pipeline diagram separates hand reconstruction and camera localization. A world-frame hand trajectory depends on both estimates. [Official figure source](https://nvidia.github.io/IsaacCapture/main/ego_post_processing/egohand.html)

![The official V2D example illustrates the input camera view and reconstruction. Inspect fingers and wrists at contact points where occlusions are common.](https://nvidia.github.io/IsaacCapture/main/_images/egohand-v2d-example.jpg)

The official V2D example illustrates the input camera view and reconstruction. Inspect fingers and wrists at contact points where occlusions are common. [Official figure source](https://nvidia.github.io/IsaacCapture/main/ego_post_processing/egohand.html)

## Worked example

1. Start with the documented head-mounted V2D sample and its supplied calibration. Generate hand boxes or pass existing left and right boxes indexed by frame.
2. Run reconstruction and inspect the overlay before passing motion into a robot retargeting step. Add a camera trajectory only when the task needs a consistent world frame.

## What to verify

- Boxes use source-video pixels and anatomical left/right labels. A mirrored stream or wrong calibration can yield plausible-looking projections with incorrect 3D pose.
- Compare reprojected joints and check temporal jitter or sudden scale changes during occlusion. Compare world-space drift separately if camera localization is enabled.

## Official references and terms

EgoPost uses OpenMDW-1.1. A standalone EgoHand license has not been verified here. Check the terms attached to the exact assets and weights you use.

- [EgoHand setup, inputs and output artifacts](https://nvidia.github.io/IsaacCapture/main/ego_post_processing/egohand.html)
- [Isaac Capture source and component terms](https://github.com/NVIDIA/IsaacCapture)

## Related guides

[Isaac Capture](isaac-capture.md) · [Video to Data](video-to-data.md)
