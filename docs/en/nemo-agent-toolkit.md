# NeMo Agent Toolkit

[← Catalog](../../README.md) · [한국어](../ko/nemo-agent-toolkit.md)

Agent workflow integration and profiling, with a published robotics example.

> **Deprecated, EOL planned for end of 2026**

![Multi-agent robotics synthetic data workflow](https://developer-blogs.nvidia.com/wp-content/uploads/2025/06/Multi-agent-SDG-workflow-1024x505.png)

The diagram connects scenario prompts, USD scene generation and downstream video processing. [Official figure source](https://developer.nvidia.com/blog/scale-realistic-robot-simulation-using-the-nvidia-nemo-agent-toolkit-for-physical-ai/)

## Architecture and data flow

NVIDIA’s robot simulation example converts scenario prompts into scene variations. The agent searches for USD assets and calls scene modification tools. A headless Omniverse stage renders a robot sequence. Cosmos Transfer can alter appearance, and Cosmos Reason can check the resulting video. Each stage exchanges prompts, assets or video artifacts through its own interface.

## Physical AI example

Reproduce the idea on a small fixed scene with a few obstacle layouts. Store prompt, stage version, assets and rendered video per variant. Compare generated clips with expected positions before treating them as training samples.

## What to verify

NVIDIA deprecated the toolkit in October 2026 and targets end of 2026 for end of life. Use the documented migration map for observability, agent execution and evaluation. Treat the example’s model and service endpoints as version-specific.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA/NeMo-Agent-Toolkit)
- [Robotics synthetic data workflow](https://developer.nvidia.com/blog/scale-realistic-robot-simulation-using-the-nvidia-nemo-agent-toolkit-for-physical-ai/)
- [Official lifecycle and migration guide](https://docs.nvidia.com/nemo/agent-toolkit/1.9/resources/migration-guide.html)
- [Repository license](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/HEAD/LICENSE.md)

## Related guides

[NeMo Relay](nemo-relay.md) · [NeMo Fabric](nemo-fabric.md) · [NeMo Helix](nemo-helix.md) · [Replicator](replicator.md)
