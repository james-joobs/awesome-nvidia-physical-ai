# NeMo Curator

[← Catalog](../../README.md) · [한국어](../ko/nemo-curator.md)

Distributed preparation of text, image, video and audio datasets.

![NeMo Curator pipeline](https://raw.githubusercontent.com/NVIDIA-NeMo/Curator/main/fern/assets/images/architecture-diagram.png)

The stages can be composed and assigned resources independently of the pipeline’s data logic. [Official figure source](https://github.com/NVIDIA-NeMo/Curator)

## Architecture and data flow

Curator assembles preprocessing, scoring and filtering as composable stages. A pipeline describes data and resources while an executor schedules the stages. The documented Xenna executor translates stages into work on Ray actors. NeMo Curator and Cosmos Curator have separate repositories. The latter centers its recipes on Physical AI data such as video.

## Physical AI example

For sensor recordings with operator narration, prepare transcripts and accompanying clip metadata and filter low-quality samples before writing a training manifest. Use the physical-video recipes in Cosmos Curator when segmenting and scoring visual clips is the central task.

## What to verify

Keep source IDs and capture timestamps when joining modalities. Compare sample retention and diversity after filtering. Match the executor and dependencies to the release.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/Curator)
- [Video curation architecture](https://docs.nvidia.com/nemo/curator/about/concepts/video/architecture)
- [Repository license](https://github.com/NVIDIA-NeMo/Curator/blob/HEAD/LICENSE)

## Related guides

[Cosmos Curator](cosmos-curator.md) · [Cosmos Xenna](cosmos-xenna.md)
