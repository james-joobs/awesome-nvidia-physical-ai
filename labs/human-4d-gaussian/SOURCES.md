# Sources and usage scope

The lab has two distinct inputs. The **public control** uses licensed SOMA example motion and a synthetic neutral body. The **monocular pipeline** uses a local video supplied by the learner. Neither route includes a YouTube video downloader.

## Reference footage

- Original: [체포하겠어🚨🚨 — YouTube Shorts](https://www.youtube.com/shorts/rWS8uli1-m0).
- Publisher: [지숭이_Jisoong](https://www.youtube.com/@%EC%A7%80%EC%88%AD%EC%9D%B4_Jisoo).
- Attribution metadata was obtained from YouTube's official oEmbed endpoint.
- Pages links to the official YouTube player. The referenced performer's downloaded video and audio are not included in public assets. The project maintainer confirmed permission to publish the 3D/4D derivative results on 2026-11-25; those results are provided separately from the synthetic control.
- An attribution link is not a redistribution license for footage or a derived identifiable-person model.

## Public synthetic control

See [CONTROL-SOURCES.md](CONTROL-SOURCES.md) for exact inputs, transformations, hashes and rebuild commands. The builder accepts only the pinned official SOMA example motion hash. Its reference RGB and Gaussian rendering depict the same synthetic neutral geometry. They are not reconstructions of the YouTube performer.

## Reconstruction tools and checkpoints

| Component | Role | Official source and terms |
|---|---|---|
| NVIDIA GEM-X | Whole-body/hand motion estimation | [Code](https://github.com/NVlabs/GEM-X), Apache-2.0 with documented per-file OpenMDW exceptions; [weights](https://huggingface.co/nvidia/GEM-X), NVIDIA Open Model License. Read the upstream release's license files. |
| NVIDIA SOMA-X / py-soma-x 0.3.3 | Native human geometry, skinning matrices, body/hand conventions | [Code](https://github.com/NVlabs/SOMA-X), [native assets](https://huggingface.co/nvidia/SOMA-X), Apache-2.0. This preset does not require separately licensed SMPL-X or MHR assets. |
| NVIDIA Warp | Actual native SOMA skinning runtime | [Code](https://github.com/NVIDIA/warp), Apache-2.0. |
| SAM 2.1 large | Predicted source-person masks | [Code](https://github.com/facebookresearch/sam2), [checkpoint](https://huggingface.co/facebook/sam2.1-hiera-large), Apache-2.0. |
| 4DAnyone base | Pose-conditioned multiview video generation and native 4DGS implementation | [Code](https://github.com/ant-research/4DAnyone), [model/license table](https://huggingface.co/AntResearch/4DAnyone/blob/4c80e87b805a5f8461cf339cdbe2fb4249e585aa/LICENSE.md). Base model, VAE and context are Apache-2.0. Separate included components retain their terms. |
| 4DAnyone Turbo adapter | Seed offset views and both later-interval generation passes | Same model repository; the Rank64 Turbo LoRA has **CC BY-NC-SA 4.0** terms, unlike the base weights. This workflow is not an unrestricted commercial-asset recipe. |
| Goliath/Sapiens2 conventions | Public keypoint-conditioning renderer/schema used by the SOMA adapter | Consult the Sapiens2 entry in the [official 4DAnyone model license table](https://huggingface.co/AntResearch/4DAnyone/blob/4c80e87b805a5f8461cf339cdbe2fb4249e585aa/LICENSE.md). No claim that these third-party conventions are NVIDIA assets. |
| BiRefNet | Generated-view foreground masks | [Code](https://github.com/ZhengPeng7/BiRefNet), [model](https://huggingface.co/ZhengPeng7/BiRefNet), MIT. The model repository's Python implementation is executed only in the configured isolated reconstruction environment. |
| MatConvNet VGG-19 convolution features | Frozen perceptual objective for original-resolution crops | Distributed by the pinned 4DAnyone reconstruction asset downloader; see its model license table, CC BY 4.0 asset entry. This loss is not standard LPIPS. |
| MoGe-3 ViT-L | RGB-inferred depth and normals | [Code](https://github.com/microsoft/MoGe), [weights](https://huggingface.co/Ruicheng/moge-3-vitl), MIT. FlexGEMM/Triton are separate dependencies. |
| gsplat | Differentiable Gaussian rasterization | [Official code](https://github.com/nerfstudio-project/gsplat), Apache-2.0. |
| Spark / Three.js | Browser rendering | [Spark](https://github.com/sparkjsdev/spark), [Three.js](https://github.com/mrdoob/three.js), MIT. |

Pinned revisions are recorded in [model-pins.json](model-pins.json). Install required checkpoints into the chosen output root and configure their paths in `runtime.json`. Setup does not accept license terms on someone else's behalf or silently substitute missing assets.

## Output interpretation

Source pixels are observed. GEM-X/SOMA motion, masks, cameras, depth and normals are estimated. Unobserved appearance is generated. Agreement with MoGe guidance is not measured real-world geometry accuracy. The recommended full-motion `extend` route generates twelve new view videos per later interval using two Turbo4 passes, unlike the seed’s Base24-plus-Turbo recipe. Generated video count, accepted synthetic targets, independent observed cameras and repeated loss-weighting slots are distinct counts. Explicit teacher curation may retain fewer generated directions. The separate `--trajectory-experiment` comparison transfers short-interval appearance without new later-interval multiview diffusion.

The independent adapters in this folder follow the repository's MIT license. Third-party code/assets and input-footage rights remain separate. `package` for the monocular route creates a private local package. The separate `publish_package.py` exporter requires a local derivative-publication permission receipt, excludes source RGB/audio and exports only a reduced browser model with sanitized metadata. Runtime paths, training checkpoints, model caches and source logs are not published.

## Published dance reconstruction

Source credit: **지숭이_Jisoong — 체포하겠어🚨🚨**, [official YouTube Shorts](https://www.youtube.com/shorts/rWS8uli1-m0). Permission for public3D/4D derivative results was confirmed by the project maintainer on 2026-11-25. Original RGB/audio stay in the official YouTube player. Permission details are retained privately; this statement does not grant a blanket license for further redistribution of the person model or footage. Third-party tool and model terms in the table above continue to apply. In particular, the Turbo adapter weights have CC BY-NC-SA4.0 terms; this is not an unrestricted commercial-asset recipe.

The published31.9s native orbit video retains the full selected trained model. The browser representation is a reduced subset capped at400000 Gaussians per segment, preserving the parameters of retained points; it is not pixel-identical to the full model. Separate earlier rigged3DGS four-view footage is preserved as a comparison. No original-video panels or source audio are present in either hosted clip.
