# RGB-only NuRec, Harmonizer and Alpamayo

[All labs](../../../labs/README.md) · [한국어](../../ko/labs/nurec-rgb-reality.md)

Reconstruct a real road in **NuRec**, compare **Harmonizer** on the same new camera views, and inspect **Alpamayo 2 Edge** predictions together with actual camera detections. The reconstruction uses RGB pixels only. Start with the saved viewer and videos, then reproduce the stages on one RTX 5090.

## How it works

![RGB camera geometry enters NuRec; native renders enter Harmonizer; original RGB and estimated history enter Alpamayo; detections and predictions join the viewer](../../../assets/lessons/nurec-rgb-reality/pipeline.en.svg)

### 1. Which tools actually ran?

| Stage | Actual input → output | Its role |
| --- | --- | --- |
| COLMAP | 162 RGB images → camera intrinsics, poses and sparse XYZ/RGB | Recover geometry from image matches, with no supplied calibration or pose labels. |
| Rig bundle adjustment | Free-camera estimates → one six-camera rig over 27 nominal times | Fit the fixed camera layout required by this NuRec input profile. |
| NCore | Estimated cameras, RGB and SfM points → NuRec sequence + Gaussian seed | Package data; NCore is a format and API, not a model. |
| NuRec 26.04 | NCore + RGB-derived seed → trained artifact, native new-view RGB and exported Gaussians | Run the actual NuRec runtime using its 3DGUT COLMAP preset. |
| Harmonizer | Native NuRec RGB → enhanced RGB at the same camera poses | Released **non-temporal** image enhancement; it does not change the 3D model. |
| Alpamayo 2 Edge | Original RGB views + estimated past motion + navigation → 64 future poses per keyframe | Run the actual VLA checkpoint; display its prediction without applying controls. |
| Mask R-CNN | Original RGB → classes, scores, boxes and instance masks | Recognize road users independently of Alpamayo and enhancement. |

The [standalone 3DGUT lab](rgb-reality-view.md) is a comparison implementation. NuRec itself also uses a 3DGUT preset here, but this lab calls **NuRec's data, training, native rendering and export entry points**, rather than substituting the standalone trainer.

### 2. What does RGB-only mean here?

The pinned public example fetches only camera JPEGs and the original data terms. COLMAP estimates `K[3,3]`, camera-to-world matrices `[4,4]` and sparse points `XYZ[N,3]` from overlapping images. No LiDAR, supplied depth, GPS, IMU, sensor poses, intrinsics, sensor timestamps or object annotations enter reconstruction.

Six folders and matching frame numbers define a **nominal** camera grouping. Rig bundle adjustment jointly refines camera extrinsics, rig poses and points while keeping the estimated undistorted intrinsics fixed. The free-camera fit had 0.875 px mean reprojection error; the fixed-rig fit has about 1.150 px. The stronger physical layout constraint does not make the image residual smaller, and nominal grouping does not establish precise sensor synchronization.

NuRec receives 162 RGB observations and about 28,600 triangulated points. The point cloud is **derived from RGB**, not measured by a range sensor. NCore stores a dynamic rig trajectory, static camera-to-rig transforms, intrinsics and RGB frames. The dataset contains no LiDAR component or ground-truth object tracks.

Global scale remains ambiguous. The estimated camera-to-road height is normalized to one display unit. The road plane is fitted from RGB feature tracks. This is a relative coordinate system, not a surveyed road map. All images inform SfM, so the saved run is not an independent novel-view benchmark.

### 3. What changes in NuRec and Harmonizer?

NuRec optimizes Gaussian positions, orientation, size, opacity and view-dependent appearance. Its native renderer evaluates those Gaussians from a new camera. The saved run trains 16,000 steps; exact timing, artifact identity and Gaussian count are in [recorded.json](../../../labs/nurec-rgb-reality/recorded.json).

Harmonizer receives an actual native NuRec frame as `float[1,3,1,576,1024]` in `[-1,1]` and returns enhanced RGB. The side-by-side recording pairs the **same camera pose and frame index**. Its released non-temporal checkpoint treats frames independently, so details may change or flicker. Filling a road-shaped gap is an appearance prediction, not evidence that the hidden surface was observed. **Built on NVIDIA Cosmos.**

The browser viewer uses the official NuRec `export-gaussian-plys` result, converted to a compressed SPZ. It retains the Gaussians with degree-1 view-dependent color, then renders them with Spark/Three.js. This is a **NuRec-trained browser preview**; rasterization and compression can differ from native NuRec output. Harmonizer is shown in the companion native-render comparison, not claimed to run on every mouse movement.

### 4. Where does Alpamayo's route come from?

Alpamayo uses original camera pixels, not Harmonizer-generated details. Four physical RGB streams supply six virtual model slots: left, front and right views, two rotated rear subviews from the back camera, and a telephoto crop from the front. Crop rays stay inside the recorded images. This is an explicit **camera-layout adaptation**, with narrower fields of view than the model's native profile; it is not native NVIDIA AV calibration.

```text
22 selected RGB views:     uint8[22,1,3,576,1024]
Camera IDs / nominal times: int64[22]
Past positions:            float[1,20,3], -1.9 s through 0 s
Past orientations:         float[1,20,3,3]
Navigation:                “Continue straight on the road and yield to pedestrians.”
Output positions:          float[1,1,1,64,3]
Output rotations:          float[1,1,1,64,3,3]
```

Twenty past poses come from RGB-estimated, ground-projected motion: planar yaw orientation, position smoothing and interpolation to 10 Hz. Image selection uses the latest available frame **at or before** each requested time. There are no future trajectory labels. Camera poses are reconstructed offline from the whole image set, so this is not a strictly causal online perception or driving system.

The model expects meter-based history. The example explicitly assumes a **1.8 m camera height** to convert relative SfM units. That scale is not measured from RGB. Changing it can change the prediction. The CLI exposes `--assumed-camera-height-m` so this prior is visible and replaceable.

Four actual inferences are anchored at 2.1, 3.9, 5.7 and 7.8 seconds. A dashed green line displays the latest available prediction, with its input time and scale assumption. Before 2.1 seconds, no future keyframe is shown. The line receives a small display-height offset; raw coordinates remain in the saved model output. Generated explanations may be wrong and are preserved as model output, not treated as verified scene facts. This is **open-loop inference**, not a closed-loop drive or driving-quality test.

### 5. How are cars and people shown?

Mask R-CNN predicts classes, boxes and binary instance masks on the original RGB. A score threshold of 0.8 keeps six road-user classes. Cyan marks vehicles, amber marks people and purple marks cycles. The camera panel shows the actual photos with their predictions; recognition can be switched off for comparison.

A mask-bottom pixel, estimated camera geometry and the RGB-derived road plane produce an approximate 3D contact marker. Edge-truncated, horizon and far intersections remain 2D-only. Markers are not measured 3D boxes or occlusion-correct physical actors. Temporary associations can change IDs; detection observations across frames are not unique-person or unique-car counts. [Detailed mask and coordinate explanation](rgb-reality-view.md).

The credited Volvo S90 is an added 3D foreground reference, not the original collection vehicle or a dynamics model. Native reconstruction, appearance enhancement, object perception and behavior prediction remain separately inspectable.

## Run the lab

### 1. Explore without a CUDA GPU

Use the viewer on this page and the native NuRec/Harmonizer comparison. The source-RGB recognition panel, camera selector, predicted path and mouse controls are interactive. Browser playback reuses saved inference outputs.

```bash
python3 labs/nurec-rgb-reality/check.py
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092
```

Open **http://127.0.0.1:8092/**. An internet connection supplies pinned viewer JavaScript modules. Video and evidence checks also work without an NVIDIA GPU.

### 2. Prepare one GPU machine

The tested host uses Linux x86_64, one RTX 5090 32 GB and about 32 GB system RAM. Install a compatible NVIDIA driver, Docker with NVIDIA Container Toolkit, Python, Git, uv and Node.js/npm. Check [NVIDIA Linux onboarding](../onboarding/nvidia-linux.md).

```bash
nvidia-smi
export NUREC_RGB_ROOT="$HOME/physical-ai-labs/nurec-rgb-road"
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" setup
```

Read [SOURCES.md](../../../labs/nurec-rgb-reality/SOURCES.md) first: the NuRec runtime, model weights, dataset and vehicle have separate terms. Setup pulls the pinned runtime, installs isolated environments and downloads public model checkpoints plus the NuRec metric dependency. These downloads and initial compilation take longer than the warmed-up sample run. Model weights, raw logs and input caches stay outside Git.

### 3. Follow each stage

Run from the repository folder. Each command must finish successfully before the next:

```bash
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" rgb
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" rig
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" prepare
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" train
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" render
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" enhance
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" --assumed-camera-height-m 1.8 policy
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" perceive
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" export
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" serve
```

`rgb` recovers cameras; `rig` enforces the fixed layout; `prepare` writes NCore; `train` runs NuRec and exports its Gaussians. `render` produces native front, quarter and orbit views; `enhance` processes the orbit frames with Harmonizer. `policy` and `perceive` run their own models on source RGB, and `export` packages the viewer.

For a fresh output folder, `pipeline.py --root "$NUREC_RGB_ROOT" all` runs the full sequence. GPU stages use the same lock and one visible device. The demo preset expects six camera folders with the documented PandaSet-style names; a single forward camera cannot observe the rear context needed by this example. Custom camera layouts need an explicit adapter, not relabeling unseen views.

## Check the result

```bash
python3 labs/nurec-rgb-reality/check.py --decode-video
python3 -m unittest discover -s labs/rgb-reality-view -p 'test_*.py'
```

The checker validates data provenance, camera/rig geometry, actual NuRec completion, native/Harmonizer frame pairing, policy tensor shapes and finite rotations, source-RGB detection outputs, compressed model count, artifact hashes and recorded controls. Full-video decoding needs FFmpeg. It verifies implementation and integrity, **not driving safety, detector accuracy or hidden-surface truth**.

Compare this run with [standalone 3DGUT](rgb-reality-view.md), [the earlier RGB + LiDAR NuRec baseline](pandaset-nurec.md), and [the self-authored synthetic-road interface test](reality-view.md). Their data assumptions and execution paths are labeled separately. The interactive view is ego-centered, but no Tesla proprietary model or live Reality View system is being reproduced.
