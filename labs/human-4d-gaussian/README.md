# Human 4D Gaussian lab

[한국어](README.ko.md) · [Full learning guide](../../docs/en/labs/human-4d-gaussian.md) · [Sources and terms](SOURCES.md)

This folder provides real stage adapters for two routes:

- **Known-geometry control:** official SOMA example motion → native Warp skinning → synthetic RGB and per-vertex Gaussians. No monocular learning is claimed.
- **Local monocular reconstruction:** local video → official GEM-X motion-video → SOMA/SAM2 → source-preserving 4DAnyone seed → original face/hand and MoGe guidance → pose-conditioned later intervals → native/browser rendering.

The public control can be inspected without CUDA. New training needs explicitly configured Linux GPU environments. This is not a silent one-click installer: a missing runtime, model or stage output stops with a prerequisite error.

## 1. Inspect the public control without a GPU

From the repository root:

```bash
python3 labs/human-4d-gaussian/pipeline.py \
  --root "$HOME/physical-ai-labs/control-check" --mode control \
  --package-dir site/public/showcase/human-4d-control --deep check
```

This checks gzip array hashes, counts, timeline coverage, native SOMA position parity and full video decoding when FFmpeg is available. Reports are written under `--root`, not into the input package. It does not run reconstruction or treat the reference YouTube footage as sample input.

## 2. Configure isolated runtimes

Run `setup` once to write a private `runtime.json` template. The first invocation intentionally returns a prerequisite error until real paths are configured.

```bash
export HUMAN_4D_ROOT="$HOME/physical-ai-labs/human-4d"
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" setup
```

Use [runtime.example.json](runtime.example.json) as a guide. Relative paths resolve inside `--root`. Configure:

- `python.gem`: GEM-X with its official motion/video dependencies, py-soma-x and SAM2.
- `python.reconstruction`: pinned 4DAnyone, Torch 2.8/cu128, gsplat, NumPy/SciPy/Pillow, Transformers/BiRefNet.
- `python.moge`: MoGe-3 with its pinned official requirements in a separate environment.
- `sources`, `assets`, `models`: actual checked-out sources and downloaded checkpoints; no machine address or credential belongs in this file.
- `cuda_home` and `cuda_arch`: this example uses CUDA 12.9/SM 12.0 for RTX 5090. Change them for another compatible GPU/toolchain.

The supplied requirement files document the reconstruction adapter dependencies; they do not install every upstream model's runtime. Follow the official [GEM-X install](https://github.com/NVlabs/GEM-X#quick-start), [4DAnyone install](https://github.com/ant-research/4DAnyone#installation), [SOMA assets](https://huggingface.co/nvidia/SOMA-X), [SAM2 install](https://github.com/facebookresearch/sam2#installation), and [MoGe install](https://github.com/microsoft/MoGe#installation). Keep their environments separate.

Example reconstruction environment (after obtaining the pinned sources):

```bash
uv venv --python 3.11 "$HUMAN_4D_ROOT/envs/reconstruction"
uv pip install --python "$HUMAN_4D_ROOT/envs/reconstruction/bin/python" \
  torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128
uv pip install --python "$HUMAN_4D_ROOT/envs/reconstruction/bin/python" \
  -r labs/human-4d-gaussian/requirements-reconstruction.txt
```

Download required weights from [SOURCES.md](SOURCES.md), configure paths, then rerun setup. `--fetch-sources` can fetch the pinned source revisions **inside the selected output root**. It does not download input footage or install packages globally.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" --fetch-sources setup
```

Default expected model layout:

```text
models/
  4danyone/model.safetensors
  4danyone/Wan2.2_VAE.pth
  4danyone/prompt_context.safetensors
  4danyone/Wan22_TI2V_5B_Turbo_lora_rank_64_fp16.safetensors
  birefnet/...
  moge-3/model.pt
  sam2.1_hiera_large.pt
```

The 4DAnyone downloader verifies the Turbo adapter and can obtain the optional perceptual asset under this model root. GEM's own config must point to its real motion checkpoint and detectors. Do not copy another person's absolute runtime paths into your config.

## 3. Run local reconstruction stages

The tested preset uses one portrait 9:16 person video, a static camera, normalized 30Hz timing and at least 121 frames. Original-resolution video is retained; working RGB is 540×960. Other framing and moving-camera cases require a camera adapter and are rejected rather than silently stretched.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" prepare --video "$HOME/Videos/my-motion.mp4"
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" rig
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" multiview
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" train
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" refine --seed-only
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" render
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" package
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" --deep check
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" serve
```

`multiview` runs Base24 for six seed directions and Turbo4 for six offset directions. It does not generate the full long video from every camera. `train` fits the six-direction source-preserving seed. `refine` first fits all twelve directions at higher resolution, then original ROIs and MoGe guidance. The quickstart uses `refine --seed-only` for this 121-frame interval. Removing that option selects the experimental full-motion extension; use a separate output root after inspecting the short result.

For later intervals, `refine` uses `warmstart.py --mode trajectory` to bind one shared seed snapshot to coherent SOMA material tracks, then `fit_interval.py` fits actual interval RGB/ROIs/MoGe. Velocity/time variance stay fixed while spatial covariance is optimized independently through `conditional.py`; standard native SO(4) archives are restored on save. Side/rear protected views are renders of the transferred initialization, not newly observed or newly diffused RGB. This long-sequence extension is undergoing direct GPU validation; the public control and its checks are independently executable. Review interval boundaries and RGB quality on your own result rather than interpreting a completed process as verified fidelity.

GPU stages share the configured file lock. The script keeps outputs private and does not push, upload or publish packages. Use a new root for a different video or experimental recipe. Upstream source checkpoints and previous outputs are not replaced by setup.

## 4. Rebuild the public control

Configure `python.control_export`, `python.control_render`, SOMA source and native assets. The export accepts only the pinned official animation hash.

```bash
export CONTROL_ROOT="$HOME/physical-ai-labs/soma-control"
python3 labs/human-4d-gaussian/pipeline.py --root "$CONTROL_ROOT" --mode control setup
python3 labs/human-4d-gaussian/pipeline.py --root "$CONTROL_ROOT" --mode control prepare
python3 labs/human-4d-gaussian/pipeline.py --root "$CONTROL_ROOT" --mode control rig
python3 labs/human-4d-gaussian/pipeline.py --root "$CONTROL_ROOT" --mode control render
python3 labs/human-4d-gaussian/pipeline.py --root "$CONTROL_ROOT" --mode control package
python3 labs/human-4d-gaussian/pipeline.py --root "$CONTROL_ROOT" --mode control --deep check
```

`multiview`, `train` and `refine` return an explicit error in control mode, since those stages do not occur. Full rebuild details and array layouts are in [CONTROL-SOURCES.md](CONTROL-SOURCES.md).

## Local viewing

Open the Pages lab and choose **Open a local result folder**. Select the package folder containing `manifest.json`, `source.mp4` and its model subfolders. Files are read with browser-local URLs, not uploaded. The optional `serve` command provides a loopback data URL; it does not run GPU inference or claim to host the full Pages application.
