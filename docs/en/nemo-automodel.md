# NeMo AutoModel

[← Catalog](../../README.md) · [한국어](../ko/nemo-automodel.md)

PyTorch-native distributed training of supported language and multimodal models.

![AutoModel architecture overview](https://raw.githubusercontent.com/NVIDIA-NeMo/Automodel/main/docs/automodel_diagram.png)

The official overview places the training and distributed execution layers around supported models. [Official figure source](https://github.com/NVIDIA-NeMo/Automodel)

## Architecture and data flow

Model recipes connect a supported Hugging Face model and processor to datasets, losses and a training loop. PyTorch DeviceMesh and DTensor express how model or optimizer state is distributed. The training configuration selects the available parallelism and checkpoint format.

## Physical AI example

Use a supported VLM and adapt it with verified image-question-answer examples from a robot workcell. First run a small dataset to verify image decoding and target-token masking. Then scale across devices and export the checkpoint for held-out tests.

## What to verify

Check each recipe’s supported modality and processing contract. A VLM recipe and checkpoint format do not establish compatibility with a robot action head.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/Automodel)
- [Repository license](https://github.com/NVIDIA-NeMo/Automodel/blob/HEAD/LICENSE)

## Related guides

[NeMo Megatron Bridge](nemo-megatron-bridge.md) · [NeMo RL](nemo-rl.md)
