# OSMO

[Catalog](../../README.md) · [한국어](../ko/osmo.md)

An orchestration system for GPU-backed simulation and training workflows.

**Official sources:** [Repository](https://github.com/NVIDIA/OSMO)

**License and access:** Apache-2.0. Models, data, dependencies and hosted services may have separate terms; check each source before use.

![OSMO workflow overview](https://media.githubusercontent.com/media/NVIDIA/OSMO/main/docs/front_cover.png)

Image source: [OSMO](https://github.com/NVIDIA/OSMO)

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Define workflow and resources"]
  S1["schedule tasks"]
  S2["run on available infrastructure"]
  S3["collect results"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Coordinate multi-stage robotics simulation and training jobs.

## Related technologies

Isaac Sim, Isaac Lab, Cosmos Data Factory. Confirm compatibility and runtime requirements in the documentation for each version.
