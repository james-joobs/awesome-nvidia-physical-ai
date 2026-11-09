# SimReady

[Catalog](../../README.md) · [한국어](../ko/simready.md)

SimReady describes specifications and practices for 3D assets prepared for physically based simulation. Assets can combine geometry and appearance with properties such as collision, physical materials and semantic information; the requirements depend on the selected asset profile. It is a set of specifications and an ecosystem rather than one software library.

**Official documentation:** [SimReady overview](https://docs.omniverse.nvidia.com/simready/latest/index.html) · [SimReady Central](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html) · [SimReady Foundation](https://github.com/NVIDIA/simready-foundation)

**Access and licenses:** Specifications, code and individual assets have separate terms. NVIDIA-authored Foundation content is Apache-2.0; third-party assets can have different terms, including non-commercial restrictions. Check the asset card and the actual files before use.

![An example SimReady object](https://media.githubusercontent.com/media/NVIDIA/simready-foundation/main/nv_core/cip_specs/isaac_asset_transformer/tests/fixtures/prop_physx_toolbox/simready_usd/.thumbs/sm_obs_electricians_large_tool_box_a01_01_thumbnail.png)

Image source: [NVIDIA SimReady Foundation](https://github.com/NVIDIA/simready-foundation).

## Components and workflow

[SimReady Foundation](simready-foundation.md) provides asset profiles, specifications and validation tools. [SimReady Central Library](simready-central-library.md) makes registered assets discoverable; asset owners continue to host the packages. OpenUSD describes and composes the resulting scenes.

The following is a conceptual workflow; the exact validation steps depend on the asset profile.

```mermaid
flowchart LR
  A["Find or author 3D asset"] --> B["Add simulation properties"] --> C["Validate against profile"] --> D["Compose scene in OpenUSD"] --> E["Simulate and evaluate"]
```

## Use case

For a warehouse robot, select assets for shelving, pallets and equipment, verify their licenses and physical properties, then compose the scene in Isaac Sim. Validate collisions and sensor behavior before using the environment for testing or synthetic data generation.

## Related technologies

OpenUSD, Isaac Sim, Omniverse, SimReady Foundation and SimReady Central Library. Each project and asset has its own requirements and terms.
