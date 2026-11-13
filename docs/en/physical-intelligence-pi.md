# Physical Intelligence π series and openpi

[← Robot foundation model catalog](../../README.md#robot-foundation-models-and-vlas) · [한국어](../ko/physical-intelligence-pi.md)

Physical Intelligence’s π series uses camera observations, language instructions, and robot state to generate robot actions. The openpi repository publishes inference and fine-tuning code and checkpoints for three model variants. The Pi API beta offers hosted fine-tuning and inference. Release and access information was checked on November 13, 2026.

## Models and availability

| Model or service | What it does | Availability |
|---|---|---|
| **π0** | Uses a PaliGemma backbone and a flow-matching action expert to generate a sequence of continuous actions. | The base checkpoint and selected ALOHA and DROID fine-tunes are public. [Paper](https://arxiv.org/abs/2410.24164) · [Release](https://www.pi.website/blog/openpi) · [Checkpoints](https://github.com/Physical-Intelligence/openpi#model-checkpoints) |
| **π0-FAST** | Generates discrete action tokens autoregressively and decodes them into robot actions. | The base and DROID checkpoints are public. Physical Intelligence also publishes FAST as a standalone action tokenizer. [Checkpoints](https://github.com/Physical-Intelligence/openpi#model-checkpoints) · [FAST tokenizer](https://huggingface.co/physical-intelligence/fast) |
| **π0.5** | Builds on π0 with co-training on different types of robot and vision-language data to improve transfer to new environments. | The base checkpoint and LIBERO and DROID fine-tunes are public. The model was announced in April 2025, and openpi lists its checkpoint release in September 2025. [Research](https://www.pi.website/blog/pi05) · [Checkpoints](https://github.com/Physical-Intelligence/openpi#model-checkpoints) |
| **π0.6 / π*0.6** | π0.6 is a refined base VLA. π*0.6 adds reinforcement learning with the RECAP method, using robot experience and feedback. | Research published November 17, 2025. Neither version appears in the openpi checkpoint list. [Research](https://www.pi.website/blog/pistar06) |
| **π0.7** | Conditions actions on language, visual subgoals, and other context to transfer skills across tasks and robot platforms. | Research published April 16, 2026. A public checkpoint is unverified. [Research](https://www.pi.website/blog/pi07) |
| **Pi API beta** | Accepts uploaded demonstration data, runs hosted fine-tuning, and serves the resulting policy for inference. | Announced October 13, 2026, with a waitlist. The public announcement leaves the underlying model IDs unspecified. [Announcement](https://www.pi.website/blog/api-beta) · [Waitlist](https://www.pi.website/) |

## Run a released checkpoint

1. To check that the policy server accepts observations and returns an action chunk, run the simple client on a supported GPU host. It generates an observation without a robot. [openpi requirements](https://github.com/Physical-Intelligence/openpi#requirements) · [Simple client](https://github.com/Physical-Intelligence/openpi/tree/main/examples/simple_client)
2. To evaluate a task in simulation, start with the released π0.5-LIBERO checkpoint and the official LIBERO evaluation. The workflow starts a policy server and a simulator client. The client sends fresh observations and applies the returned actions in the simulator. [openpi LIBERO example](https://github.com/Physical-Intelligence/openpi/tree/main/examples/libero)
3. To adapt to another robot, choose a base checkpoint and gather demonstrations in the target setup. The openpi fine-tuning guide uses LeRobot data and defines input/output transforms and normalization for the selected robot. [Fine-tuning guide](https://github.com/Physical-Intelligence/openpi#fine-tuning-base-models-on-your-own-data) · [LeRobot π0.5 policy](https://huggingface.co/docs/lerobot/pi05)

Match camera keys, state and action ordering, normalization statistics, and the controller’s action format to the checkpoint. Inspect a short rollout before measuring task success and inference latency. The upstream openpi PyTorch backend covers π0 and π0.5. For π0-FAST, use the upstream JAX implementation. [openpi PyTorch support](https://github.com/Physical-Intelligence/openpi#pytorch-support) · [Normalization statistics](https://github.com/Physical-Intelligence/openpi/blob/main/docs/norm_stats.md)

## Code, checkpoints, and terms

The openpi repository code uses Apache-2.0. The official openpi checkpoint list identifies download locations without listing separate checkpoint terms. Hugging Face’s LeRobot π0 and π0.5 base conversions carry the Gemma license tag. Check the terms for the checkpoint, its backbone, and the training data you plan to use. [openpi LICENSE](https://github.com/Physical-Intelligence/openpi/blob/main/LICENSE) · [LeRobot π0 card](https://huggingface.co/lerobot/pi0_base) · [LeRobot π0.5 card](https://huggingface.co/lerobot/pi05_base) · [Gemma terms](https://ai.google.dev/gemma/terms)

## Related guides

[LeRobot](lerobot.md) · [Isaac GR00T](groot-model.md)
