# Human-1M Explorer

[Catalog](../../README.md) · [한국어](../ko/human-1m-explorer.md)

Human-1M Explorer is NVIDIA's browser for inspecting egocentric human work demonstrations. The Space illustrates selected examples and their annotations. The dataset card describes the released 100K-hour slice and its data contract.

## Read the anatomy of an episode

![NVIDIA Human-1M official episode anatomy for bundling flower stems](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K/resolve/main/figures/card_episode_anatomy.png)

The flower-stem example aligns head and wrist views, reconstructed geometry, hand and head tracks, a task-level goal (T1), and timed subtask actions (T2). The picture shows a stereo example with wrist views. Other capture configurations have different camera availability. [Dataset card](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K#anatomy-of-an-episode) · [Official Explorer](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer)

![Human-1M Explorer 3D task map](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer/resolve/main/figures/task_landscape_3d.png)

The task map positions task descriptions by embedding similarity. Use it to browse related activities, then open individual episodes to inspect whether the actual motions and objects match the task you are collecting. [Official task explorer](https://huggingface.co/spaces/nvidia/PhysicalAI-Human-1M-Explorer#semantic-map)

## Worked example — select hand-tool interactions

Find episodes around assembly and repair. For a small sample, align T2 intervals with the MP4 timestamps, inspect both hands near occlusions, and check pose confidence and tracking masks in the frame data. LeRobot v3 shards separate video streams from Parquet frame rows and episode metadata. Join through episode metadata and timestamps rather than assuming that every episode has the same cameras or duration. Retargeting is an additional step with embodiment and contact constraints. [Official schema](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K/blob/main/SCHEMA.md) · [Quality standards](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K#quality-at-every-step)
