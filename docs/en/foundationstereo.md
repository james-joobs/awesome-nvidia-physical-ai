# FoundationStereo

[← Catalog](../../README.md) · [한국어](../ko/foundationstereo.md)

FoundationStereo estimates dense disparity between rectified stereo images. Calibration converts disparity to metric depth.

![FoundationStereo network overview](https://nvlabs.github.io/FoundationStereo/static/images/overview.jpg)

*Read from feature extraction to cost filtering and iterative disparity refinement.* [Official figure source](https://nvlabs.github.io/FoundationStereo/)

![FoundationStereo depth examples](https://nvlabs.github.io/FoundationStereo/static/images/intro.jpg)

*Compare stereo input with reconstructed depth; fine geometry near discontinuities is worth checking.* [Official figure source](https://nvlabs.github.io/FoundationStereo/)

## How it works

The published network combines fine local CNN features with monocular cues adapted from DepthAnythingV2. Its hybrid cost volume represents possible left-right matches. Attentive filtering aggregates context over image locations and disparity. A recurrent update stage then refines the disparity, using cost and correlation features at each estimate.

### Component interfaces

| Component | Input | Output |
|---|---|---|
| Feature extraction | Rectified left and right RGB images | CNN and monocular-prior features |
| Matching and refinement | Left and right features | Dense disparity in image coordinates |
| Projection | Disparity and stereo calibration | Metric depth or point cloud |

## A practical workflow

Capture calibrated stereo images of a bin with matte, glossy and transparent objects. Convert disparity to depth, project points into 3D and compare them with known object distances. Evaluate depth around object boundaries separately from background pixels.

## What to verify

Keep camera calibration and baseline fixed when comparing models. Measure valid depth coverage, error by distance, and latency at the deployment image size. Benchmark results depend on dataset and hardware.

## License and availability

Research code has non-commercial restrictions; check separately distributed commercial models. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Research architecture and benchmark examples](https://nvlabs.github.io/FoundationStereo/)
- [Related official resource · github.com](https://github.com/NVlabs/FoundationStereo)
