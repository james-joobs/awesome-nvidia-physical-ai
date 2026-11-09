# CDF Augmentation (formerly paidf-augmentation)

[Catalog](../../README.md) · [한국어](../ko/cdf-augmentation.md)

Tools for generating visual and text variations from existing data using model-backed workflows.

**Official sources:** [Repository](https://github.com/NVIDIA/cdf-augmentation)

**License and access:** Apache-2.0; models have separate terms. Models, data, dependencies and hosted services may have separate terms; check each source before use.

![CDF Augmentation (formerly paidf-augmentation) official example](https://raw.githubusercontent.com/NVIDIA/cdf-augmentation/main/docs/Augmentation_v1.1.0.png)

Image source: [CDF Augmentation (formerly paidf-augmentation)](https://github.com/NVIDIA/cdf-augmentation)

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Prepare inputs"]
  S1["choose transformation and model"]
  S2["generate variants"]
  S3["inspect consistency"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Expand weather, lighting or appearance coverage where capturing new examples is costly.

## Related technologies

Cosmos Data Factory, Cosmos models, Cosmos Evaluator. Confirm compatibility and runtime requirements in the documentation for each version.
