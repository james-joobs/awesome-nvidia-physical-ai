# AlpaGym

[← Catalog](../../README.md) · [한국어](../ko/alpagym.md)

AlpaGym links an autonomous-driving policy to AlpaSim for closed-loop experience and to Cosmos-RL for distributed policy updates.

## How it works

The host resolves Hydra configuration, starts services, and manages local or Slurm launch artifacts. The runtime runs in a GPU container. Cosmos-RL requests rollouts, the episode runner calls AlpaSim over gRPC, and policy adapters batch inference. Reward terms score completed drives and episode transport returns artifacts for optimization.

```mermaid
flowchart LR
    H["Host config and launch"] --> R["Runtime harness"]
    T["Cosmos-RL trainer"] -->|rollout request| R
    R <-->|observations and actions| S["AlpaSim episode"]
    R --> W["Reward and episode artifacts"] --> T
```

### Component interfaces

| Component | Input | Output |
|---|---|---|
| Host | Resolved experiment configuration and scene list | Simulator launch and run artifacts |
| Runtime | Rollout request, policy and AlpaSim observations | Scored episode and observations for training |
| Cosmos-RL | Rollout artifacts and training settings | Updated policy weights |

## A practical workflow

Bring up the documented AlpaSim tutorial first. Train from a supported checkpoint on a small fixed scene set. Compare the starting and trained checkpoint on held-out routes and inspect cases where reward improved but the drive looks worse.

## What to verify

Save the resolved configuration, scene split, reward weights and policy checkpoints. Check which model adapters the checkout supports. Measure collision, route progress and rollout throughput independently so policy quality is distinguishable from system throughput.

## License and availability

Code: Apache-2.0; dependencies and models have separate terms. Models, data, dependencies and hosted services may have separate terms; check each source before use.

## Official references

- [Architecture and workflow documentation](https://github.com/NVlabs/alpagym#architecture)
- [Onboarding and prerequisites](https://github.com/NVlabs/alpagym/blob/main/docs/ONBOARDING.md)
- [Related official resource · github.com](https://github.com/NVlabs/alpagym)

## Related tools

See [Cosmos RL](cosmos-rl.md) for the rollout and trainer boundary and its upstream maintenance status.
