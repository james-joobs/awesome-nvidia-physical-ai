# Public model-run evidence

These products use our own simulator geometry and RGB, released model weights, and a pinned official camera-action example. No PhysicalAI-AV or NuRec recordings, scenes or benchmark metrics are included.

- `synthetic-intersection/`: 22 original Isaac Sim camera images, their timestamps and hashes, the self-contained USD scene, and a recording of the native GUI capturing those views.
- `alpamayo-synthetic/`: the actual CLI seed-19 output JSON, unchanged float32 trajectory tensors, model receipt with verified weight hashes, and `run-summary.json` copied from the complete CLI run. The reasoning output is the model's `<NOMINAL>` token.
- `prediction-scene/`: the same 64 predicted poses drawn and replayed as a cosmetic car in USD, with a CSV for inspection. This is trajectory replay, not closed-loop driving.
- `cosmos-right/` and `cosmos-left/`: image-to-video attempts. Generation finished, but the requested cube slide is not clearly visible.
- `cosmos-camera-actions/`: a 61-frame forward-dynamics result from an image and the published normalized camera-action sequence. The view changes visibly; this does not establish metric or physical accuracy.

Public MP4 copies are H.264 CRF-23 re-encodes with the original frame count, dimensions and FPS. Original model MP4s remain on the recording machine. Original and preview hashes are recorded in [`../recorded.json`](../recorded.json). The model tensors and input PNGs are unchanged.

This is a small public subset of the complete GPU run. The large packed model inputs and full runtime logs are omitted. Run the shared CLI's `verify` command against a complete run directory on the GPU machine; use the independent CPU checker below for this bundled subset. `run-summary.json` preserves the full run's original artifact references for traceability, including files that are not bundled here.

Check the saved products without a model installation:

```bash
python3 labs/world-driving/check.py \
  --cosmos labs/world-driving/evidence/cosmos-camera-actions \
  --alpamayo labs/world-driving/evidence/alpamayo-synthetic
```

Model and code terms are linked in [`../model-pins.json`](../model-pins.json). The setup script downloads weights into an external experiment folder; weights are not part of this repository.
