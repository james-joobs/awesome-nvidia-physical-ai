# Cosmos RL

[← Catalog](../../README.md) · [한국어](../ko/cosmos-rl.md)

Distributed reinforcement learning infrastructure used by AlpaGym.

> **Limited maintenance**

![Cosmos RL worker architecture](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-rl/main/assets/rl_infra.svg)

The figure separates rollout production, policy updates and controller messages. [Official figure source](https://github.com/nvidia-cosmos/cosmos-rl)

## Which process collects experience and which updates the policy?

### Separate collection and training

In distributed reinforcement learning, rollout workers run the policy and collect experience. The trainer uses that experience and its scores to update weights. In AlpaGym, a rollout is a closed-loop drive in AlpaSim. After selecting the task and algorithm, track collection throughput separately from learning and evaluation metrics.

### Read rollout settings in a real preset

The [published training preset](https://github.com/NVlabs/alpagym/blob/972d160eed0e23d388497851504a3a233fec5879/packages/host/src/alpagym_host/conf/run/public_2507_1epoch.yaml) sets `rollout.n_generation=2`, `rollout.batch_size=1`, and `train.num_epochs=1`. These specify generation requests, the rollout batch setting, and training epochs. Inspect [AlpaGym rewards and metrics](alpagym.md) for driving behavior. [Cosmos RL project](https://github.com/nvidia-cosmos/cosmos-rl)

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
