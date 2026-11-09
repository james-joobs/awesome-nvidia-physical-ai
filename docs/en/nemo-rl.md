# NeMo RL

[← Catalog](../../README.md) · [한국어](../ko/nemo-rl.md)

Distributed SFT and reinforcement learning for supported LLMs and VLMs.

![NeMo RL architecture](https://raw.githubusercontent.com/NVIDIA-NeMo/RL/main/docs/assets/RL_diagram.png)

Read the diagram as separate rollout and training responsibilities connected by the distributed runtime. [Official figure source](https://github.com/NVIDIA-NeMo/RL)

## Architecture and data flow

Rollout workers generate candidate responses, an environment or scoring function returns rewards, and the training workers update the policy. Ray coordinates workers. The training implementation can use the AutoModel DTensor or Megatron Bridge path depending on recipe. The repository includes VLM SFT and GRPO support.

## Physical AI example

Build a fixed set of image questions about a workcell and score answers against event labels or allowed structured values. Compare the starting and post-trained model on held-out scenes. For autonomous-driving rollouts, use the separately documented AlpaGym and Cosmos RL setup where applicable.

## What to verify

Validate the reward against human labels and check reward gains against task accuracy. Use the exact model and backend requirements of the chosen recipe. A language or VLM reward does not validate a real robot controller.

## License and availability

Apache-2.0 repository code. Model weights, external services and dependencies can have separate terms.

## Official sources

- [Repository](https://github.com/NVIDIA-NeMo/RL)
- [Repository license](https://github.com/NVIDIA-NeMo/RL/blob/HEAD/LICENSE)

## Related guides

[NeMo Gym](nemo-gym.md) · [Cosmos RL](cosmos-rl.md) · [Alpagym](alpagym.md)
