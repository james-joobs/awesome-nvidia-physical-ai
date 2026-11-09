# Cosmos Curator

[Catalog](../../README.md) · [한국어](../ko/cosmos-curator.md)

A data curation framework for processing and filtering large collections of videos and images.

**Official sources:** [Repository](https://github.com/NVIDIA/cosmos-curator)

**License and access:** Apache-2.0; models have separate terms. Models, data, dependencies and hosted services may have separate terms; check each source before use.

![Cosmos Curator dashboard](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-dashboard.png)

Image source: [Cosmos Curator](https://github.com/NVIDIA/cosmos-curator)

**Architecture.** Curator pipelines use parallel workers per stage. The architecture guide describes how workers process video tasks, transfer artifacts and scale stages. [Official architecture](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md).

## Workflow

The following conceptual diagram is an explanatory overview, not an official architecture diagram.

```mermaid
flowchart LR
  S0["Ingest media"]
  S1["split and process"]
  S2["filter and deduplicate"]
  S3["inspect and export"]
  S0 --> S1 --> S2 --> S3
```

## Use case

Prepare cleaner video corpora before model training or dataset search.

## Related technologies

Cosmos Data Factory, Cosmos Dataset Search. Confirm compatibility and runtime requirements in the documentation for each version.
