# RTX / DGX Spark

[← All projects](../../README.md) · [한국어](../ko/rtx-dgx-spark.md)

## Overview

GPU product family / AI computer.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Select compute hardware"] --> n1
    n1["set up a compatible software stack"] --> n2
    n2["run AI development or simulation workloads"]
```

## Workflow and use

Select compute hardware → set up a compatible software stack → run AI development or simulation workloads. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** running simulation or model development workloads. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** CUDA, Isaac Sim, Cosmos.

## Architecture and example

RTX is a family of GPUs; DGX Spark is an AI development computer. Their supported software, memory and performance characteristics vary by model and workload.

Select hardware against the simulator or model requirements, then measure whether the specific workload fits its memory and performance budget.

[Official technical source](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)

## Availability and terms

Hardware products, not open-source projects. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[RTX](https://www.nvidia.com/en-us/geforce/graphics-cards/) · [DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)
