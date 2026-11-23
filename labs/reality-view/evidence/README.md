# Recorded neural road-view experiment

[English guide](../../../docs/en/labs/reality-view.md) · [한국어 실습](../../../docs/ko/labs/reality-view.md) · [Measured receipt](../recorded.json)

| File | What it contains |
|---|---|
| `reality-view.en.mp4`, `reality-view.ko.mp4` | 20-second comparison and route display, English/Korean captions |
| `nurec-novel.mp4` | NuRec renders at 40 held-out camera poses, played over 8 seconds |
| `harmonizer-novel.mp4` | The same views after the official non-temporal Harmonizer checkpoint |
| `alpamayo-overlay.mp4` | One actual Alpamayo 2 Edge prediction projected onto a display camera and BEV |
| `frames/` | Three lossless reference / NuRec / Harmonizer triplets for independent CPU checks |
| `trajectory.json` | All 64 predicted positions and rotation matrices; frame and units included |

The input scene is our own primitive-only USD road. No NVIDIA PhysicalAI-AV/NuRec dataset content or pretrained model weights are included. Rendering, per-frame enhancement, and a single predicted trajectory are distinct stages; the videos do not demonstrate closed-loop vehicle control. Playback speed is edited.

Whole-frame held-out PSNR is 29.21 dB for NuRec and 27.09 dB after Harmonizer. The latter reduces pixel fidelity in this small synthetic scene. Use the supplied originals to inspect the changed lane and ground boundaries.

**Built on NVIDIA Cosmos.** Harmonizer weights are obtained separately under the NVIDIA Open Model License; Alpamayo 2 Edge weights use OpenMDW-1.1. Our scripts follow the repository license. See [pinned sources and model terms](../model-pins.json).
