# Cosmos and Cosmos 3

[← All projects](../../README.md) · [한국어](../ko/cosmos.md)

![Cosmos world scenario transfer example](https://raw.githubusercontent.com/NVIDIA/cosmos/main/assets/demos/transfer_worldscenario.gif)

Image: official project source linked below.

## Overview

World-model and tooling platform and model family.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Select a world-model task"] --> n1
    n1["prepare prompts or video"] --> n2
    n2["generate or reason"] --> n3
    n3["evaluate outputs"]
```

## Workflow and use

Select a world-model task → prepare prompts or video → generate or reason → evaluate outputs. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** synthetic physical scenarios. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** Cosmos Predict, Transfer, Reason, Cosmos Curator.

## Architecture and example

Cosmos 3 uses a mixture-of-transformers architecture combining autoregressive reasoning and diffusion generation. The broader platform also includes curation and evaluation tools; model versions and their inputs differ.

For example, build a rare driving scenario from available context, generate a candidate video, and review its physical plausibility before using it in a dataset.

[Official technical source](https://github.com/NVIDIA/cosmos)

## Availability and terms

The [Cosmos repository](https://github.com/NVIDIA/cosmos) specifies OpenMDW-1.1 for its code and models; it is not assumed to be OSI-approved. Other repositories have their own terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[Repository](https://github.com/NVIDIA/cosmos)
