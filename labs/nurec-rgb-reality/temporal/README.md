# Temporal Reality View: reproduce the RGB-only demo

[한국어](README.ko.md) · [Full lesson](../../../docs/en/labs/nurec-rgb-reality.md) · [Sources and terms](../SOURCES.md)

The geometric anchor is an RGB-reconstructed NuRec scene. Harmonizer conditions the current render on four previous enhanced outputs. Perception and Alpamayo use original camera pixels; their display overlays are applied after generation. **Built on NVIDIA Cosmos.** This is an offline reconstruction with optional live image enhancement, not a Tesla implementation or vehicle controller.

## Inspect saved results first

```bash
python3 labs/nurec-rgb-reality/temporal/check.py
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092
```

Open **http://127.0.0.1:8092/**. Choose the improved model, rotate around the Volvo, switch to the driver view and inspect RGB detections and the estimated path. The support variant colors Gaussian centers by agreement with predicted RGB depth: red 0 / amber 1 / teal 2+ distinct named cameras. It preserves geometry; it is not measured visibility or a hallucination detector. Saved checks require no CUDA GPU or model download.

## Generate a matched V1/V5 comparison

Use Linux x86_64, Python **3.12+**, uv, Docker with NVIDIA Container Toolkit, Git and `flock`. Follow the [GPU onboarding](../../../docs/en/onboarding/nvidia-linux.md) and parent lab first. Commands run from the repository root. Check available disk space: the public checkpoint is about 5 GB, with additional container, cache and output storage.

```bash
export NUREC_RGB_ROOT="$HOME/physical-ai-labs/nurec-rgb-road"
export RV_TEMPORAL_ROOT="$HOME/physical-ai-labs/reality-temporal"
export RV_INPUT="$NUREC_RGB_ROOT/renders/orbit/front_camera"
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" setup
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" --input "$RV_INPUT" compare
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" --input "$RV_INPUT" evaluate
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" check
```

`RV_INPUT` must contain ordered 16:9 PNG/JPEG files from one continuous rendered camera path. Use `--max-frames 6` before `compare` for a short GPU test, with a fresh `--comparison-dir` inside the runtime root. At least six frames are needed to evaluate actual four-output context. Output folders are never silently reused. For multiple shots, invoke `enhance.py --cut-frames` inside the same container environment or process each continuous shot separately.

Setup pins official source, the Cosmos dependency revision, NVIDIA PyTorch base image and public model revision/hash. It downloads **only** `nvidia/Harmonizer/diffusion_harmonizer.pkl`. The released file contains the complete live DiT and VAE weights; `standalone.py` initializes from these components, remaps wrapper names and checks every learned parameter against the released tensor after dtype conversion. There is no gated Cosmos-base download. Architectural nonlearned buffers follow the pinned implementation. Generated component caches stay private and are not redistributed.

The checked pipeline uses upstream code commit `826c1998796e024bc82c9843b3ec515c50737573` and model revision `20ca33d4612b1e98e0526b3a7ee604af5b289f58`; the source and model have **separate licenses**. Download only the pinned trusted checkpoint: pickle deserialization executes code.

### Reproduce the published 160-frame path

Complete the parent reconstruction, and the depth-guidance **production** stages through `train` and `export` in a separate folder, as explained in the lesson. Then render both original and production artifacts using the same 160-sample camera paths:

```bash
export RGB_GUIDED_PROD="$HOME/physical-ai-labs/nurec-guidance-production"
uv run --no-project --with numpy --with scipy python labs/nurec-rgb-reality/guidance/render_comparison.py --root "$RGB_GUIDED_PROD" --reference "$NUREC_RGB_ROOT"
export RV_INPUT="$RGB_GUIDED_PROD/preview/guided-orbit/front_camera"
```

Use this `RV_INPUT` with the comparison commands in a **fresh** output directory. The 160 frames are additional rendered camera samples, not additional camera observations. The published inference runs used 1024×576, BF16, seed 42 and timestep 250. The portable setup, six-frame V1/V5 GPU comparison and CPU evaluation were exercised on the GPU host; the 160-frame GPU run and live viewer use the same adapters and full parameter verification.

## Use the live viewer

On the GPU machine, keep this command running in its own terminal. It holds the shared GPU lock and keeps the model loaded:

```bash
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" serve
```

The service binds **127.0.0.1:8765**, not a public interface. For a separate laptop, open another terminal and forward that loopback port. Replace `GPU_HOST` with your own SSH alias:

```bash
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 GPU_HOST
```

On the laptop, start the allowlisted viewer with its explicit local proxy:

```bash
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092 --enhancer-url http://127.0.0.1:8765
```

Open **http://127.0.0.1:8092/?lang=en**, load the scene and select **Enhance this view**. Once four previous outputs exist, the receipt changes from `0/4` to `4/4`. Small mouse changes retain history; large jumps clear it to avoid reusing old geometry. **Update continuously** is opt-in, serial and captures the latest view after the previous response. It is an asynchronous preview, not 36 fps diffusion. The current service retains at most two local sessions.

The current clean 3D render is the model input. Source-RGB detection contacts and the open-loop Alpamayo path are projected into that same crop and drawn on both panels **after** enhancement; they never become claims inferred from generated pixels. Public static Pages has no backend endpoint and makes no localhost inference requests.

## Inspect and record

- `comparison/{independent,temporal}/result.json`: source/output hashes, actual history length, per-frame synchronized model latency and exact parameter coverage.
- `comparison/evaluation.json`: shared native optical flow, forward/backward validity check and V1/V5 warp error plus edge magnitude. Smoothing can improve the proxy; this is not unseen-view accuracy.
- `live-captures/`: private clean input/output images and view receipts. Review before publishing; do not commit raw runtime folders.

```bash
python3 -m unittest discover -s labs/nurec-rgb-reality/temporal -p 'test_*.py'
node labs/nurec-rgb-reality/temporal/record_viewer.mjs --language en --url 'http://127.0.0.1:8092/?lang=en' --output ./runs/local-temporal-recording
```

The geometry tests need NumPy; use an isolated environment. Recording requires Chrome and Playwright, or an installed module supplied through `PLAYWRIGHT_MODULE`. It checks real GPU responses, small mouse rotation, history initialization/reset and the mobile layout; no fake inference is inserted. Keep recording output under the ignored `runs/` directory.

The scene remains static, RGB scale is relative, occluded surfaces are unverified and source camera adaptation is approximate. [Measured results, limitations and source data](../../../docs/en/labs/nurec-rgb-reality.md#check-the-result).
