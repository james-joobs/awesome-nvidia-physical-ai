# NeMo Megatron Bridge

[← Catalog](../../README.md) · [한국어](../ko/nemo-megatron-bridge.md)

Megatron Core training recipes and bidirectional Hugging Face checkpoint conversion.

![Megatron Bridge project overview](https://raw.githubusercontent.com/NVIDIA-NeMo/Megatron-Bridge/main/Repo-Mbridge.png)

The project figure provides context for the checkpoint bridge and its training ecosystem. [Official figure source](https://github.com/NVIDIA-NeMo/Megatron-Bridge)

## Architecture and data flow

Bridge maps supported Hugging Face model weights and architecture to a Megatron Core representation. Recipes configure data, parallelism, optimizer and training. After pretraining, SFT or LoRA on a supported model, the appropriate conversion can export weights back into the Hugging Face format.

## Physical AI example

For a larger supported VLM, validate the Hugging Face to Megatron conversion on a handful of inspection images before scheduling multi-GPU SFT. After training, compare exported and training-side results on the same image and prompt.

## What to verify

Check that a bridge exists for the exact model, and verify tokenizer, vision processor and numerical agreement across the conversion boundary.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/Megatron-Bridge)
- [Repository license](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/HEAD/LICENSE)

## Related guides

[NeMo AutoModel](nemo-automodel.md) · [NeMo RL](nemo-rl.md)
