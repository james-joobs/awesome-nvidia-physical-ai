# Cosmos RL

[← Catalog](../../README.md) · [한국어](../ko/cosmos-rl.md)

Distributed reinforcement learning infrastructure used by AlpaGym.

> **Limited maintenance**

![Cosmos RL worker architecture](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-rl/main/assets/rl_infra.svg)

The figure separates rollout production, policy updates and controller messages. [Official figure source](https://github.com/nvidia-cosmos/cosmos-rl)

## Architecture and data flow

A controller coordinates policy workers and rollout workers. Rollout replicas produce experiences and policy replicas consume them to train. The documented control messages include rollout, evaluation and weight synchronization. AlpaGym uses the framework for autonomous-driving post-training in AlpaSim.

## Physical AI example

Pin the AlpaGym-compatible trainer and run one scene to inspect rewards, termination conditions and weight updates. Compare a checkpoint with the original policy on held-out routes.

## What to verify

The upstream repository reports limited maintenance and points to the Cosmos 3 ecosystem for new development. Keep working experiment versions pinned and follow the model-specific recipes when migrating.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/nvidia-cosmos/cosmos-rl)
- [AlpaGym integration](https://github.com/NVlabs/alpagym#architecture)
- [Repository license](https://github.com/nvidia-cosmos/cosmos-rl/blob/HEAD/LICENSE)

## Related guides

[Alpagym](alpagym.md) · [NeMo RL](nemo-rl.md) · [Cosmos Framework](cosmos-framework.md)
