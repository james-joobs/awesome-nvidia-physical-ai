# CDF Augmentation (formerly paidf-augmentation)

[Catalog](../../README.md) · [한국어](../ko/cdf-augmentation.md)

CDF Augmentation is a YAML-driven client for transforming image, video and text. Generation and optional captioning run through HTTP endpoints named in the configuration. Model weights reside on the inference server.

## Read the official pipeline

![NVIDIA CDF Augmentation pipeline](https://raw.githubusercontent.com/NVIDIA/cdf-augmentation/main/docs/Augmentation_v1.1.0.png)

Follow the media and prompt into the endpoint call and the candidate into verification. A quality rejection can trigger another attempt with a changed seed. An external service failure is handled separately. [Pipeline and adapters](https://github.com/NVIDIA/cdf-augmentation#pipeline-flow)

| Layer | What to configure |
|---|---|
| Source | Image, video or text and one YAML run configuration |
| Prompt | Fixed text, filled template, prompt file or optional model-generated caption |
| Adapter | Transport and role, for example NIM /v1/infer or OpenAI-compatible video |
| Gate | Optional motion comparison, attribute verification or a Cosmos Evaluator Arbitrator endpoint |

## Worked example — change weather while retaining actor motion

Generate weather variants of a clip with a known pedestrian track. Record the endpoint revision and per-candidate seed. Check requested weather and compare tracks, occlusions and event timing to the source. Review or recompute labels if the generated actor moves differently. An endpoint can be remote or self-hosted, while local H.264 decode and certain alignment stages have their own GPU requirements. [Official configuration cookbook](https://github.com/NVIDIA/cdf-augmentation/tree/main/configs/cookbook) · [Runtime requirements](https://github.com/NVIDIA/cdf-augmentation#requirements)

Repository code is Apache-2.0. Verify selected model and service terms. [Official repository](https://github.com/NVIDIA/cdf-augmentation)
