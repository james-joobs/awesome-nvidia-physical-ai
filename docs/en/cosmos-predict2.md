# Cosmos Predict2 code

[Catalog](../../README.md) · [한국어](../ko/cosmos-predict2.md)

Cosmos Predict2 generates visual world states from conditioning signals. Its archived repository documents separate Text2Image and Video2World checkpoints and examples post-trained for robot videos and action conditioning.

## Official architecture and input contract

![NVIDIA Cosmos Predict2 architecture](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-predict2/main/assets/cosmos-predict-diagram.png)

Read from the generation conditions to the visual output. In Video2World, one image or multiple video frames establish visual context, and text guides the scenario. Multiple frames also provide motion cues. The standard recipe takes media and text. Use the documented action-conditioned checkpoint and input format when actions drive the experiment. [Repository architecture and models](https://github.com/nvidia-cosmos/cosmos-predict2#models) · [Video2World inference](https://github.com/nvidia-cosmos/cosmos-predict2/blob/main/documentations/inference_video2world.md)

Inside the Video2World model, a diffusion transformer denoises video latents. Temporal concatenation puts input latents next to the frames being generated. Text reaches the denoising layers through cross-attention, and adaptive normalization encodes diffusion time. Resolution and frame rate are checkpoint-specific. The official 720p 16 FPS variant, for example, emits 1280 × 704 frames. [Official 2B model card and input/output specification](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Video2World#model-architecture)

![Official Video2World conditioning image](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-predict2/main/assets/video2world/example_input.jpg)

This is the visual input shown in the official Quick Start. It is the opening observation against which to compare the continuation. [Quick Start](https://github.com/nvidia-cosmos/cosmos-predict2#quick-start)

## Worked example — continue a robot clip

Start from an opening gripper frame and a prompt describing the next movement. Run the same prompt and seed once with a still image and once with multiple frames. Keep the generated video and saved prompt along with checkpoint and conditioning length. Compare object persistence, camera stability and whether the gripper stays aligned to the target. For a batch, the documented JSON input associates each input video with its prompt and output path. For an action-conditioned run, confirm normalization and embodiment before supplying trajectories. [Inference examples and post-training](https://github.com/nvidia-cosmos/cosmos-predict2#user-guide)

The repository was archived in December 2025 and points users to Predict2.5. Code is Apache-2.0 and the documented weights use NVIDIA Open Model License. [Repository and terms](https://github.com/nvidia-cosmos/cosmos-predict2#license-and-contact)
