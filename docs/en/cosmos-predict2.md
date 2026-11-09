# Cosmos Predict2 code

[Catalog](../../README.md) · [한국어](../ko/cosmos-predict2.md)

Code for inference and training of a world and video generation model.

**Official source:** [Repository](https://github.com/nvidia-cosmos/cosmos-predict2)

**License:** Apache-2.0 code; model weights separately licensed.

## Workflow

This diagram is a conceptual overview.

```mermaid
flowchart LR
  S0["Prepare conditioning inputs"]
  S1["load model"]
  S2["generate video"]
  S3["evaluate results"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Generate and assess visual scenarios for physical AI research.

## Related technologies

Cosmos, Cosmos Evaluator.
