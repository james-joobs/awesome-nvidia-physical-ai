# SimReady Central

[Catalog](../../README.md) · [한국어](../ko/simready-central.md)

A submission and review index for owner-hosted Hugging Face simulation asset packages.

**Official sources:** [GitHub](https://github.com/NVIDIA-Omniverse/simready-central)

**License and access:** Public repository; submission onboarding and asset terms apply separately. Models, data, dependencies and hosted services may have separate terms; check each source before use.

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Prepare an owner-hosted package"]
  S1["submit registration"]
  S2["review"]
  S3["discover accepted assets in the library"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Make assets discoverable while preserving their original hosting and licensing.

## Related technologies

SimReady Central Library, Hugging Face, OpenUSD. Confirm compatibility and runtime requirements in the documentation for each version.
