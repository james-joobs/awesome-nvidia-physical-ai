# SimReady Foundation

[Catalog](../../README.md) · [한국어](../ko/simready-foundation.md)

An NVIDIA-authored collection of OpenUSD asset profiles, specifications, validation tools and sample content.

**Official sources:** [GitHub](https://github.com/NVIDIA/simready-foundation)

**License and access:** NVIDIA-authored content Apache-2.0; third-party assets have their own licenses. Models, data, dependencies and hosted services may have separate terms; check each source before use.

![SimReady sample object](https://media.githubusercontent.com/media/NVIDIA/simready-foundation/main/nv_core/cip_specs/isaac_asset_transformer/tests/fixtures/prop_physx_toolbox/simready_usd/.thumbs/sm_obs_electricians_large_tool_box_a01_01_thumbnail.png)

Image source: [SimReady Foundation](https://github.com/NVIDIA/simready-foundation)

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Choose asset profile"]
  S1["author or import asset"]
  S2["validate required properties"]
  S3["use in a simulation scene"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Prepare reusable objects with simulation-relevant physical and semantic properties.

## Related technologies

SimReady, OpenUSD, Isaac Sim, SimReady Central. Confirm compatibility and runtime requirements in the documentation for each version.
