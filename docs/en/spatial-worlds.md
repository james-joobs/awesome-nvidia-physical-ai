# Choose a 3D world generation and rendering workflow

[한국어](../ko/spatial-worlds.md) · [Catalog](../../CATALOG.md)

## What kind of world do you need?

A camera-controlled video and an explorable 3D scene are different outputs. Start by deciding whether you need new pixels, a persistent radiance field, editable geometry, or a world with collision and dynamics.

| Input and method | Output | What the next application can do |
|---|---|---|
| Text/image → generative 3D model | Gaussian scene; sometimes a mesh or collider | Render unseen viewpoints; import supported representations into another application |
| Calibrated photos → 3DGS reconstruction | Centers, scales, rotations, opacity and color | Re-render a measured space near captured views |
| Seed + procedural rules → scene generator | Meshes, materials, lights and cameras | Edit geometry, export assets, add physics and create datasets |
| State + controls → driving simulator | Next state, sensor frames and event records | Test controls in a closed loop and record ego views |
| Image + camera actions → video model | A time sequence of RGB images | Inspect generated visual motion; a reusable 3D asset is not implied |

**Our working path:** [CARLA ego-camera simulation](labs/carla-ego.md) → [known views → fVDB 3DGS → interactive Spark viewer](labs/spatial-reconstruction.md). A separate [Infinigen house tour](labs/scene-generation.md) shows actual generated geometry. [Cosmos video generation](labs/world-driving.md) remains available as a different output type.

## Compare the tools and their data boundaries

### Generative 3D worlds

**World Labs Marble** accepts prompts and visual inputs to produce explorable worlds. Its export documentation describes SPZ/PLY splats and separate mesh/collider options. Hosted generation is not a local open-source model. Free generation and export rights are separate; current exports require paid plans. We did not call a paid API or generate a Marble world in this run. **Spark**, the open-source World Labs renderer, is what our site uses to display our own fVDB result. [Marble export](https://docs.worldlabs.ai/marble/export/gaussian-splat/index) · [File specifications](https://docs.worldlabs.ai/marble/export/specs) · [Spark source / MIT](https://github.com/sparkjsdev/spark)

**NVIDIA Lyra 1.0** combines generated multiview video information and a Gaussian decoder to output 3D/4D scenes. Its model card lists the NVIDIA Open Model License. **Lyra 2.0** adds long-horizon, 3D-consistent world exploration and reconstruction; its model weights instead use the NVIDIA Internal Scientific Research and Development Model License. Both implementations are public Apache-2.0 code. Do not transfer one version's weight license to the other. The official Lyra 2 setup was tested on H100 hardware; neither version was executed in this OMEN update. [Lyra source](https://github.com/nv-tlabs/lyra) · [Lyra 1 model card](https://huggingface.co/nvidia/Lyra) · [Lyra 2 code and model terms](https://github.com/nv-tlabs/lyra/tree/9fffc9adc37004091ecf26ef03abfb3abdf4d59a/Lyra-2)

**WorldGen** offers a lighter text/image → panorama → depth → splat/mesh workflow. Its code is Apache-2.0, but the FLUX dependencies have separate model terms. On OMEN, the official `FLUX.1-dev` and `FLUX.1-Fill-dev` repositories returned authenticated **403 access denied**. We cloned and inspected the source; we did not run complete generation. Once those model licenses/access requests are approved in the server account, use the author's pinned Python/CUDA instructions in a dedicated environment. [WorldGen](https://github.com/ZiYang-xie/WorldGen) · [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) · [FLUX.1-Fill-dev](https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev)

### Measured reconstruction and editable geometry

**fVDB Reality Capture** optimizes a radiance field from posed images. In our run, known CARLA cameras and training-view depth seed the Gaussians; there is no prompt-driven scene invention. **SHARP** infers nearby-view Gaussians from one image, with greater uncertainty in hidden regions. SHARP's code uses Apple's custom software license and its weights permit noncommercial research. **Infinigen** creates meshes, materials and room layouts with procedural rules. It is not a neural foundation model. Its BSD-3-Clause code and the Blender/asset dependencies have separate scopes. [fVDB](https://github.com/openvdb/fvdb-reality-capture) · [SHARP licenses](https://github.com/apple-aiml-research/ml-sharp) · [Infinigen](https://github.com/princeton-vl/infinigen)

## Run status and practical limits

Verified on **2026-11-20**. “Executed” means our own run and saved artifacts, not a replay of the author's promotional video.

| Tool | OMEN status | Available result |
|---|---|---|
| CARLA 0.9.16 / UE4.26 | Executed on RTX 5090 | Four ego-camera environments, chase originals and trajectories |
| fVDB Reality Capture 0.6.0 | Executed on RTX 5090 | 72-view dataset, full PLY, 3DGS video, 6.15 MB browser preview |
| Apple SHARP | Executed on RTX 5090 | Two single-image reconstructions and nearby-view recordings |
| Infinigen / Blender | Scene generation and CPU Cycles render | Furnished house, saved `.blend`, camera path and tour recording |
| Spark 2.4.0 | Integrated into the site | Click-to-load WebGL2 viewer; rendering uses the visitor's device |
| WorldGen | Source inspected; gated weights returned 403 | Setup follow-up recorded; no generated output claimed |
| NVIDIA Lyra 1 / 2 | Official sources and licenses checked | Reference workflow; not executed in this update |
| World Labs Marble | Hosted reference | No account, payment or API job started |

WonderWorld's official installation calls for 48 GB GPU memory, above OMEN's single 32 GB GPU. HunyuanWorld 1.0's community license excludes South Korea, so it was not selected for this run. These are concrete selection limits, not a comparison of visual quality. [WonderWorld](https://github.com/KovenYu/WonderWorld) · [HunyuanWorld 1.0 license](https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0/blob/main/LICENSE)

## Continue with an experiment

1. [Drive in CARLA](labs/carla-ego.md): understand frames, synchronous ticks and ego-camera placement.
2. [Reconstruct the plaza](labs/spatial-reconstruction.md): read intrinsics, coordinate transforms, Gaussians and a held-out-view check.
3. [Generate a house](labs/scene-generation.md): inspect meshes, materials and a camera path through real geometry.
4. [Inspect a model's proposed driving trajectory](labs/world-driving.md), then [evaluate a driving policy with AlpaSim](workflows/alpasim-closed-loop.md).

Rendering a convincing scene does not supply a collision mesh or prove physical validity. Carry scale, coordinates and licensing metadata with the scene when connecting these tools. [fVDB input/output theory](fvdb-reality-capture.md) · [Media credits](../../site/public/showcase/SPATIAL-CREDITS.md).
