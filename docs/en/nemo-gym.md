# NeMo Gym

[← Catalog](../../README.md) · [한국어](../ko/nemo-gym.md)

Tool-using agent rollout environments and verifiers.

![NeMo Gym environment overview](https://raw.githubusercontent.com/NVIDIA-NeMo/Gym/main/fern/assets/images/product_overview.png)

The official overview shows how agent, resource and model services take part in rollouts. [Official figure source](https://github.com/NVIDIA-NeMo/Gym)

## Architecture and data flow

A model server exposes generation, an agent server controls the interaction loop, and a resource server supplies task tools and verification. Rollouts record model and tool interactions for evaluation or training. NeMo RL documents an environment integration.

## Physical AI example

Create an offline incident-triage task with a read-only clip metadata tool. Verify that the agent cites the expected event ID and uses only permitted calls. Use the same tasks for a repeatable evaluation before considering post-training.

## What to verify

Pin task data, tool schema and verifier version. Review individual environment and dataset terms. Robot physics and control still run in the simulation or robot stack.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/Gym)
- [Repository license](https://github.com/NVIDIA-NeMo/Gym/blob/HEAD/LICENSE)

## Related guides

[NeMo RL](nemo-rl.md) · [Isaac Lab](isaac-lab.md)
