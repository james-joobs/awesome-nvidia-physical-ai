# Sources and separate licenses

Checked 2026-11-23. Our pipeline code is MIT. It invokes third-party runtimes and models; this does not relicense their code, weights, data or assets.

| Component | Primary source / pinned version | Terms and use |
| --- | --- | --- |
| NuRec SDK | [NVIDIA/NuRec](https://github.com/NVIDIA/NuRec), [Apache-2.0 SDK license](https://github.com/NVIDIA/NuRec/blob/main/LICENSE.md) | Actual NuRec input, training, native rendering and official Gaussian export. This run uses the SDK's `experimental/3dgut/3dgut_colmap` preset. |
| NuRec runtime | [NGC NRE runtime](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nre/containers/nre-ga), 26.04 / runtime 26.4.149; image digest `97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284` | Binary runtime follows NGC distribution terms, separately from the Apache SDK. No container binaries are bundled in Git. |
| COLMAP | [3.13 API](https://colmap.github.io/legacy/3.13/pycolmap/index.html), pycolmap-cuda12 3.13.0 | BSD-3-Clause; RGB-only camera/point recovery and rig-constrained bundle adjustment. |
| NCore | [NVIDIA/ncore](https://github.com/NVIDIA/ncore) | Apache-2.0 format/API in the NuRec runtime. Only RGB-derived estimates are packaged; no LiDAR source component. |
| Harmonizer | [NVIDIA source](https://github.com/NVIDIA/harmonizer), [model](https://huggingface.co/nvidia/Harmonizer), revision `20ca33d4612b1e98e0526b3a7ee604af5b289f58` | Released `harmonizer_nontemporal.pt`, SHA-256 `ece8e2daa914e8c2a027a2da94e0eb2064491d5b3fd8514009fae9a442e06e90`. Weights under NVIDIA Open Model License; obtained separately. **Built on NVIDIA Cosmos.** Frame-independent enhancement, not a new 3D reconstruction. |
| Alpamayo 2 Edge | [NVlabs/alpamayo2-edge](https://github.com/NVlabs/alpamayo2-edge/tree/02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e), [weights](https://huggingface.co/nvidia/Alpamayo2-Edge/tree/b92b6aa326bd3e2235db28f248ad5a30b5890e64) | Apache-2.0 code; [OpenMDW-1.1 weights](https://huggingface.co/nvidia/Alpamayo2-Edge/blob/b92b6aa326bd3e2235db28f248ad5a30b5890e64/LICENSE). Shards checked against pinned SHA-256 values. No weights bundled. Source RGB + derived history, no NVIDIA AV Dataset assets. |
| RGB object perception | [TorchVision 0.23 Mask R-CNN](https://docs.pytorch.org/vision/0.23/models/generated/torchvision.models.detection.maskrcnn_resnet50_fpn_v2.html), [source license](https://github.com/pytorch/vision/blob/v0.23.0/LICENSE) | BSD-3-Clause source. Public COCO_V1 weights; a separate model-specific weights license is not explicitly stated on the model page. The source license does not replace training-data rights. See [checkpoint provenance](../rgb-reality-view/SOURCES.md). |
| Browser preview | [Spark](https://github.com/sparkjsdev/spark) 2.4.0, [Three.js](https://github.com/mrdoob/three.js) 0.187.0, [splat-transform](https://github.com/playcanvas/splat-transform) 3.12.0 | MIT. NuRec exports its Gaussians in 3DGS format; SPZ retains the Gaussians with degree-1 color. Third-party rasterization and compression can differ from native NuRec. |
| NuRec metric dependency | [Official TorchVision AlexNet checkpoint](https://download.pytorch.org/models/alexnet-owt-7be5be79.pth) | Public upstream dependency cached before offline container execution, SHA-256 `7be5be791159472b1fbf3c69796f7cb30dca7ad8466c2df70058c37116cdee02`. No checkpoint bundled; source/training-data terms remain separate. |

## Example data and vehicle

PandaSet is by **Scale AI and Hesai**: [author paper](https://arxiv.org/abs/2112.12610), [official devkit](https://github.com/scaleapi/pandaset-devkit). The JPEG-only downloader uses the same pinned **unofficial community mirror** as the [RGB comparison lab](../rgb-reality-view/SOURCES.md). Only camera pixels and the original license are fetched. Matching frame numbers define nominal times; no sensor timestamp, pose or calibration files are read.

The original payload says **CC BY 4.0 + PandaSet Dataset Terms**; [Scale's Nucleus notice](https://scale.com/legal/nucleus-os) has also identified PandaSet as CC BY-SA 4.0. We retain both notices and apply **CC BY-SA 4.0 + original Dataset Terms** to the new scene, resized RGB previews and annotated recordings. Do not imply endorsement or identify individuals. The devkit's Apache license is not the data license. [Original data terms](evidence/PANDASET-DATA-LICENSE.txt).

**Volvo S90 Recharge (Free)** by **[lazercar](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9)**, CC BY 4.0. Geometry/materials/axes are simplified and the GLB is meshopt-compressed. It is a separate foreground reference with a display shadow, not the capture vehicle or an OEM dynamics model. [Vehicle provenance and modifications](../rgb-reality-view/SOURCES.md).

## Presentation and measured scope

The ego-centered road-user presentation refers to [Tesla's official visualization documentation](https://www.tesla.com/ownersmanual/modely/en_us/GUID-2CB60804-9CEA-4F4B-8B04-09B991368DC5.html). That source does not establish the internal architecture of the newly discussed Reality View. No Tesla source, proprietary model or driving system is reproduced or endorsed here.

The scene is static, and moving traffic can ghost. Novel views can expose gaps; Harmonizer may fill or alter details and flicker across frames. Perception uses original RGB, not generated enhancements. Its scores are model predictions, not verified accuracy. Ground contacts assume one RGB-derived road plane.

Alpamayo uses a disclosed virtual-camera adapter, nominal source timing, planar/smoothed RGB-derived ego history and an assumed metric scale. It runs open-loop on four keyframes and does not actuate or evaluate a vehicle. Generated explanations may be incorrect. Separate stage receipts, frame-pair hashes, output shapes, artifact hashes and browser interactions support execution/integrity, not driving safety or hidden-surface truth.
