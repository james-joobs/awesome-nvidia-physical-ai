# Sources, rights and reproducibility

Checked 2026-11-23. Code, scene data, car assets and tool dependencies have separate licenses. The repository's MIT license covers our pipeline code; it does not replace the following terms.

## Reconstruction and viewer tools

| Tool | Tested source/version | License / scope |
| --- | --- | --- |
| NVIDIA 3DGRUT / 3DGUT | [dfd3d54](https://github.com/nv-tlabs/3dgrut/tree/dfd3d54c8c612003fb7948443edf7778f2bcd5ec), 3DGUT COLMAP MCMC preset | [Apache 2.0](https://github.com/nv-tlabs/3dgrut/blob/dfd3d54c8c612003fb7948443edf7778f2bcd5ec/LICENSE); trained from RGB-derived COLMAP points, no downloaded neural-model checkpoint |
| COLMAP / pycolmap | [3.13 documentation](https://colmap.github.io/legacy/3.13/pycolmap/index.html), pycolmap-cuda12 3.13.0 | [BSD 3-Clause](https://github.com/colmap/colmap/blob/main/COPYING.txt); camera intrinsics, poses and sparse points estimated from RGB |
| nvidia-ncore | [NVIDIA/ncore](https://github.com/NVIDIA/ncore), 19.9.1 | Apache 2.0 in installed distribution metadata; a 3DGRUT dependency, no NCore sensor dataset is imported |
| SlangTorch | [shader-slang/slang-torch](https://github.com/shader-slang/slang-torch), 1.3.18 | [Apache 2.0 with LLVM exception](https://github.com/shader-slang/slang-torch/blob/main/LICENSE) |
| Spark | [sparkjsdev/spark](https://github.com/sparkjsdev/spark), 2.4.0 | MIT; interactive Gaussian rendering |
| Three.js | [mrdoob/three.js](https://github.com/mrdoob/three.js), 0.187.0 | MIT; orbit controls, mesh rendering, GLTF/meshopt loading |
| SPZ conversion | [PlayCanvas splat-transform](https://github.com/playcanvas/splat-transform), 3.12.0 | MIT; all 400,000 Gaussians retained, SH reduced from degree 3 to 1, SPZ version 3 |
| Mesh optimization | [glTF Transform](https://github.com/donmccurdy/glTF-Transform), CLI 4.2.1 / core 4.5.1 | MIT; meshopt compression and simplified geometry |

Other dependencies retain their upstream terms. Core Python pins are in [constraints.txt](constraints.txt); source commit, architecture and install commands are in [pipeline.py](pipeline.py). First-use compilation needs the CUDA development toolkit, not just the driver/runtime. CUDA 12.0 cannot build this Blackwell preset.

## RGB sample: PandaSet scene 001

- Original creators: **Scale AI and Hesai**. [Author paper](https://arxiv.org/abs/2112.12610) and [official devkit](https://github.com/scaleapi/pandaset-devkit). The devkit's Apache license is **not** the dataset license.
- Original website is unavailable; the example downloader uses the **unofficial community mirror** [georghess/pandaset](https://huggingface.co/datasets/georghess/pandaset), pinned to revision `e2e123aea3b3132c67f4b395ec6120f63e190271`.
- Only 162 camera JPEGs (six directions, every third frame) and the original license file are fetched. No supplied intrinsics, poses, timestamps, GPS, IMU, LiDAR, depth or annotations are downloaded. Fresh JPEGs discard EXIF and metadata before SfM.
- The archive's original [LICENSE.txt](evidence/PANDASET-DATA-LICENSE.txt) says **CC BY 4.0 plus PandaSet Dataset Terms**. [Scale's Nucleus notice](https://scale.com/legal/nucleus-os) has also identified PandaSet as **CC BY-SA 4.0**. These notices differ; we preserve the original terms and apply **CC BY-SA 4.0** to our new scene and recordings, with original Dataset Terms also applying. Do not identify people or imply endorsement.
- The remote ZIP index has a pinned archive size and LFS identity. Each fetched member is checked against ZIP CRC/size and gets a SHA-256 receipt. **The complete 44.5 GB archive hash was not verified**, because the downloader range-fetches only selected members. Receipts are in `evidence/download-result.json` and `evidence/input-manifest.json`.
- This example contains no NVIDIA AV Dataset assets. Private/internal-only NuRec scene data from earlier experiments is excluded.

## Added vehicle: Volvo S90 Recharge

- **[Volvo S90 Recharge (Free)](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9)** by **lazercar**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The author's model listing and [API metadata](https://api.sketchfab.com/v3/models/9462b07c10244fd4a28d86846dc9e3a9) identify the license. No manufacturer endorsement.
- Author's [source archive](https://drive.google.com/file/d/1Q9Zz8getrYY5AA1f8k72rapH2kCTXKD6/view), SHA-256 `222d57d4ad29b7bafecb9ef0ded813d60dbb03343a124fec90b235b3e22cf087`.
- Our export removes small trim, simplifies geometry/materials, normalizes axes, and creates a meshopt-compressed GLB (~0.95 MB). [export_vehicle.py](export_vehicle.py) describes the Blender conversion; [VEHICLE-LICENSE.txt](assets/VEHICLE-LICENSE.txt) documents optimization settings. The huge source archive is not vendored.
- The browser renders this **actual 3D mesh** in a separate foreground scene after the Gaussian scene, with a display shadow. It is a position reference, not the original collection vehicle, a metric alignment or an OEM physics model. Foreground compositing does not establish correct scene occlusion or collisions.

## Measured scope

The saved run connected 162/162 images in COLMAP, trained 16,000 iterations on **one RTX 5090**, and exported 400,000 Gaussians. All source images inform SfM. This is not an independent novel-view accuracy benchmark. The optional upstream end evaluator is disabled (`test_last=false`); the pipeline validates model completion and browser interactions separately.

The road plane is fitted only from triangulated RGB features in lower front-camera regions. Normalizing camera-to-road distance defines display units; it does not recover measured meters. Traffic is part of one static reconstruction and may appear duplicated or blurred. Far or unseen surfaces can have gaps. The videos show **actual recorded browser mouse interactions**, not a prerecorded scene sweep presented as interactivity.

## RGB object perception extension

- **TorchVision Mask R-CNN ResNet50 FPN v2, COCO_V1**, [official model page](https://docs.pytorch.org/vision/0.23/models/generated/torchvision.models.detection.maskrcnn_resnet50_fpn_v2.html), [versioned source](https://github.com/pytorch/vision/blob/v0.23.0/torchvision/models/detection/mask_rcnn.py), [BSD-3-Clause source license](https://github.com/pytorch/vision/blob/v0.23.0/LICENSE). Tested TorchVision 0.23.0 with PyTorch 2.8.0+cu128.
- Public [upstream checkpoint](https://download.pytorch.org/models/maskrcnn_resnet50_fpn_v2_coco-73cbd019.pth), SHA-256 `73cbd0190fcbe3ba339921fbce2c3a0b6bb9126c9a133c85e43a2a8e060a109e`. Checked before loading; downloaded to the user's local cache, **not bundled in Git**. No gated access is needed. The model page does not separately state a model-specific weights license: **publicly downloadable weights; separate weights terms not explicitly established here**. The BSD source license does not replace source training-data rights.
- Inputs are only the already reconstructed RGB images, RGB-derived camera estimates and RGB-derived road plane. No PandaSet object annotations, LiDAR, source calibration or sensor timestamps are read. Camera thumbnails are resized source RGB and retain the dataset attribution/terms above. New annotated recordings and masks retain the same CC BY-SA 4.0 + original PandaSet terms as the scene.
- Inspired by the ego-centered road-user presentation described in [Tesla's official manual](https://www.tesla.com/ownersmanual/modely/en_us/GUID-2CB60804-9CEA-4F4B-8B04-09B991368DC5.html). That source does not establish the internals of the newly discussed Reality View. This lab makes no claim of equivalence to Tesla's proprietary architecture, live system or driving behavior.
- Model scores are not calibrated correctness probabilities. 3D contact markers assume one road plane, use relative scale and omit unreliable intersections. Temporary associations can fragment or switch IDs. They do not prove 3D extent, identity, velocity, physical occlusion or control safety.
