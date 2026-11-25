# Joint RGB geometry for Reality View

[한국어](README.ko.md) · [Parent lab](../README.md) · [Saved-output check](check.py)

Use a public model to obtain **RGB, depth and cameras together**, then inspect a time-indexed 3D surface. Aether is the closest tested generative alternative to WorldLatent. DA3-BASE provides the more useful geometry branch for this road clip. They are different models; neither output is called WorldLatent or a WorldVAE latent.

The parent lab's 3D viewer, NuRec checkpoint, Harmonizer service, source-RGB recognition and Alpamayo path remain available. This experiment adds frame-local RGB-D geometry rather than replacing the static Gaussian model.

## What actually ran

One RTX 5090, sequential jobs, BF16 Aether; DA3's existing isolated Torch2.8/CUDA12.8 environment. No LiDAR, imported sensor calibration/poses/timestamps, or measured depth.

| Experiment | Input and output | Offline inference | Peak allocated GPU memory |
|---|---|---:|---:|
| Aether reconstruction | 17 front RGB, 720×480 → decoded RGB, disparity, camera rays | 21.40 s | 14.58 GiB |
| Aether prediction | First RGB + camera rays estimated by the previous pass → 17 predicted RGB/depth/ray frames, 50 steps | 80.24 s | 14.57 GiB |
| DA3-BASE joint | Same17 front crops, processed at756×504 → depth, confidence, cameras | 4.50 s | 4.78 GiB |
| DA3-BASE surround | 6 RGB cameras ×17 nominal times, processed at504×280; no camera priors | 3.41 s | 5.96 GiB |
| DA3-BASE surround + RGB camera priors | Same102 source views,756×420, cameras estimated earlier from RGB/SfM | 6.33 s | 11.29 GiB |

These are single-run offline measurements, not live camera-to-display throughput. The last run processes102 **views**, representing17 times; it does not produce102 new time steps. Model load, installation, initial compilation, camera recovery, serialization, network and browser rendering are excluded from inference timings. DA3 measurements include its image processing and prediction conversion. Resolution, runtime and camera conditioning differ between rows. Do not rank speed or quality from this table alone.

The portable Aether image below was independently built and run:22.74 s,14.58 GiB; its decoded RGB, disparity and ray maps were **raw-array identical** to the first reconstruction run. All earlier outputs are preserved outside Git.

## Start in a browser

Open **Explore a real road in 3D** in the parent lab and press **Start 3D**. The default keeps a 3DGS background with time-local vehicles; [that composition is explained separately](../dense/README.md). Use **Compare → Depth reconstruction** for the original RGB-D experiments:

1. **DA3-BASE · RGB/SfM camera priors:** six current-time depth surfaces; better camera anchoring, not a camera-pose accuracy test.
2. **DA3-BASE ·6 RGB cameras:** jointly estimated depth and cameras without camera priors. Wider coverage, but larger camera drift in this clip.
3. **DA3-BASE · front RGB / AetherV1 · front RGB:** the same 17 front crops. Compare model behavior with fewer observations.
4. **NuRec:** the existing static3DGS trained from a longer multi-camera clip. Better persistent appearance in some views; moving traffic can ghost.

Choose a source camera, drag to orbit, scrub time, and click an RGB pixel. The displayed Z-depth and3D coordinate come from the actual saved model output. A source-RGB texture is attached to each depth mesh. Six current-time surfaces are shown together; we do not accumulate moving cars across time. Unobserved sides and uncertain boundaries remain incomplete. The static Gaussian comparison uses a different data/training budget and is not a matched model benchmark.

One first-camera orientation and one positive scale align each new sequence to the existing RGB/SfM display frame. No per-frame correction is applied. The reference is itself an RGB estimate. Front-only DA3 and Aether camera-center agreement is0.685% and2.290% of the reference path length; rotation disagreement is1.06° and5.31° median. These are **reference agreement**, not ground-truth camera accuracy. The pose-conditioned run inherits its camera prior, so its near-zero disagreement must not be presented as independent accuracy.

## Understand the data

```text
RGB uint8[N,H,W,3]
    ├─ Aether: shared diffusion transformer
    │    ├─ decoded RGB [N,H,W,3]
    │    ├─ disparity [N,H,W] → depth =1/disparity
    │    └─ rays [N,6,H/8,W/8] → camera-to-world + intrinsics
    └─ DA3: depth-ray transformer
         ├─ Z-depth float[N,H,W]
         ├─ confidence float[N,H,W]
         └─ world-to-camera [N,3,4] + K [N,3,3]
                   ↓ invert pose, unproject depth
             frame-local 3D points / RGB-textured mesh
```

For the prior-conditioned surround pass, `N=102`, `H=420`, `W=756`. `N` is17 times ×6 RGB cameras, not a neural latent channel dimension. Aether uses direction plus signed-log camera origin; these six channels are **not Plücker direction/moment channels**. Always use its official postprocessor. WorldLatent's unpublished decoder conventions cannot be assumed to match.

A real saved front-camera pixel at nominal2.4 s:

```json
{
  "view_index": 49,
  "pixel_xy": [378, 350],
  "rgb_uint8": [70, 73, 80],
  "z_depth_relative": 3.82502,
  "focal_pixels": [779.25244, 779.70190],
  "camera_xyz_relative": [0.00000, 0.68680, 3.82502],
  "world_xyz_relative": [-4.29220, 0.03739, 0.22340]
}
```

Depth is measured along the camera's forward Z-axis, not along the slanted pixel ray. With focal lengths `fx,fy` and principal point `cx,cy`, calculate `X=(u-cx)Z/fx`, `Y=(v-cy)Z/fy`. Then camera-to-world rotation/translation places that point in the scene. Its unit is relative, not measured meters. Confidence is a model score, not a calibrated probability.

For compact viewing, depth is sampled every2 or3 pixels, range-limited to0.1–80 relative display units, and stored as little-endian uint16. The bottom15th percentile of DA3 confidence per view is hidden. Triangles crossing a>10% depth discontinuity are omitted. The actual full-precision geometry remains in the run directory. The browser's frame cadence is separate from the saved nominal3.33Hz observations.

## Reproduce on Linux with one NVIDIA GPU

First follow the [parent RGB reconstruction setup](../README.md). The source folder must contain undistorted RGB camera subfolders. Keep all runtime inputs, checkpoints and raw logs outside Git. Read [model/data terms](#sources-and-terms) before downloading.

```bash
export RV_JOINT_ROOT="$HOME/physical-ai-labs/reality-joint"
export RV_RGB_IMAGES="/path/to/undistorted/images"
mkdir -p "$RV_JOINT_ROOT"
python3 labs/nurec-rgb-reality/unified/prepare_inputs.py \
  --images "$RV_RGB_IMAGES" --out "$RV_JOINT_ROOT/inputs"
```

This selects00/03/…/48 from six RGB cameras. Filename/10 is the parent lab's nominal timing assumption. It does not read sensor timestamps. It creates distinct front/full, front/crop and surround input sets with hashes.

Aether uses its original public pipeline and pinned weights. Its portable image supports RTX5090 via the pinned NVIDIA PyTorch/CUDA13 base:

```bash
git clone https://github.com/Sage-PhysicalAI/Aether.git "$RV_JOINT_ROOT/Aether"
git -C "$RV_JOINT_ROOT/Aether" checkout 871c6f7ebcd66f3571ed27db5d65264a51d624a3
docker build -t physical-ai-aether:portable-20261125 labs/nurec-rgb-reality/unified
export RV_JOINT_ADAPTERS="$PWD/labs/nurec-rgb-reality/unified"
docker run --rm -v "$RV_JOINT_ROOT:/workspace" -v "$RV_JOINT_ADAPTERS:/adapters:ro" \
  physical-ai-aether:portable-20261125 python /adapters/download_models.py
flock /tmp/rgb-reality-view.gpu.lock docker run --rm --gpus device=0 --shm-size=4g \
  -e OMP_NUM_THREADS=8 -e TOKENIZERS_PARALLELISM=false \
  -v "$RV_JOINT_ROOT:/workspace" -v "$RV_JOINT_ADAPTERS:/adapters:ro" \
  physical-ai-aether:portable-20261125 python /adapters/run_aether.py \
  --upstream /workspace/Aether --models /workspace/models \
  --images /workspace/inputs/front-full --out /workspace/aether-reconstruction
```

The real empty T5 text embedding is calculated by the official constructor. The text encoder is then released; the embedding is not replaced with zeros. VAE slicing/tiling is enabled. No quantization or changed weights were used. `geometry.npz` contains observed RGB, decoded RGB, depth, points and cameras; `raw.npz` retains the original decoded disparity/rays.

DA3 uses the already documented [isolated DA3 setup](../guidance/setup.py). Choose a fresh runtime root if you do not already have that environment:

```bash
export RV_DA3_ROOT="$HOME/physical-ai-labs/reality-da3"
python3 labs/nurec-rgb-reality/guidance/setup.py --root "$RV_DA3_ROOT"
flock /tmp/rgb-reality-view.gpu.lock "$RV_DA3_ROOT/.venv/bin/python" \
  labs/nurec-rgb-reality/unified/run_da3.py \
  --images "$RV_JOINT_ROOT/inputs/front-crop" --out "$RV_JOINT_ROOT/da3-front" \
  --frames 17 --resolution 756 --ray-pose
flock /tmp/rgb-reality-view.gpu.lock "$RV_DA3_ROOT/.venv/bin/python" \
  labs/nurec-rgb-reality/unified/run_da3.py \
  --images "$RV_JOINT_ROOT/inputs/surround" --out "$RV_JOINT_ROOT/da3-surround" \
  --frames 102 --resolution 504 --ray-pose
```

To use only **RGB-estimated** camera priors, complete the parent [guidance input stage](../guidance/make_inputs.py), then run the surround command at `--resolution 756` with `--camera-priors /path/to/all-cameras.json` and a fresh `--out`. The runner rejects metadata indicating LiDAR or supplied sensor calibration/poses. This camera-conditioned mode does not independently estimate camera accuracy.

For the separate generative experiment, repeat the Aether command with a fresh output, `--steps 50` and `--camera-from /workspace/aether-reconstruction/geometry.npz`. It receives only the first image plus cameras estimated from all17 images in the prior reconstruction pass. Those camera estimates are not ground truth and this is not blind future prediction. Cars and lights may change or disappear. Do not feed generated pixels into the perception or driving-policy evaluation as verified evidence.

Export the tested clip into a **fresh** folder:

```bash
python3 labs/nurec-rgb-reality/unified/export_viewer.py \
  --aether "$RV_JOINT_ROOT/aether-reconstruction" --da3 "$RV_JOINT_ROOT/da3-front" \
  --surround "$RV_JOINT_ROOT/da3-surround" \
  --reference site/public/showcase/nurec-rgb-reality/cameras.json \
  --out "$RV_JOINT_ROOT/viewer-export"
python3 labs/nurec-rgb-reality/unified/check.py
python3 -m unittest discover -s labs/nurec-rgb-reality/unified -p 'test_*.py'
```

The reference file above belongs to this exact recorded clip. A different video needs its own camera/time reference and vehicle placement; do not reuse this clip's alignment or claim metric scale. The GPU-free check validates the repository's saved outputs and checksums; it is not a quality benchmark of a new private run.

## Sources and terms

- [Aether code / MIT](https://github.com/Sage-PhysicalAI/Aether), [AetherV1 weights / MIT card](https://huggingface.co/AetherWorldModel/AetherV1). CogVideoX VAE/text encoder use [separate CogVideoX terms](https://huggingface.co/zai-org/CogVideoX-5b-I2V/blob/main/LICENSE): research use; commercial registration/authorization required.
- [DA3 code](https://github.com/ByteDance-Seed/Depth-Anything-3), [DA3-BASE weights](https://huggingface.co/depth-anything/DA3-BASE): Apache-2.0 for this checkpoint. Larger DA3 variants have different terms.
- [DeepVerse code](https://github.com/SOTAMak1r/DeepVerse), [DeepVerse1.1 weights](https://huggingface.co/SOTAMak1r/DeepVerse1.1): another released autoregressive RGB/depth/action world-model candidate. The weights card declares MIT; the code repository has no separate license file in the inspected tree, and inherited SD3/Pyramid-Flow terms need separate review. Its official instructions recommend disabling depth for action control on non-game/OOD images. Researched, not executed or selected for this real-road geometry branch.
- [Pi3X](https://huggingface.co/yyfz233/Pi3X): another released joint geometry/camera candidate; code BSD-3-Clause, weights CC BY-NC4.0. Researched, not executed here; not an RGB generative world model.
- [WorldMirror license](https://github.com/Tencent-Hunyuan/HunyuanWorld-Mirror/blob/main/License.txt) excludes South Korea, EU and UK; not executed/selected for this deployment.
- [WorldLatent official project](https://worldlatent.github.io/): separate research reference. No actual WorldLatent weights were available in the earlier official-source audit; nothing here simulates having run its14B model.
- [Data, NuRec, Harmonizer, Alpamayo and Volvo terms](../SOURCES.md). Source-RGB Mask R-CNN and Alpamayo results remain in the original parent viewer. No new model weights are redistributed.

Our adapters are MIT. RGB derivatives and recordings retain the parent PandaSet **CC BY-SA4.0 + original Dataset Terms** treatment. [Display asset credits](../../../site/public/showcase/reality-joint-geometry/ATTRIBUTION.txt).
