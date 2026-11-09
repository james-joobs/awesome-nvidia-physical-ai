# NVIDIA DRIVE

[← All projects](../../README.md) · [한국어](../ko/nvidia-drive.md)

## Overview

Autonomous-driving hardware and software platform.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Prepare driving software and models"] --> n1
    n1["develop on DRIVE platform"] --> n2
    n2["validate for the target vehicle"]
```

## Workflow and use

Prepare driving software and models → develop on DRIVE platform → validate for the target vehicle. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** developing autonomous driving software. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** Alpamayo, AlpaSim.

## Architecture and example

DRIVE AGX provides automotive compute hardware; the DRIVE OS SDK supplies the system software and interfaces used to develop and test automotive AI workloads.

Integrate and evaluate a vehicle sensor-processing stack on a DRIVE AGX developer kit before vehicle-level validation.

[Official technical source](https://developer.nvidia.com/DRIVE)

## Availability and terms

Product/platform; check component terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[Official page](https://developer.nvidia.com/drive)
