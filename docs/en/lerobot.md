# LeRobot

[← Back to catalog](../../README.md) · [한국어](../ko/lerobot.md)

LeRobot combines robot and teleoperator interfaces, episode storage, policy training and evaluation. Its dataset is the boundary between collection and learning: a policy selects observations and actions by feature names and time offsets declared in the dataset and training configuration.

## Architecture and data flow

| Component | Inputs, processing and outputs |
|---|---|
| **Recording** | A supported robot and teleoperator provide state and action vectors. Cameras contribute named observations. A recorded episode groups them with the task and timing information needed to replay or train. |
| **LeRobotDataset v3** | Tabular time series are stored in Parquet and video in MP4. Several episodes can share files, with metadata describing episode boundaries and how to locate each camera stream. |
| **Data loader and policy** | The dataset API returns samples and temporal windows for a policy. The training stack consumes them locally or, with supported v3 configuration, streams them from the Hub. |

![The official format diagram shows how data, video and metadata make up a v3 dataset. Use the metadata to locate a specific episode instead of assuming that one episode equals one file.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/lerobotdataset-v3/asset1datasetv3.png)

The official format diagram shows how data, video and metadata make up a v3 dataset. Use the metadata to locate a specific episode instead of assuming that one episode equals one file. [Official figure source](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

![The streaming illustration explains how training can read required shards without a full upfront download.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/lerobotdataset-v3/streaming-lerobot.png)

The streaming illustration explains how training can read required shards without a full upfront download. [Official figure source](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

## Worked example

1. Record a short SO-101 demonstration with named observation cameras. Visualize an episode and verify that camera frames, joint observations and actions remain aligned.
2. Train a supported policy with the same camera and action schema. Compare held-out episodes and policy-controlled rollouts before increasing collection scale.

## What to verify

- Check camera feature names, frame rate, units and action ordering. A schema may load successfully even if camera channels or joint ordering are swapped.
- Verify format compatibility with the target trainer. For example, the GR00T N1.7 repository provides conversion from v3 to its v2-based format.

## Official references and terms

Hugging Face publishes the repository code under Apache-2.0. The Hub lists terms per dataset and model.

- [LeRobot source and supported policies](https://github.com/huggingface/lerobot)
- [LeRobotDataset v3 design](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)
- [Training-time streaming](https://huggingface.co/docs/lerobot/main/training_dataset_streaming)

## Related guides

[Isaac Capture](isaac-capture.md) · [Isaac GR00T](isaac-gr00t.md)
