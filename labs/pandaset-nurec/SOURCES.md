# Sources and separate asset rights

Code in this repository follows the repository license. It does not relicense input datasets, model weights, car meshes or rendered media.

| Asset | Primary evidence | Observed permission / handling |
| --- | --- | --- |
| PandaSet camera RGB, measured LiDAR and calibration | [Authors' paper](https://arxiv.org/abs/2112.12610), [original devkit](https://github.com/scaleapi/pandaset-devkit), [preserved original data terms](PANDASET-DATA-LICENSE.txt) | Payload `LICENSE.txt`: CC BY 4.0 plus PandaSet Dataset Terms, including privacy and no-endorsement restrictions. This is a data license, separate from the Apache-2.0 devkit. |
| Alternative first-party license label | [Scale Nucleus dataset notices](https://scale.com/legal/nucleus-os) | This page labels PandaSet CC BY-SA 4.0; the payload labels it CC BY 4.0. The notices differ. We retain the original terms and release our **newly created demo media** under CC BY-SA 4.0 to meet the stronger attribution/share-alike condition. This does not change upstream terms or claim that the notices are identical. |
| Download transport | [Community mirror](https://huggingface.co/datasets/georghess/pandaset/tree/e2e123aea3b3132c67f4b395ec6120f63e190271) | Unofficial mirror, unaffiliated with the creators. Original hosting referenced by the devkit was unavailable when checked. Revision pinned; individual ZIP CRC and size checked; per-file SHA-256 recorded. A range download does **not** verify the full 44.5 GB archive SHA-256. |
| Volvo S90 Recharge mesh | [lazercar's original model](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9), [license](https://creativecommons.org/licenses/by/4.0/), [asset receipt](../reality-view/ego-car.json) | CC BY 4.0. Author-provided Blender download; attribution, modified paint, orientation and rendering noted. Not supplied by Volvo; no manufacturer endorsement. |
| NuRec runtime | [NVIDIA documentation](https://docs.nvidia.com/nurec/), [source](https://github.com/NVIDIA/NuRec) | Runtime pinned to 26.04 in the reproduction commands. Dataset and render provenance are PandaSet, **not** NVIDIA PhysicalAI Autonomous Vehicles data. |

Attribution for demo media:

> PandaSet by Scale AI and Hesai. Volvo S90 Recharge (Free) by lazercar, CC BY 4.0. Reconstructed views, paint, coordinate alignment and rendering modified by the awesome-nvidia-physical-ai contributors. Demo media: CC BY-SA 4.0; original PandaSet Dataset Terms also apply.

Keep this attribution and the data terms with redistributed results. Do not use the footage to identify individuals or imply an affiliation with dataset creators or the vehicle manufacturer. No original full dataset, NVIDIA internal-use AV scene, model checkpoint or 1.2 GB car source archive is bundled here.

## Other real-data routes considered

| Dataset | Official terms | Why this prototype uses PandaSet instead |
| --- | --- | --- |
| [ZOD](https://zod.zenseact.com/) | [CC BY-SA 4.0 with privacy notices](https://zod.zenseact.com/license/) | Useful calibrated front-camera/LiDAR driving sequences. The official download currently requires an application/link; a six-camera surrounding view is available immediately from the selected PandaSet payload. |
| [Argoverse 2](https://www.argoverse.org/av2.html) | [CC BY-NC-SA 4.0](https://www.argoverse.org/about.html) | Calibrated surrounding cameras and LiDAR are publicly downloadable; the noncommercial condition is a less flexible fit for reusable promotional examples. |
| [Audi A2D2](https://www.a2d2.audi/a2d2/en/download.html) | CC BY-ND 4.0 | Public availability alone is insufficient. The no-derivatives condition does not provide a clear basis to distribute this reconstruction/enhancement demo, so it is not used. |
