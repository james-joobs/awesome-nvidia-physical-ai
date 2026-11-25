# Human 4D Gaussian Reconstruction from Monocular Video

[한국어](../../ko/labs/human-4d-gaussian.md) · [Lab source](../../../labs/human-4d-gaussian/) · [NVIDIA GPU setup](../onboarding/nvidia-linux.md)

Estimate human motion from one camera, then learn a Gaussian representation that changes over time. Follow **RGB frames → human motion → generated views → 4D reconstruction → browser rendering**. Separate camera movement from time playback to understand how a 4D model differs from a video.

The reference is [“체포하겠어🚨🚨” on YouTube Shorts](https://www.youtube.com/shorts/rWS8uli1-m0), published by **지숭이_Jisoong**. The original opens through YouTube's official player. Public examples carry their own source and usage notes. You can load your own video and model files locally to follow the lab.

The **31.9s dance reconstruction** is now available in the browser, with permission to publish the 3D/4D derivative results confirmed. Original footage and audio remain in the official YouTube player. The existing **synthetic SOMA rig control** is preserved as a separate example. Follow the GPU lab below to reconstruct a video you can use.

## How it works

![Observed RGB, estimated motion, generated views and depth/normal guidance enter a time-conditioned Gaussian model, then render from an interactive camera](../../../assets/lessons/human-4d-gaussian/pipeline.en.svg)

### 1. What you will learn

| Stage | What to inspect | Data passed to the next stage |
| --- | --- | --- |
| Video and time | How resolution, FPS and frame indices affect motion playback | RGB frames and indices/times from the shared 30Hz input |
| Human motion | The difference between joints, skin deformation and camera coordinates | 3D joints, SOMA deformation matrices and estimated cameras |
| View generation | How a model estimates side and rear appearance at the same pose | Per-camera RGB and predicted foreground masks |
| 4D reconstruction | How position, time, volume and appearance are optimized together | A time-conditioned Gaussian model |
| Detail and geometry | Where original face/hand pixels and inferred depth/normals enter training | Refined models and comparison records |
| Validation | How to distinguish observation, reconstruction and generation | Synchronized recordings, a browser model and checks |

The NVIDIA components are **GEM-X and SOMA for motion estimation and human representation**. Ant Research's 4DAnyone generates additional views, Microsoft's MoGe-3 predicts depth/normals, gsplat renders Gaussians, and Spark/Three.js displays them in the browser. Their connection here is this repository's implementation, not an official integrated NVIDIA product.

### 2. What do RGB and 3D joints contain?

An RGB image is a `uint8[height, width, 3]` array. Its three values describe red, green and blue. Video adds a **frame index and time**. Comparing mismatched times can make a correctly moving hand look like a reconstruction error.

GEM-X estimates body and hand poses. SOMA expresses those poses using human geometry and skin deformation. The tested configuration produces the following arrays, where `T` is the processed frame count.

```text
rgb:          uint8[T, H, W, 3]        observed camera color
times:        float[T]                 frame times in seconds
joints:       float[T, 77, 3]          estimated joint XYZ
deformations: float[T, 110, 4, 4]      SOMA skin-deformation matrices
K:            float[T, 3, 3]          estimated camera intrinsics
```

**The 77 joints and 110 skinning bones are different arrays.** Estimated motion is not motion-capture ground truth. Camera focal length and body scale can also differ from physical measurements. The final output is a learned 4D Gaussian representation, rather than a conventional skeletal-animation export.

### 3. Where do side and rear views come from?

A predicted mask separates the person from the source background. Estimated motion is projected into virtual cameras to create skeleton conditioning videos. 4DAnyone reads the source RGB and those conditions to generate other appearances.

```text
source RGB + the same estimated motion
  → skeleton video for each virtual camera
  → 4DAnyone multiview generation
  → per-view RGB + predicted foreground mask
```

Each virtual `K[3,3]` and `camera_to_world[4,4]` records an **intended viewpoint**. Generation is not guaranteed to obey that camera or pose exactly. If faces, clothing or feet disagree across generated views, fitting them together can create overlapping or smeared 3D appearance.

The joint 12-view experiment uses shared RCP references and TCR links between view groups. The official implementation connects two six-view groups; this is different from twelve unrelated generation calls. **Observed RGB remains the source camera's training target.** It is not replaced by a generated front view. Unobserved clothing backs and hair remain generated estimates.

The runner's default reproduction preset follows the selected appearance prior: **six Base24 directions plus six separately generated Turbo4 offset directions**. Joint 12-view generation is a separate comparison. These are not presented as the same generation condition.

### 4. How does a 4D Gaussian move?

A Gaussian is a soft particle with a center, size/orientation, opacity and color. Adding time describes **where it appears at a query time and how visible it is**.

```text
stored model
  position/time center + space/time covariance + opacity + SH color
       ↓ query time t
  evaluate the 3D center, volume and temporal opacity
       ↓ user-selected camera
  project and composite the particles → RGB
```

In the model archive, `xyz[N,3]` stores particle centers and `time[N,1]` stores their temporal centers. Degree-3 DC and SH appearance together form `color_coefficients[N,16,3]`. **`N` counts particles; `T` counts video frames.** Particles do not all contribute equally at every time.

This implementation conditions the joint space-time distribution on the requested time. Each particle's conditional spatial covariance is fixed; changing centers and temporal weights produce the moving body. You can therefore **hold the pose time and orbit the camera**, or hold the camera and play the motion. It represents the recorded motion interval; it is not a general character rig that accepts arbitrary new motions.

Long videos are processed in intervals supported by the model. The package records interval starts, frame ranges and playback transitions. Pose, appearance and color continuity need separate checks at interval boundaries.

### 5. How do short models become one full-motion timeline?

After completing the short result, `extend` fits later intervals with **new twelve-direction video priors generated from each interval’s own RGB and motion**. The seed uses six Base24 directions plus six Turbo4 offsets; later intervals use two six-direction Turbo4 passes. Equal view counts do not imply identical generation settings.

![Connect 121-frame training windows at a 120-frame stride, excluding overlap and final padding from the 957-frame playback](../../../assets/lessons/human-4d-gaussian/sequence.en.svg)

For example, 957 frames at 30Hz last 31.9 seconds. Each training window contains 121 frames and starts 120 frames after the previous one. Neighboring models share one training frame, but playback shows it once. The last 117 real frames receive four internal padding frames for the generator; those repeats do not extend playback.

All intervals retain **the same world origin, axes and units**. At global time 4.50 seconds, the second model is queried at local time 0.50 seconds. The camera stays in place as models change. The browser prepares only the current model and the next model.

Better source-view agreement does not validate hidden surfaces. Inspect each boundary for changing clothing colors or body thickness, and look for residual smearing around fast hands and hair.

**Comparison experiment:** `refine --trajectory-experiment` transfers the first model’s appearance to SOMA skin trajectories before fitting observed RGB. It avoids new multiview generation in later intervals, but produced more smearing there. The recommended full-motion exercise uses `extend` above.

### 6. Where do face/hand detail and geometry guidance enter?

Face/hand refinement crops **pixels at the original video resolution**. It does not enlarge an already reduced image. Cropping changes the image origin, so camera principal point `(cx, cy)` must move by the same offset. Training a crop without that adjustment mismatches image pixels and 3D rays.

MoGe-3 predicts **Z-depth `[H,W]`** and **normals `[H,W,3]`** from RGB. Z-depth measures along the camera's forward axis, rather than along an off-axis pixel ray. A normal is a unit vector describing surface orientation. Camera coordinates here are X right, Y down and Z forward.

```text
RGB → MoGe-3 → inferred depth + normals
                    ↓ scale/camera alignment; reject edges and contradictions
4D model → rendered depth + finite-difference normals → weak agreement loss
                    ↓
backpropagate with observed-RGB losses → update Gaussian parameters
```

Generated-camera constraints receive less weight than the observed RGB camera. Adding a prior does not turn the hidden back into an observation. Normals derived from rendered depth also differ from a smooth mesh's surface normals and can remain noisy.

## Run the lab

### 1. Start with observation and camera controls

Choose **Load the 3D example** above to fetch the reduced 4D Gaussian reconstruction learned from the dance video. The original remains in the official YouTube player on the left; orbit the 3D reconstruction on the right. Playback controls are independent. The 31.9s model has eight intervals; only the current and next interval are prepared in memory.

Pause3D and inspect the same pose from several directions. Open **Also explore the synthetic SOMA rig control** for the separate known-geometry example. Loading your own local RGB/model pair still provides a shared source/model timeline.

Use the 3D controls in this order:

1. Pause and choose a time.
2. Compare the front pose with the source. Where available, show source and 3D at equal size.
3. Hold time and drag to side/rear views. Those surfaces may be generated estimates.
4. Hold the camera and play. Look for sudden changes in hair, clothing and hands.
5. Inspect the beginning, middle, end and processing-interval boundaries.

**Open a local result folder** reads your package in this browser. It does not upload files to a server or run new GPU reconstruction. Select the top-level folder containing `manifest.json`. Include `source.mp4` in that package to compare the original.

```text
my-result/
  manifest.json
  source.mp4
  browser/
    s00/meta.json + Gaussian data
    s01/meta.json + Gaussian data
```

A path pointing outside the selected folder does not give the browser access to that video. Package source footage you can use inside the result folder.

The public control uses **18,056 vertex Gaussians**, **110 skinning bones** and up to **eight weights per particle**. SOMA deformation matrices computed with NVIDIA Warp move their centers. Its reference RGB is a fixed-camera triangle-mesh render of the same synthetic human.

The official SOMA motion contains 931 frames at 24Hz, giving about **38.79 seconds** of video. Horizontal root translation is removed for in-place playback; height and rotation are retained. Gaussian sizes remain isotropic and fixed, so this is not a complete representation of a deforming mesh surface. This control is not RGB-learned appearance or a model of the YouTube performer. [Control construction and sources](../../../labs/human-4d-gaussian/CONTROL-SOURCES.md).

### 2. Prepare one NVIDIA GPU machine

Training requires Linux x86_64, a compatible NVIDIA driver/CUDA toolchain, Git, Python and uv. The tested GPU is **one RTX 5090 32GB**. Follow [Linux GPU onboarding](../onboarding/nvidia-linux.md), then run these lines separately from the repository root.

```bash
nvidia-smi
export HUMAN_4D_ROOT="$HOME/physical-ai-labs/human-4d"
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" setup
```

`nvidia-smi` should report the GPU and driver. **The first `setup` writes a `runtime.json` template and exits with a prerequisite error asking for actual runtime configuration.** It does not mean dependencies have been installed.

Follow [runtime setup](../../../labs/human-4d-gaussian/README.md) and its official installation links to prepare separate Python environments, sources and weights, then enter their paths in `runtime.json`. Do not install into Isaac Sim's Python. Rerun the same `setup` command and pass its real module, pinned-source and asset-path checks before continuing. Initial model loading and CUDA compilation can still take additional time. Check source, weight and input-data terms in [SOURCES.md](../../../labs/human-4d-gaussian/SOURCES.md).

### 3. Prepare a local video you can use

The tested preset uses **static-camera 9:16 portrait video with even dimensions and at least 121 frames at 30Hz (about 4.03 seconds)**. Start with one person visible from head to feet, limited occlusion and few scene cuts. Replace the example with **your own file path**. The lab does not automatically download YouTube videos.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  prepare --video "$HOME/Videos/my-motion.mp4"
```

`prepare` reads resolution, frame count and timing, then prepares RGB for estimation. Check the beginning, middle and end of its input preview for a cropped-out person. The original file is retained separately. Motion, working RGB and ROIs share frame indices/times from the normalized 30Hz input; raw variable-FPS frame indices are not claimed to match one-to-one.

### 4. Estimate motion and inspect view conditions

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" rig
```

Set `RECON_PY` below to the `python.reconstruction` path in `runtime.json`. The inspection tools use NumPy, Pillow and OpenCV from that environment too.

First inspect the estimated GEM-X/SOMA joints overlaid on the original video. If wrists or ankles follow the wrong body part, check the input and estimate before continuing. Inspect foreground masks too. The following command measures mask coverage over the estimated head surface and creates RGB/mask contact sheets for frames needing review. It never edits the masks.

```bash
RECON_PY="$HUMAN_4D_ROOT/envs/reconstruction/bin/python"
"$RECON_PY" labs/human-4d-gaussian/inspect_masks.py --root "$HUMAN_4D_ROOT"
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" multiview
```

`multiview` projects reference-interval motion into virtual cameras and generates views. Full-video extension generates fresh views from each interval's own RGB and SOMA motion. Create the start/middle/end contact sheets below. Check **whether front, side and rear views actually face the intended directions**, and compare hand positions and clothing. The tool assembles images; it does not automatically classify front/back consistency.

```bash
"$RECON_PY" labs/human-4d-gaussian/inspect_teachers.py --root "$HUMAN_4D_ROOT" \
  --name pilot --out "$HUMAN_4D_ROOT/diagnostics/pilot-views.jpg"
"$RECON_PY" labs/human-4d-gaussian/inspect_teachers.py --root "$HUMAN_4D_ROOT" \
  --name offset --out "$HUMAN_4D_ROOT/diagnostics/offset-views.jpg"
```

If RGB contains a visible face but its mask is `0`, the training target asks the model to reproduce background there. If a generated image labeled `yaw=180°` shows a frontal face, its camera and image contradict each other. Fix these inputs before spending more optimization steps. See the [code README](../../../labs/human-4d-gaussian/README.md) for inspection and isolated experiments.

### 5. Train the model and refine original details

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" train
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" refine --seed-only
```

Start with **121 frames (about 4.03 seconds)**. `--seed-only` keeps the first exercise within that short interval so you can inspect it before trying the experimental full-motion extension. `train` fits observed RGB and generated views together. `refine` adds original face/hand pixels and MoGe-3 guidance, preserving previous checkpoints. A falling training loss alone does not establish more accurate novel views. Continue with the checks below.

### 6. Render, package and inspect

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" render
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" package
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" --deep check
```

`render` makes matched-time native and orbit recordings. `package` writes the browser model and playback metadata. After `check` validates arrays, files and time coverage, use **Open a local result folder** in [this page's viewer](#explore) and select `$HUMAN_4D_ROOT/package`. Playing an existing package does not require a CUDA GPU.

Optionally serve the package data locally with the command below. Its URL exposes data for inspection, not a replacement for the complete Pages 3D application.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" serve
```

Keep output folders outside tracked source. Publishing a model requires considering the source footage, people/capture material, model weights and included assets together. Linking to a source video and redistributing its footage or derived model are separate uses.

### 7. Advanced: extend the full motion with new views

After inspecting the short result, run this in the same output root. Every later interval performs generation and fitting, so a longer clip can take hours on one GPU. Completed stages are reused only after matching their input, recipe and output hashes. Rerun the same command after an interruption; use a new output root when changing an experiment’s conditions.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" extend
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" render
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  --package-dir "$HUMAN_4D_ROOT/package-full" package
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  --package-dir "$HUMAN_4D_ROOT/package-full" --deep check
```

The full timeline is written only after every interval passes its checks. Your short render and package remain intact; new renders use a separate folder identified by the selected model inventory. Open `package-full` in the viewer and inspect the beginning, middle, end and every interval boundary.

## Check the result

### Explore the published 3DGS and 4DGS results

| Result | Actual implementation | What to inspect |
| --- | --- | --- |
| Earlier rigged 3DGS | GEM-X/SOMA motion, one Gaussian appearance, Warp deformation and 3DGUT rendering | Front/left/back/right shown simultaneously. Hidden appearance uses body/symmetry priors. |
| Full-quality 4DGS video | Conditional 4D Gaussians fitted to generated multiview priors and original RGB · 957 frames | Native free-view render of the full selected models, not the reduced browser subset. |
| Browser 4DGS | At most 400000 retained Gaussians per interval across the same eight intervals | Selection preserves temporal/body-height coverage and retained parameters. It is not pixel-identical to the full model. |

[Full 31.9s native orbit video](../../../site/public/showcase/human-4d-dance/orbit.mp4) · [Earlier four-view 3DGS comparison](../../../site/public/showcase/human-4d-dance/rigged-3dgs.mp4)

Total browser-model transfer is about 382MiB, fetched in segments rather than all at page load. On mobile, watch the video first; use Wi-Fi to **Load the 3D example**. The next segment is prefetched; slower connections can pause at boundaries. 30Hz is the model time sampling rate, not guaranteed browser FPS.

Source: **지숭이_Jisoong — 체포하겠어🚨🚨**. Sides, back and occluded hands are inferred, not measured multiview ground truth. [Sources and usage scope](../../../labs/human-4d-gaussian/SOURCES.md) · [Published-package checker](../../../labs/human-4d-gaussian/check_published.py).



### 1. Inspect the complete interval

| Check | How to inspect | Completion criterion |
| --- | --- | --- |
| Time correspondence | Pause source and 3D at the same time | Beginning/middle/end poses correspond and coverage is recorded |
| Free viewpoint | Compare front, both sides and rear at fixed time | The same model renders from a real 3D camera; generated regions are labeled |
| Motion continuity | Play with a fixed camera | Interval transitions and fast-hand artifacts can be inspected |
| Valid data | Inspect checks and model arrays | No empty intervals, missing files, NaNs or infinities |
| Comparison recording | Show source and manipulation side by side | Both motions are readable without relying on a small inset |

Sharp source footage still does not reveal occluded hands, hair or the back of clothing. Plausible hidden appearance is different from verified hidden appearance. Moving Gaussians are not automatically a collision-ready human mesh or robot-control data.

### 2. What the short comparison established

These results concern a **4.03-second experimental interval**, not full-video performance. Conditions branch from the same initial model. No single metric establishes improved appearance from every direction.

| Comparison | Observed result | Interpretation |
| --- | --- | --- |
| Original face/hand refinement vs matched 3,000-step control | VGG19 appearance error fell 5.5%; mean central-ROI PSNR was 0.26dB lower | Appearance and pixel-reconstruction metrics changed differently |
| Joint 12-view generation | Generation and 3D fitting completed; some foot/side overlap remains | More directions did not establish an overall quality improvement |
| Finer face/hand particles | Face metrics became worse | Preserved as a separate experiment, not selected as default |
| MoGe-3 vs matched 1,500-step continuation | Error against inferred depth fell about 10.5%; RGB differences were small | Better prior agreement, not measured 3D accuracy |

Face/hand metrics average 25 times × three regions, or 75 ROIs. Some frames were excluded from direct high-resolution ROI optimization but remained in low-resolution conditioning/training. They are not independent unseen-view test data. The geometry comparison likewise measures agreement with the depth/normals used for guidance.

[Aggregate evaluation values](../../../labs/human-4d-gaussian/reconstruction-evaluation.json) retain the numerical comparisons without distributing source frames or the person model.

### 3. Official references and related labs

- [GEM-X](https://github.com/NVlabs/GEM-X): body/hand pose and temporal motion estimation.
- [SOMA-X](https://github.com/NVlabs/SOMA-X): human geometry and deformation representation.
- [4DAnyone](https://github.com/ant-research/4DAnyone): multiview video generation and 4DGS reconstruction.
- [MoGe-3](https://github.com/microsoft/MoGe): RGB-inferred depth and normals.
- [RGB scene reconstruction](rgb-reality-view.md): compare a moving person with scene reconstruction.
- [fVDB Reality Capture lab](spatial-reconstruction.md): separate training and evaluation cameras in a calibrated scene.

Reference footage: [지숭이_Jisoong channel](https://www.youtube.com/@%EC%A7%80%EC%88%AD%EC%9D%B4_Jisoo) · [original YouTube Shorts](https://www.youtube.com/shorts/rWS8uli1-m0). See [sources and licensing](../../../labs/human-4d-gaussian/SOURCES.md) for the separate usage scope of reference footage, models and public samples.
