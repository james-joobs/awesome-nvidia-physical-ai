# RGB-only Reality View lab

[English guide](../../docs/en/labs/rgb-reality-view.md) · [한국어 가이드](../../docs/ko/labs/rgb-reality-view.md) · [Data and asset terms](SOURCES.md)

**RGB images → COLMAP → NVIDIA 3DGUT → a persistent 3D road you can orbit with a mouse.**

The viewer also shows **actual Mask R-CNN detections and instance masks** on source RGB, with approximate road-plane contact markers in 3D. Toggle recognition and switch camera direction to inspect the evidence.

The tested preset uses one RTX 5090 32 GB on Linux. No LiDAR, supplied depth, calibration, camera poses, GPS, IMU or gated pretrained weights enter reconstruction. The example uses 162 RGB images and estimates cameras from image matches. The Volvo S90 is a credited, simplified 3D mesh added as an ego-position reference.

```bash
export RGB_VIEW_ROOT="$HOME/physical-ai-labs/rgb-road"
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" all
```

First install the prerequisites in the guide: a working NVIDIA driver, CUDA development toolkit 12.8/12.9, C++ compiler, Git, Python, uv and Node.js/npm. Setup creates isolated environments and builds extensions. It can take much longer than training. Read the example's dataset terms before downloading.

Open **http://127.0.0.1:8090/** after export. Drag to orbit, right-drag to pan, scroll/pinch to zoom. Use Driver for the estimated capture camera; Play path replays estimated camera positions.

Bring your own RGB footage, in a fresh output folder:

```bash
python3 labs/rgb-reality-view/pipeline.py \
  --root "$HOME/physical-ai-labs/my-road" \
  --video "/absolute/path/to/road.mp4" --sample-fps 3 all
```

Overlapping translated views, textured roads and mostly static surroundings help SfM. A forward camera cannot recover unseen rear surfaces. Scale is relative; the road plane comes from RGB feature tracks. This is offline static reconstruction, not live perception, dynamic world prediction or vehicle control.

Without a CUDA GPU, inspect the saved results:

```bash
python3 labs/rgb-reality-view/check.py
python3 labs/rgb-reality-view/check.py --decode-video
python3 -m unittest discover -s labs/rgb-reality-view -p 'test_*.py'
```

Open the bundled 3D scene without training (internet needed for pinned viewer modules):

```bash
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/rgb-reality-view
```

Then visit **http://127.0.0.1:8090/**.

The optional video check needs FFmpeg. [recorded.json](recorded.json) contains measured runtimes, GPU-memory sampling scope and hashes. The browser model is in [site/public/showcase/rgb-reality-view](../../site/public/showcase/rgb-reality-view/); bilingual recordings are in [evidence](evidence/). Raw machine logs stay outside public artifacts.

`record_tour.mjs` records actual mouse, wheel and button interactions with optional Playwright 1.60.0 and Chrome. `package_tour.py` adds English/Korean captions with FFmpeg, Pillow and a font you supply. No pre-rendered camera sequence replaces the interaction.

For an existing reconstructed output, add perception without retraining:

```bash
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" perceive
```

This downloads the pinned public COCO detector weights on first use. Its source/weights terms are documented separately in SOURCES.md. No dataset annotations or LiDAR are used. The saved recognition video is [English](evidence/rgb-perception.en.mp4) / [한국어](evidence/rgb-perception.ko.mp4).
