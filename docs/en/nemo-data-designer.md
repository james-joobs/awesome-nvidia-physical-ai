# NeMo Data Designer

[← Catalog](../../README.md) · [한국어](../ko/nemo-data-designer.md)

Schema-driven generation of synthetic datasets from models and seed data.

![Data Designer architecture](https://arxiv.org/html/2609.17699v1/figures/ndd_architecture_diagram.png)

The report shows how dataset configuration flows through the generation system. [Official figure source](https://arxiv.org/html/2609.17699)

## Architecture and data flow

Columns declare how records are produced. Sampler columns create base values, generation columns can depend on other fields or seed rows, and validators check the resulting records. Model-backed columns may use multimodal context and tool calls when configured. The engine evaluates dependencies in the dataset specification and records artifacts for review.

## Physical AI example

Generate question-answer candidates for warehouse clips using an existing clip manifest and reference event times. Keep the original clip ID, mark generated labels and reject rows with impossible timestamps or unsupported event categories. Have a reviewer check whether questions and answers match the footage.

## What to verify

Validate provenance and distribution as well as schema. Generated questions and labels are separate from pixel data and simulator ground truth. Check provider, model, seed and plugin terms.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/DataDesigner)
- [Documentation](https://docs.nvidia.com/nemo/datadesigner)
- [Technical report and figures](https://arxiv.org/html/2609.17699)
- [Repository license](https://github.com/NVIDIA-NeMo/DataDesigner/blob/HEAD/LICENSE)

## Related guides

[Cosmos Data Factory](cosmos-data-factory.md) · [CDF Auto Labeling](cdf-auto-labeling.md)
