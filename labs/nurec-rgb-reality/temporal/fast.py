"""Current-frame-only decoding and optional CUDA graph replay.

Keep the full five-frame encoder and DiT context. The pinned VAE decoder is
causal; only its first output is consumed by the viewer. No weight, resolution,
precision, diffusion-step or context-length reduction is applied.
"""
from __future__ import annotations
import torch


def set_layout(model, profile):
    if profile not in {'baseline', 'exact', 'tuned'}:
        raise ValueError('Unknown execution profile')
    tuned = profile == 'tuned'
    torch.backends.cudnn.benchmark = tuned
    if tuned:
        torch.backends.cudnn.benchmark_limit = 10
    # Only convolution weights are rank-five. Blanket Module.to(memory_format)
    # would incorrectly convert rank-four normalization parameters too.
    torch.nn.utils.convert_conv3d_weight_memory_format(
        model._inner_vae(), torch.channels_last_3d if tuned else torch.contiguous_format
    )


class CurrentFrame:
    def __init__(self, model):
        if model.vae_skip_connection:
            raise ValueError('This optimization requires the pinned no-skip VAE')
        self.model = model

    def __call__(self, x):
        model = self.model
        latent = model.vae_encode(x)
        sigma = model.timesteps.to(dtype=latent.dtype) / 1000
        denoised = model.unet.denoise(xt_B_C_T_H_W=latent, sigma=sigma, condition=model.condition).x0
        # Retain the full video normalization before slicing. Image and video
        # normalization need not be equal in other releases or configurations.
        tokenizer = model.vae
        raw = denoised / model.sigma_data
        stats = tokenizer.model
        if raw.shape[2] == 1:
            raw = raw * stats.img_std.type_as(raw) + stats.img_mean.type_as(raw)
        else:
            raw = raw * stats.video_std[:, :, :raw.shape[2]].type_as(raw) + stats.video_mean[:, :, :raw.shape[2]].type_as(raw)
        return stats.decode(raw[:, :, :1].contiguous())


class GraphForward:
    """One fixed-shape graph. Returned storage belongs to the next replay too."""
    def __init__(self, forward, example, warmup=3):
        self.input = torch.empty_like(example)
        self.input.copy_(example)
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream), torch.inference_mode():
            for _ in range(warmup):
                forward(self.input)
        torch.cuda.current_stream().wait_stream(stream)
        torch.cuda.synchronize()
        self.graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph, stream=stream), torch.inference_mode():
            self.output = forward(self.input)
        torch.cuda.synchronize()

    def __call__(self, x):
        if x.shape != self.input.shape or x.dtype != self.input.dtype or x.device != self.input.device:
            raise ValueError('CUDA graph input must retain its captured shape, dtype and device')
        self.input.copy_(x)
        self.graph.replay()
        return self.output
