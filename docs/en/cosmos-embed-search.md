# Cosmos Embed / Dataset Search

[← All projects](../../README.md) · [한국어](../ko/cosmos-embed-search.md)

Cosmos Dataset Search (CDS) indexes video and text so users can retrieve candidate clips from a large corpus. Cosmos Embed NIM projects supported text and video inputs into a shared vector space.

## Read the official service diagram

![NVIDIA Cosmos Dataset Search architecture](https://docs.nvidia.com/cosmos/cds/latest/_images/cds_system_overview.png)

| Layer | Responsibility |
|---|---|
| Core service and indexing | Orchestrate ingestion and create an index tied to a dataset volume and version |
| Cosmos Embed NIM | Encode clips and text queries into comparable vectors |
| Milvus | Store vectors and find nearest candidates |
| PostgreSQL | Store collection metadata and storage configuration |
| Retrieval and UI | Query the selected volume and index, resolve assets, and render them for the user |

The indexing arrow takes you from stored media to a named index. The retrieval arrow starts with a query and resolves vector neighbors back to accessible assets. This division helps distinguish a stale index, a ranking issue and an unreadable asset. [NVIDIA CDS architecture](https://docs.nvidia.com/cosmos/cds/latest/introduction.html) · [Docker Compose deployment](https://docs.nvidia.com/cosmos/cds/latest/docker-compose-deployment.html)

## Worked example — retrieve traffic near misses

Index an authorized collection and search for pedestrians entering the crosswalk from behind parked vehicles. Review the top results against a small hand-labeled set. Inspect clip boundaries because a brief event can span two chunks. Create an index version when clip definitions or the embedding checkpoint change. Similarity ranks candidates for review. Use a timestamp-aware model or manual review before treating hits as ground truth. [Official repository](https://github.com/NVIDIA-Omniverse-blueprints/cosmos-dataset-search) · [Cosmos Reason2](cosmos-reason2.md)

Check official deployment and service terms for the selected CDS and NIM versions. [NVIDIA documentation](https://docs.nvidia.com/cosmos/cds/latest/introduction.html)
