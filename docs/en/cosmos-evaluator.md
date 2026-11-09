# Cosmos Evaluator

[Catalog](../../README.md) · [한국어](../ko/cosmos-evaluator.md)

A framework for evaluating generated video with checks for physical plausibility and visual fidelity.

**Official sources:** [Repository](https://github.com/NVIDIA/cosmos-evaluator)

**License and access:** Apache-2.0; model terms vary by checker. Models, data, dependencies and hosted services may have separate terms; check each source before use.

![Cosmos Evaluator architecture diagram](https://raw.githubusercontent.com/NVIDIA/cosmos-evaluator/main/docs/assets/architecture_diagram.png)

Image source: [Cosmos Evaluator](https://github.com/NVIDIA/cosmos-evaluator)

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Choose generated video and criteria"]
  S1["run suitable checkers"]
  S2["inspect results"]
  S3["refine data"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Screen synthetic driving or manipulation videos before adding them to training data.

## Related technologies

Cosmos Data Factory, Cosmos generation models. Confirm compatibility and runtime requirements in the documentation for each version.
