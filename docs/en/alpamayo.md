# Alpamayo

[← Catalog](../../README.md) · [한국어](../ko/alpamayo.md)

Alpamayo is a family of reasoning and action models for autonomous driving. The R1 research architecture is a useful concrete example. Check the model card before carrying that architecture or input contract over to another release.

![Alpamayo-R1 model architecture](https://arxiv.org/html/2511.00088v2/main_arch_1.png)

*Follow the multiview and ego-motion inputs into the VLM backbone, then distinguish the reasoning tokens from the trajectory decoder’s waypoints.* [Official figure source](https://arxiv.org/html/2511.00088v2#S3)

![Alpamayo-R1 chain of causation labeling pipeline](https://arxiv.org/html/2511.00088v2/labeling_overview_new_2.png)

*This training-data diagram shows how driving clips become labeled examples linked to specific decisions. It is separate from inference.* [Official figure source](https://arxiv.org/html/2511.00088v2#S3)

## How it works

R1 conditions its reasoning and trajectory predictions on observations such as camera frames and ego-motion history. A vision-language backbone produces driving reasoning and a trajectory generation component produces continuous waypoints. A simulator driver can consume the resulting trajectory to advance the ego vehicle. Reasoning text and motion are separate outputs to inspect.

## A practical workflow

Run an Alpamayo-supported AlpaSim driver on a scenario with a partly occluded obstacle or a complex merge. Review the generated reasoning with the resulting trajectory and rollout metrics. Compare against a baseline policy using the same scene and route.

## What to verify

Check the checkpoint’s accepted cameras, context and coordinate frames, required memory and gated access. Evaluate trajectory quality and behavior independently of whether the explanation sounds plausible.

## License and availability

Access and license terms for weights vary by model version. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Architecture and workflow documentation](https://research.nvidia.com/labs/avg/publication/2025/12/alpamayo-r1/)
- [R1 model card](https://huggingface.co/nvidia/Alpamayo-R1-10B)
- [AlpaSim driver tutorial](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md)
- [Related official resource · github.com](https://github.com/NVlabs/alpamayo-recipes)
