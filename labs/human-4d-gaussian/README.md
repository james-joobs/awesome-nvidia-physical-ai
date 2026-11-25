# Human 4D Gaussian lab

[한국어](README.ko.md) · [Full learning guide](../../docs/en/labs/human-4d-gaussian.md) · [Sources and terms](SOURCES.md)

This folder provides real stage adapters for two routes:

- **Known-geometry control:** official SOMA example motion → native Warp skinning → synthetic RGB and per-vertex Gaussians. No monocular learning is claimed.
- **Local monocular reconstruction:** local video → official GEM-X motion-video → SOMA/SAM2 → source-preserving 4DAnyone seed → original face/hand and MoGe guidance → fresh multiview fitting for later intervals → native/browser rendering.

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

`multiview` runs Base24 for six seed directions and Turbo4 for six offset directions. It does not generate the full long video from every camera. `train` fits the six-direction source-preserving seed. `refine` first fits all twelve directions at higher resolution, then original ROIs and MoGe guidance. The quickstart uses `refine --seed-only` for this 121-frame interval. Then use the separate `extend` stage for the full-motion exercise.

For a longer clip, complete the short seed and run the explicit `extend` stage. It generates twelve new views per later interval (six Turbo4 views plus six Turbo4 offsets), fits a new native model, adds high-resolution RGB, original face/hand ROIs and MoGe-3 guidance, then checks the selected checkpoint. This differs from the seed's Base24-plus-Turbo generation. Internal 121-frame windows advance by 120 frames; padding never extends playback.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" extend
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" render
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  --package-dir "$HUMAN_4D_ROOT/package-full" package
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  --package-dir "$HUMAN_4D_ROOT/package-full" --deep check
```

A full timeline is written only after every interval completes. Stage journals match inputs, runtime configuration, adapter code and output hashes before reuse. Rerun the same command after an interruption; changed inputs or conditions require a separate output root. Renders are stored under `renders/<model-and-renderer-hash>` so the full result does not replace the short one. The `package-full` output contains the complete timeline for web integration.

The older `refine --trajectory-experiment` path binds a shared seed snapshot to SOMA material tracks and fits observed-only later intervals through the stable conditional factorization. It remains an explicitly selected comparison: it produced more smearing than fresh multiview fitting. Plain `refine` and `refine --seed-only` complete the short seed; neither silently starts the experimental transfer route.

GPU stages share the configured file lock. The script keeps outputs private and does not push, upload or publish packages. Use a new root for a different video or experimental recipe. Upstream source checkpoints and previous outputs are not replaced by setup.

### Inspect inputs before fitting a long interval

`inspect_masks.py --root "$HUMAN_4D_ROOT"` compares predicted foreground coverage with the estimated SOMA head projection. Its `coverage.json` and contact sheets are review aids, not ground truth or a whole-body segmentation accuracy score. A high masked RGB score can hide a face that the mask incorrectly removed.

For a later interval, generate its two teacher sets before fitting:

Use the actual `python.reconstruction` executable from `runtime.json` in place of `RECON_PY`:

```bash
RECON_PY="$HUMAN_4D_ROOT/envs/reconstruction/bin/python"
export CUDA_HOME=/usr/local/cuda-12.9
export PATH="$CUDA_HOME/bin:$PATH"
export TORCH_CUDA_ARCH_LIST=12.0
flock "$HUMAN_4D_ROOT/.gpu.lock" "$RECON_PY" labs/human-4d-gaussian/fresh_interval.py \
  --root "$HUMAN_4D_ROOT" --name s01 --start 120 --views-only
"$RECON_PY" labs/human-4d-gaussian/inspect_teachers.py --root "$HUMAN_4D_ROOT" \
  --name s01 --out "$HUMAN_4D_ROOT/diagnostics/s01-base.jpg"
"$RECON_PY" labs/human-4d-gaussian/inspect_teachers.py --root "$HUMAN_4D_ROOT" \
  --name s01 --offset --out "$HUMAN_4D_ROOT/diagnostics/s01-offset.jpg"
```

Run this direct GPU helper inside the same configured GPU lock and CUDA environment as the main pipeline; it deliberately does not acquire a second lock. Its default step counts must match the runtime configuration when subsequently using `extend`. `--views-only` writes an awaiting-review state without claiming a trained checkpoint. Repeating the same helper command without that flag verifies cached inputs and continues fitting.

More directions are not always better: inspect all six base and six offset views at their first, middle and last frames. A frontal face in a camera labeled 180° is a contradictory target even when source-camera PSNR looks good. `--exclude-base-cameras 3` explicitly omits base camera 3; it retains contiguous camera slots, maps geometry guidance to the retained views, and records generated versus accepted counts. Only the exclusion list may change while the interval is explicitly awaiting teacher review and fitting has not started; the previous recipe is retained. After fitting starts, changed exclusions need a new interval name/output root. Changed seeds or generator profiles always need a separate experiment. Old checkpoints remain unchanged. Direct helper experiments are not silently selected into an existing `models.json`.

`repair_foreground.py --help` documents an optional, manually selected mask correction: it intersects foreground masks warped from both adjacent RGB frames, adds their agreement only near the estimated head, and creates new training data plus original-pixel edge ROIs. It does not edit original masks, download imagery, change the renderer, or automatically decide that a correction is valid. Review the corrected mask and retrain a separate candidate before selecting it.

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

## Inspect your result

Inspect the generated comparison videos under `renders`. The package contains `manifest.json`, model data and the motion timeline for integration with a web frontend. The optional `serve` command exposes these package files over loopback HTTP.

Optional `source_credit` and `source_reference_url` in `runtime.json` carry your input attribution into the selected model inventory and browser package; the native comparison also prints the credit. Use an ASCII credit or a compatible installed font for native video text.

## Published reconstruction / 공개 재구성 결과

[English](https://james-joobs.github.io/awesome-nvidia-physical-ai/labs/human-4d-gaussian/#explore) · [한국어](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/labs/human-4d-gaussian/#explore)

31.9s /957 frames /8 conditional 4D intervals. A reduced browser subset and full-quality native orbit video are published with derivative permission confirmed by the maintainer. Original footage/audio stay in the official YouTube player. The synthetic SOMA control remains separate.

```bash
python3 labs/human-4d-gaussian/check_published.py --deep
```

This checks the published model hashes, complete timeline and retained-parameter numeric parity without a CUDA GPU. `publish_package.py` requires a separate local permission receipt, excludes source footage/audio and refuses to overwrite an existing export. It does not upload or push anything. [Sources and usage scope](SOURCES.md).
