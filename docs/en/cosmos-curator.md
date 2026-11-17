# Cosmos Curator

[Catalog](../../README.md) · [한국어](../ko/cosmos-curator.md)

Cosmos Curator turns source footage into selected, annotated clips for dataset construction. A curation recipe defines the stages, and Cosmos-Xenna executes them over Ray workers.

## How does a long recording become useful training clips?

### Keep each clip tied to its source

Choose stages such as splitting, quality filtering, and annotation. In an illustrative manifest, `source_id=demo07`, `start_s=12.4`, and `end_s=17.8` point to a 5.4-second interval. A quality flag or task annotation helps explain why it was retained. Use the selected stage’s documented output fields.

### Inspect what the filters retain

A filter intended to remove shaky or duplicate footage may also discard useful demonstrations with fast hand movements. Compare the pass rate and a sample of rejected clips when tuning thresholds. Split by source recording so nearby clips from the same video stay in the same dataset split. [Cosmos Curator project](https://github.com/NVIDIA/cosmos-curator)

## Logical and physical views

![Cosmos Curator official logical architecture](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-logical-view.png)

In the logical view, each stage owns a pool of stateful Ray actors. Video decode and clipping can feed filters, captioning, embedding and output writers. The driver schedules downstream work with object references. A worker resolves the reference when it needs the task data. [Official logical architecture](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#logical-view)

![Cosmos Curator official physical architecture](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-physical-view.png)

The physical view shows workers and object stores across nodes. A downstream worker can load an object from the local or a remote store. The scheduler can prefer locality and vary pool sizes based on stage throughput and resource demand. [Official physical architecture](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#physical-view)

## Worked example — curate a manipulation video archive

Split a small batch of long videos into clips, then select filters for motion and video quality. Keep original video IDs, clip offsets, and the outputs of captioning or embedding alongside accepted clips. Review examples from both sides of each filter threshold. If clips accumulate before captioning, inspect stage throughput and GPU allocation before adding more decoders. Partition training and evaluation by source video to keep overlapping clips together. [Official pipeline and documentation](https://github.com/NVIDIA/cosmos-curator#documentation)

Code is Apache-2.0. Model artifacts and storage access have separate requirements and terms. [Official license and contact](https://github.com/NVIDIA/cosmos-curator#license-and-contact)

## Related tools

Compare the Physical AI recipes here with general multimodal curation in [NeMo Curator](nemo-curator.md). [Cosmos Xenna](cosmos-xenna.md) describes the stage executor used by some pipelines.
