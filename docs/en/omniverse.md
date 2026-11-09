# NVIDIA Omniverse

[← All projects](../../README.md) · [한국어](../ko/omniverse.md)

## Overview

OpenUSD-based 3D development platform.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Compose OpenUSD assets and scenes"] --> n1
    n1["connect simulation applications"] --> n2
    n2["build and iterate digital twins"]
```

## Workflow and use

Compose OpenUSD assets and scenes → connect simulation applications → build and iterate digital twins. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** a digital twin of a factory. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** OpenUSD, Isaac Sim, SimReady.

## Architecture and example

Omniverse Kit provides an application framework built from extensions; OpenUSD is used to compose and exchange scene data across compatible applications.

Compose factory geometry and equipment into a shared scene, then connect a simulator to evaluate a robot workflow.

[Official technical source](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/kit_architecture.html)

## Availability and terms

Product, SDK, and publicly available components have different terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[Official page](https://developer.nvidia.com/omniverse)
