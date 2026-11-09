# Cosmos Embed / Dataset Search

[← All projects](../../README.md) · [한국어](../ko/cosmos-embed-search.md)

## Overview

Multimodal embedding model/service and video-search microservices.

## Conceptual workflow

```mermaid
flowchart LR
    n0["Prepare a video collection"] --> n1
    n1["create embeddings"] --> n2
    n2["search by multimodal query"] --> n3
    n3["inspect retrieved clips"]
```

## Workflow and use

Prepare a video collection → create embeddings → search by multimodal query → inspect retrieved clips. This is a conceptual workflow; check the official source for version-specific prerequisites and supported configurations.

**Example use case:** finding relevant clips in a video archive. Check applicability, supported inputs and model versions in the official source.

**Related technologies:** Cosmos Curator, Cosmos.

## Architecture and example

Dataset Search combines a core ingestion/search service, Cosmos Embed NIM, Milvus vector storage, Postgres metadata and a web interface. It creates indexes from video and associated text, then searches embeddings.

Index driving footage and use a semantic query to find clips matching a scenario; review results before curation.

[Official technical source](https://docs.nvidia.com/cosmos/cds/latest/introduction.html)

## Availability and terms

Complete source availability and license scope unverified. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official sources

[Documentation](https://docs.nvidia.com/cosmos/cds/latest/introduction.html)
