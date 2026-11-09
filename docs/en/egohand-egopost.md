# EgoHand / EgoPost

[← All projects](../../README.md) · [한국어](../ko/egohand-egopost.md)

## Overview

Capture components for egocentric hand and camera motion.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Capture egocentric observations"] --> n1
    n1["estimate hand and camera motion"] --> n2
    n2["process for downstream retargeting"]
```

## Workflow and use

Capture egocentric observations → estimate hand and camera motion → process for downstream retargeting. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** recording hand movement for robot demonstrations. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** Isaac Capture.

## Architecture and practical details

The Ego Pipeline captures egocentric observations and post-processes them to reconstruct hand and camera poses. An example is capturing a person manipulating an object without a robot in the loop, then inspecting the reconstructed motion before any downstream retargeting. The capture device, reconstruction components and their licenses are separate concerns.

[Official documentation](https://github.com/NVIDIA/IsaacCapture)

![EgoHand pipeline](https://raw.githubusercontent.com/NVIDIA/IsaacCapture/main/docs/source/_static/egohand-pipeline.svg)

*Image source: [Official repository](https://github.com/NVIDIA/IsaacCapture)*

## Availability and terms

EgoPost uses OpenMDW-1.1; EgoHand's independent license is unverified. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[Isaac Capture](https://github.com/NVIDIA/IsaacCapture)
