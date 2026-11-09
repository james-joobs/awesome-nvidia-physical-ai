# CDF Auto Labeling (formerly paidf-auto-labeling)

[Catalog](../../README.md) · [한국어](../ko/cdf-auto-labeling.md)

CDF Auto Labeling composes annotation tasks over images and videos. Its runner executes selected stage services in a defined order over a shared scene directory.

## Read the official architecture

![NVIDIA CDF Auto Labeling workspace architecture](https://raw.githubusercontent.com/NVIDIA/cdf-auto-labeling/main/docs/assets/architecture_diagram_cdf_ual.png)

The runner calls services that wrap task packages. Detection and tracking, captioning, visual QA, grounding and training export each read or write artifacts according to the scene contract. A JSONL DataEntry identifies the sample by id, its media by media_path and its DAFT scene directory by data_path. The scene can preserve source media in sidecars/raw.<ext> and pass transformed media between stages through sidecars/active.<ext>. [Services overview](https://github.com/NVIDIA/cdf-auto-labeling/blob/main/docs/developer/architecture/services-overview.md) · [Artifact contract](https://github.com/NVIDIA/cdf-auto-labeling/blob/main/docs/developer/architecture/artifact-contract.md)

```json
{"id":"warehouse-clip-17","media_path":"/data/clip17.mp4","data_path":"/output/warehouse-clip-17"}
```

The illustrative record connects one source to the directory where stages exchange outputs. The selected services determine which annotations appear.

## Worked example — forklift tracks

Run detection and tracking over two forklifts passing each other. Add grounding or captioning if the downstream task needs it, then run training export. Inspect overlap frames for swapped track IDs. If a stage transformed the media, verify coordinates and frame timestamps against the active video before merging batches. [Official quick start](https://github.com/NVIDIA/cdf-auto-labeling#quick-start)

Code is Apache-2.0. Models, endpoints and dependencies have separate conditions. [License and redistribution](https://github.com/NVIDIA/cdf-auto-labeling#license-and-contributions)
