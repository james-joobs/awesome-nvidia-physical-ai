# Spatial worlds and driving media / 3D 공간·주행 미디어 출처

Recorded or rendered on falconeyes-omen, 2026-11-20. These are our own executions, not downloaded promotional videos. Original takes, full models and intermediate files remain in `~/physical-ai-grid/spatial-worlds-2026-11-20/` on that server.

| Published files | Origin and modifications | Upstream terms |
|---|---|---|
| `carla-ego.mp4`, `carla-city-clear.*`, `carla-junction-rain.*`, `carla-suburb-sunset.*`, `carla-highway-fog.*` | CARLA Project Team: CARLA 0.9.16 built-in Town10HD, Town03, Town02 and Town04 maps and vehicles. Original ego RGB sensors with rule-based Traffic Manager. Resized, H.264 encoded and labeled; four takes combined into a grid. | [CARLA-specific assets: CC-BY, version not specified by the README](https://github.com/carla-simulator/carla/tree/0.9.16#licenses). [Source code: MIT](https://github.com/carla-simulator/carla/blob/0.9.16/LICENSE). Unreal Engine and dependencies retain separate terms. |
| `spatial-reconstruction.*`, `town03.spz`, `assets/lessons/spatial-worlds/reference-vs-render.webp` | CARLA Project Team's Town03 fountain plaza, captured in 72 posed RGB-D views. Reconstructed by us with fVDB Reality Capture; rendered into an MP4 and compressed into a browser model with every Gaussian and degree-1 color. Derived appearance and geometry retain the CARLA asset scope; no collision mesh is included. | CARLA asset credit and CC-BY scope above. [fVDB Reality Capture code: Apache-2.0](https://github.com/openvdb/fvdb-reality-capture). |
| `sharp-city.*`, `sharp-suburb.*` | Our CARLA-derived photographs processed by Apple SHARP. Actual 90° camera focal length supplied; nearby views rendered with fVDB. No SHARP weights or original full PLY predictions are redistributed. | CARLA asset scope above. [Apple software license](https://github.com/apple-aiml-research/ml-sharp/blob/aed6527499ef91cba3b54c18d49a870f25947190/LICENSE) and [Apple ML Research Model License](https://github.com/apple-aiml-research/ml-sharp/blob/aed6527499ef91cba3b54c18d49a870f25947190/LICENSE_MODEL): noncommercial research. These are research demonstration results, not production model permissions. |
| `scene-generation.*` | Princeton University's Infinigen, commit `53033dd55c7191cbc436be6ffbb63c026935a509`: house-tour example, seed 0, three rooms, planned camera motion. Blender Cycles CPU render, 16 samples and OpenImageDenoise. 48 views played at 8 FPS, one third of the 24 FPS timeline speed. | [Infinigen BSD-3-Clause](https://github.com/princeton-vl/infinigen/blob/53033dd55c7191cbc436be6ffbb63c026935a509/LICENSE). Blender and third-party materials retain their respective terms; no model weights are used. |

**Browser code:** [Spark 2.4.0 by World Labs (MIT)](https://github.com/sparkjsdev/spark) with [Three.js (MIT)](https://github.com/mrdoob/three.js). Spark is a renderer, not a redistribution of the Marble model. The browser SPZ is encoded locally with [PlayCanvas splat-transform 3.12.0 (MIT)](https://github.com/playcanvas/splat-transform), retaining all Gaussians and degree-1 color.

**Not executed:** NVIDIA Lyra and World Labs Marble remain documented reference alternatives. WorldGen was subsequently executed after both FLUX access approvals; see the results below.

한국어: 위 자료는 OMEN에서 직접 실행·촬영·렌더링했습니다. CARLA 에셋을 바탕으로 만든 영상·3DGS에는 원래 에셋의 출처와 이용 조건이 이어집니다. 코드는 공개되어 있어도 모델 가중치나 에셋의 조건은 다를 수 있습니다. 저장소의 MIT 라이선스로 이런 자료의 조건을 바꾸지 않습니다. 전체 원본·PLY·Blender 장면은 서버에 보관하며, 웹에는 가벼운 미리보기와 실습 코드를 제공합니다.


## WorldGen generated scenes · 2026-11-20

- `worldgen-scenes.mp4/.jpg`: text-to-scene robotics laboratory, seed 42.
- `worldgen-livingroom.mp4/.jpg`: image-to-scene expansion of our own Infinigen seed-0 house-tour frame 1. Synthetic image, known K; no external photograph. Original hash matches the Infinigen recording above.
- `worldgen-forest-trail.mp4/.jpg`: text-to-scene forest, seed 17. More visible holes/transparency than the interiors.
- `worldgen-{robot-lab,livingroom,forest-trail}.spz`: 320,000-Gaussian browser previews. Retain one in four source pixels and double tangent footprints. Videos use all 1,280,000 Gaussians; previews are explicitly reduced.

All videos are actual fVDB Reality Capture renders of our generated PLYs, 480 translated camera poses each, 960×540 at 24 FPS. They are not author demonstration footage or 2D panorama pans. Full PLY/mesh, distance arrays, inputs, original panoramas and generation logs remain on falconeyes-omen under `~/physical-ai-grid/worldgen-2026-11-20/`. The repository contains source, camera matrices, numeric samples, model revisions and media hashes in [the lab](../../../labs/worldgen-scenes/).

[WorldGen source / Apache-2.0](https://github.com/ZiYang-xie/WorldGen/blob/7ce7b2767fdf31e2727b69a2e61e2e950e3a017f/LICENSE) · [WorldGen LoRA card / Apache-2.0](https://huggingface.co/LeoXie/WorldGen) · [DA-2 / Apache-2.0](https://huggingface.co/haodongli/DA-2). FLUX.1-dev and FLUX.1-Fill-dev base/derived model weights have separate [FLUX.1-dev Non-Commercial terms](https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md); output usage is a distinct scope under those terms. No weights are redistributed. Browser rendering: [Spark / MIT](https://github.com/sparkjsdev/spark); compression: [splat-transform / MIT](https://github.com/playcanvas/splat-transform).

Known local changes: calibrated pinhole-to-panorama mapping for image conditioning; DA-2's native SDPA fallback for Blackwell; standard logit-opacity PLY export and finite pole scales. Geometry is inferred and normalized, not metric ground truth or a validated collision scene.
