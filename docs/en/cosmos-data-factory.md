# Cosmos Data Factory (CDF; formerly Physical AI Data Factory)

[Catalog](../../README.md) · [한국어](../ko/cosmos-data-factory.md)

A set of composable workflows and skills for curating, labeling, augmenting and generating physical AI training data.

**Official sources:** [Repository](https://github.com/NVIDIA/cosmos-data-factory)

**License and access:** Code: Apache-2.0; documentation and skills: CC-BY-4.0; models and services have separate terms. Models, data, dependencies and hosted services may have separate terms; check each source before use.

**Components.** Reference blueprints combine reusable curation, labeling, augmentation, simulation, and evaluation components. CDF Orchestration runs reference blueprints as Airflow DAGs; execution backends differ by blueprint. [Official overview](https://github.com/NVIDIA/cosmos-data-factory).

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Collect source data"]
  S1["curate and label"]
  S2["augment or simulate"]
  S3["evaluate"]
  S4["export"]
  S0 --> S1 --> S2 --> S3 --> S4
```

## Use case

Create varied driving clips, rare event videos, or defect inspection datasets from limited examples.

## Related technologies

CDF Auto Labeling, CDF Augmentation, CDF Simulation, Cosmos Curator, Cosmos Evaluator, OSMO. Confirm compatibility and runtime requirements in the documentation for each version.
