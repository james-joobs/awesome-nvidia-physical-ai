# SimReady Central Library

[Catalog](../../README.md) · [한국어](../ko/simready-central-library.md)

A browser for discovering indexed simulation-ready assets hosted by NVIDIA and other owners.

**Official sources:** [Hugging Face Space](https://huggingface.co/spaces/nvidia/simready-central) · [Documentation](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html)

**License and access:** Public browsing; each asset has its own license. Accepted assets can include non-commercial terms. Models, data, dependencies and hosted services may have separate terms; check each source before use.

**Architecture.** Assets remain hosted by their owners; accepted registrations are indexed for discovery through the library. Each asset card determines its own usage conditions. [Official documentation](https://docs.omniverse.nvidia.com/simready/latest/simready-central.html).

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Search the library"]
  S1["inspect asset card and terms"]
  S2["obtain asset from its owner"]
  S3["integrate and validate"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Find suitable objects and scenes for a robot simulation environment.

## Related technologies

SimReady Foundation, OpenUSD, Hugging Face. Confirm compatibility and runtime requirements in the documentation for each version.
