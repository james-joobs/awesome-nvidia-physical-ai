# NVIDIA Physical AI dataset collection

[Catalog](../../README.md) · [한국어](../ko/physical-ai-dataset-collection.md)

NVIDIA's Physical AI collection is a discovery entry point for datasets. The collection groups resources for robotics, autonomous driving, simulation and other physical AI tasks. The individual cards specify file layout, access and intended use.

## Choose by the artifact you need

| Question | Start with | Inspect a small sample for |
|---|---|---|
| Can this object be placed into a simulation scene? | [3D assets and environments](datasets-3d-assets.md) | USD or MJCF representation, relative paths, scale, collision and articulation |
| Can this recording supervise a robot policy? | [Robot demonstrations](datasets-robot-demonstrations.md) | Embodiment, observation and action arrays, language goal, timing and camera views |
| Can I replay a scene or evaluate a video model? | [Driving and world-model data](datasets-driving-world-model.md) | Calibration and sensor alignment for replay, or task-specific splits and metrics for evaluation |
| Can I reproduce a specific recipe? | [V2D and Cosmos datasets](datasets-v2d-cosmos.md) | Whether the files supply model conditions, training targets, or benchmark inputs |

## Worked example — assemble a reproducible robotics slice

Start with one versioned dataset and record card URL, revision, filenames, access terms and intended purpose. Validate one episode with your data loader, replay its observations, and confirm action dimensions and units before batching. Keep generated variants with their parent episode when splitting by task or session. For a concrete contrast, the G1 teleoperation card specifies HDF5 plus MP4, while Human-1M uses LeRobot v3 shards with Parquet and video. [G1 card](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1) · [Human-1M card](https://huggingface.co/datasets/nvidia/PhysicalAI-Human-1M-100K)

Access and licensing are evaluated per entry. [NVIDIA collection](https://huggingface.co/collections/nvidia/physical-ai) · [NVIDIA dataset index](https://huggingface.co/nvidia/datasets)
