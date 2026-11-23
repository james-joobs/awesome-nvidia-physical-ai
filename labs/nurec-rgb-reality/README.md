# RGB-only NuRec Reality View lab

[English guide](../../docs/en/labs/nurec-rgb-reality.md) · [한국어 가이드](../../docs/ko/labs/nurec-rgb-reality.md) · [Sources and licenses](SOURCES.md)

**RGB → COLMAP + rig refinement → NCore → NuRec → native renders → Harmonizer.**

In parallel, actual source RGB feeds Mask R-CNN perception and Alpamayo 2 Edge trajectory inference. A credited Volvo S90 mesh, approximate object contacts and predicted paths join a browser preview of the NuRec-trained Gaussians. The native NuRec/Harmonizer comparison is separate from browser rasterization.

No LiDAR, source calibration, source sensor poses, source timestamps, depth maps or object annotations enter reconstruction. The model history uses an explicit 1.8 m camera-height scale assumption; this is not an RGB measurement or a closed-loop driving evaluation. The camera adapter and nominal timing assumptions are documented in the guide.

GPU-free saved-result checks and viewer:

```bash
python3 labs/nurec-rgb-reality/check.py
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092
```

For one RTX 5090 on Linux, read the prerequisites and separate asset/model terms first:

```bash
export NUREC_RGB_ROOT="$HOME/physical-ai-labs/nurec-rgb-road"
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" all
```

This creates isolated environments and stores downloads, raw logs and large training artifacts outside Git. Installation and first compilation are separate from recorded execution timings. The guide also provides commands for each stage. [Standalone 3DGUT comparison](../rgb-reality-view/README.md) remains available.

The [fresh-output verification](evidence/fresh-pipeline-check.json) records a second complete run of `all`, using new Python environments on the tested host and cached runtime/model downloads. [Desktop and mobile checks](evidence/browser-check.json) cover both languages, pointer/touch input, perception, predicted paths, inline video and language switching.
