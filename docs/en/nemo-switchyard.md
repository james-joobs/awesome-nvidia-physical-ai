# NeMo Switchyard

[← Catalog](../../README.md) · [한국어](../ko/nemo-switchyard.md)

Model routing for LLM agents and applications.

![Switchyard components](https://raw.githubusercontent.com/NVIDIA-NeMo/Switchyard/main/docs/assets/switchyard-components.png)

The official diagram separates the host or gateway from model selection and upstream calls. [Official figure source](https://github.com/NVIDIA-NeMo/Switchyard)

## Architecture and data flow

Switchyard separates model choice from the application’s task logic. A host gives the routing library a request, a pool of available models and a strategy. Task routing can ask a model to classify the request, and stage routing can take recent tool activity into account. The host handles requested upstream calls and consumes the routing outcome. Gateway integrations can translate OpenAI and Anthropic request, response and streaming formats.

## Physical AI example

For an inspection assistant, keep image and video analysis in a vision-capable service such as VSS. Route its downstream text summarization and report drafting across a model pool. Compare a fixed single-model baseline with the routed setup on the same clips and prompts.

## What to verify

Measure cost and latency per successfully completed report. Verify tool calls, streaming, provider error handling and accepted modalities end to end. The standalone server is documented for demos and local evaluation. Check the gateway integration and its version before deployment.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/Switchyard)
- [Architecture](https://nvidia-nemo.github.io/Switchyard/architecture/)
- [Relay integration](https://github.com/NVIDIA-NeMo/Switchyard/blob/main/docs/integrations/nemo_relay.md)
- [Repository license](https://github.com/NVIDIA-NeMo/Switchyard/blob/HEAD/LICENSE)

## Related guides

[NeMo Relay](nemo-relay.md) · [Metropolis / VSS](metropolis-vss.md)
