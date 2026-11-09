# NeMo Retriever Library

[← Catalog](../../README.md) · [한국어](../ko/nemo-retriever.md)

Multimodal extraction, indexing and retrieval of document evidence.

![NeMo Retriever extraction pipeline](https://docs.nvidia.com/nemo/retriever/extraction/images/overview-extraction.png)

The extraction pipeline converts input files into data and metadata suitable for retrieval. [Official figure source](https://docs.nvidia.com/nemo/retriever/latest/)

## Architecture and data flow

Ingestion extracts typed content such as text, tables, diagrams or transcripts into records with metadata. Chunking and embedding can write vectors to a store. Query and reranking select relevant records. Optional inference can use local models or separate NIM endpoints. The library has also been referred to as NVIDIA Ingest.

## Physical AI example

Index equipment manuals and standard operating procedures. An incident agent can use VSS for timestamped video evidence and Retriever for a cited maintenance procedure, then present the sources together in its report.

## What to verify

Check document revision, page-level provenance and retrieval accuracy. Visual event search and transcript retrieval use different inputs and evidence. Hosted services and model endpoints have separate terms.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA/NeMo-Retriever)
- [Extraction and ingestion architecture](https://docs.nvidia.com/nemo/retriever/latest/)
- [NVIDIA example combining VSS with document RAG](https://developer.nvidia.com/blog/?p=120054)
- [Repository license](https://github.com/NVIDIA/NeMo-Retriever/blob/HEAD/LICENSE)

## Related guides

[Metropolis / VSS](metropolis-vss.md) · [NemoClaw](nemoclaw.md)
