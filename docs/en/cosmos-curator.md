# Cosmos Curator

[Catalog](../../README.md) · [한국어](../ko/cosmos-curator.md)

Cosmos Curator turns source footage into selected, annotated clips for dataset construction. A curation recipe defines the stages, and Cosmos-Xenna executes them over Ray workers.

## Logical and physical views

![Cosmos Curator official logical architecture](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-logical-view.png)

In the logical view, each stage owns a pool of stateful Ray actors. Video decode and clipping can feed filters, captioning, embedding and output writers. The driver schedules downstream work with object references. A worker resolves the reference when it needs the task data. [Official logical architecture](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#logical-view)

![Cosmos Curator official physical architecture](https://raw.githubusercontent.com/NVIDIA/cosmos-curator/main/docs/assets/cosmos-curator-physical-view.png)

The physical view shows workers and object stores across nodes. A downstream worker can load an object from the local or a remote store. The scheduler can prefer locality and vary pool sizes based on stage throughput and resource demand. [Official physical architecture](https://github.com/NVIDIA/cosmos-curator/blob/main/docs/curator/reference/architecture.md#physical-view)

## Worked example — curate a manipulation video archive

Split a small batch of long videos into clips, then select filters for motion and video quality. Keep original video IDs, clip offsets, and the outputs of captioning or embedding alongside accepted clips. Review examples from both sides of each filter threshold. If clips accumulate before captioning, inspect stage throughput and GPU allocation before adding more decoders. Partition training and evaluation by source video to keep overlapping clips together. [Official pipeline and documentation](https://github.com/NVIDIA/cosmos-curator#documentation)

Code is Apache-2.0. Model artifacts and storage access have separate requirements and terms. [Official license and contact](https://github.com/NVIDIA/cosmos-curator#license-and-contact)
