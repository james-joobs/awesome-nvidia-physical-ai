# NeMo Guardrails

[← Catalog](../../README.md) · [한국어](../ko/nemo-guardrails.md)

Programmable checks for model requests, retrieval, actions and responses.

![Guardrails request flow](https://raw.githubusercontent.com/NVIDIA-NeMo/Guardrails/develop/docs/_static/images/programmable_guardrails_flow.png)

The flow shows where application checks can run around model and tool calls. [Official figure source](https://github.com/NVIDIA-NeMo/Guardrails)

## Architecture and data flow

Rails inspect input, retrieved context, dialog flow, tool execution or output according to configuration. The runtime can use Colang flows and separate safety or topic models. Tool checks belong at the application boundary where inputs and actions are visible.

## Physical AI example

For a VSS assistant, use an execution rail to check that a maintenance ticket has a source clip ID and a permitted destination. Keep human review for high-impact actions and test the rule on fabricated events and tool parameters.

## What to verify

Validate allowed and blocked actions with recorded examples. Guardrails are application controls. Robot motion limits, emergency stops and safety validation remain in the physical system.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/Guardrails)
- [Library architecture and rail types](https://docs.nvidia.com/nemo/guardrails/about-nemo-guardrails-library/how-it-works)
- [Repository license](https://github.com/NVIDIA-NeMo/Guardrails/blob/HEAD/LICENSE.md)

## Related guides

[Metropolis / VSS](metropolis-vss.md) · [NVIDIA NeMo Platform](nemo-platform.md)
