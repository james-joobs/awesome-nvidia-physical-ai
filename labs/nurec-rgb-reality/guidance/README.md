# RGB geometry guidance for NuRec

[English walkthrough](../../../docs/en/labs/nurec-rgb-reality.md#6-reduce-smearing-with-rgb-predicted-depth) · [한국어 실습](../../../docs/ko/labs/nurec-rgb-reality.md#6-rgb에서-추정한-깊이로-번짐-줄이기) · [Sources and terms](../SOURCES.md)

DA3-BASE predicts training-image depth. RGB-triangulated training points align its scale and shift. Ray-distance and derived world-normal targets feed the pinned NuRec runtime's native differentiable losses. Inputs remain RGB-only; predicted priors are not measured depth.

| Module | Responsibility |
| --- | --- |
| `pipeline.py`, `setup.py` | Isolated environment and one-stage-at-a-time commands |
| `make_inputs.py` | Timestamp split and training-only seed triangulation/coloring |
| `infer_priors.py`, `geometry.py` | Pinned/checksummed depth inference, robust alignment, normal derivation and masks |
| `train.py`, `scene.yaml` | Independent native-runtime adapter and geometry-loss configuration |
| `run_experiment.py`, `evaluate.py` | Matched-budget training, exact-resolution rendering and held-out RGB metrics |
| `dense_seed.py` | Optional RGB/depth/normal cross-view checks for a denser initialization |
| `export_model.py`, `package_viewer.py` | Official NuRec PLY export, SPZ conversion and local viewer packaging |
| `render_comparison.py` | Original/production native renders at identical scripted novel cameras |
| `collect_evidence.py`, `check.py` | Portable numeric receipts and CUDA-free saved-result verification |

Keep **two fresh output folders**. The held-out comparison uses 138 training images, 24 test images, 16k steps, seed 42 and a 450k-Gaussian limit. Camera estimation uses all RGB offline, so this is a fixed-camera image comparison. The production fit uses all 162 images, denser initialization, 32k steps and a 1.2M limit; it has no independent held-out score.

`all` runs the three original ablations. `--variant depth-normal-soft` is a follow-up after inspecting those results. Geometric regularization can reduce RGB fidelity; the saved experiment does not claim that all normal weights help.

Own adapter code is MIT. DA3 code and the selected BASE weights are Apache-2.0. NuRec runtime, dataset and vehicle terms are separate. No runtime source, model weights or machine logs are redistributed here.
