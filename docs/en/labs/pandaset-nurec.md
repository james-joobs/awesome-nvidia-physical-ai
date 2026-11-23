# Reconstruct a real road and follow a Volvo in 3D

**RGB + LiDAR comparison.** For the RGB-only pipeline with estimated cameras and a mouse-controlled viewer, use [RGB-only road reconstruction](rgb-reality-view.md).

[All labs](../../../labs/README.md) · [한국어](../../ko/labs/pandaset-nurec.md)

Turn measured driving data into an ego-centered view. PandaSet supplies real camera images, LiDAR and camera poses. NuRec reconstructs the surroundings; an independently rendered **Volvo S90 Recharge** shows the ego position. Watch the saved example first, then reproduce the scene on a GPU.

## How it works

### 1. What enters the reconstruction?

```text
Six real cameras + intrinsics + timestamped poses
                   + measured LiDAR XYZ
                             ↓
                  NCore V4 + colored point seed
                             ↓ NuRec fitting
               3D Gaussian appearance / USDZ
                             ↓ chosen camera pose + K
                   New-view RGB image
                             ↓ optional Harmonizer
                 Enhanced RGB + Volvo overlay
```

An RGB frame is `uint8[576,1024,3]`: one red, green and blue value per pixel. The original 1920×1080 photographs are resized and their camera intrinsics scaled by the same factor. The front camera has approximately:

```text
K = [[1050.674,    0,     517.333],
     [   0,    1050.672,  257.759],
     [   0,       0,        1   ]]
```

`fx/fy` are focal lengths in pixels, not millimeters. `cx/cy` locate the optical center. A **4×4 camera-to-world matrix** and a timestamp place each image in the measured world. Camera coordinates are right/down/forward; the display rig uses forward/left/up, in meters.

A LiDAR frame is a pandas table with columns `x,y,z,i,t,d`: world-space position, intensity, measurement time and sensor identifier. For example, an actual frame-0 point is `[-58.4572,-61.2693,2.8810]` meters in the dataset world. These are **already world coordinates**; applying a second sensor-to-world transform would put them in the wrong place. The [official projection implementation](https://github.com/scaleapi/pandaset-devkit/blob/master/python/pandaset/geometry.py) projects world points through the inverse camera pose and `K`.

We retain frames 2–77 from all six cameras: **456 images**. Each eighth image is reserved by the NuRec validation split. Nineteen different LiDAR frames seed **320,000 colored Gaussians**; validation-frame scans are excluded. Sensor exposures are asynchronous, so the adapter interpolates ego poses before estimating rigid camera calibration. Measured maximum residuals are below 1.44 cm and 0.131°. This is an approximation, recorded per camera.

### 2. What is real, reconstructed or added?

The road, buildings and surrounding traffic come from PandaSet photographs and LiDAR. NuRec optimizes Gaussian appearance and geometry; the elevated and quarter views are newly rendered images, not ordinary video playback. The added cameras use `fx=fy=512`, giving a 90° horizontal pinhole view.

The white **Volvo S90 Recharge** is [lazercar’s detailed vehicle model](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9), not the original collection vehicle. Blender renders its body, glass, wheels and interior from the same display cameras. A measured local road-plane fit aligns its base; a shadow catcher adds contact shadows. The car layer is then alpha-composited **after** enhancement. It supplies no Volvo controller, tire dynamics or manufacturer validation. Vehicle layers were rendered on macOS with Blender 4.5.1 / Cycles CPU, while NuRec and Harmonizer ran on the Linux GPU machine.

### 3. Why can another viewpoint look imperfect?

This preset is a **static-scene baseline**. Moving road users are not separated into tracked dynamic layers, so they can smear or appear more than once. Newly exposed surfaces can be incomplete. The per-frame non-temporal Harmonizer can alter pixels or flicker; it does not establish ground-truth geometry. **Built on NVIDIA Cosmos.**

A stationary display mesh follows the recorded ego poses. Wheel rotation, dynamic lighting and depth-based occlusion against other vehicles are not implemented. No Alpamayo inference or closed-loop driving on this real scene is claimed. The [separate synthetic-road lab](reality-view.md) shows the actual Alpamayo input/output experiment.

## Run the lab

### 1. Inspect the saved result on any computer

Open the [comparison video](../../../labs/pandaset-nurec/evidence/pandaset-nurec.en.mp4), [Volvo quarter view](../../../labs/pandaset-nurec/evidence/volvo-quarter.mp4), or [NuRec without the car layer](../../../labs/pandaset-nurec/evidence/nurec-quarter.mp4). The [evidence folder](../../../labs/pandaset-nurec/evidence) includes matched frames and the measurement receipt.

From a terminal opened in this repository:

```bash
python3 labs/pandaset-nurec/check.py
```

This reads files only; it does not launch a GPU job. With FFmpeg installed, add `--decode-video` to decode every saved MP4.

### 2. Download one permitted scene

Read the [data/asset rights and attribution](../../../labs/pandaset-nurec/SOURCES.md) first. The original payload says **CC BY 4.0 plus PandaSet Dataset Terms**; Scale’s Nucleus notice instead says CC BY-SA 4.0. We preserve both notices and apply CC BY-SA 4.0 to our new demo media, alongside the original terms. The data is transported by a **pinned unofficial community mirror** because original hosting was unavailable. This is not an official NVIDIA dataset or an official mirror.

Use an NVIDIA Linux machine with Docker GPU access. The tested machine has RTX 5090 32 GB and about 32 GB host RAM. Allow at least 15 GB free space; the optional car source adds roughly 3 GB unpacked. Review [GPU onboarding](../onboarding/nvidia-linux.md) if `nvidia-smi` or Docker cannot see your GPU.

```bash
export PANDASET_ROOT="$HOME/physical-ai-labs/pandaset-road"
mkdir -p "$PANDASET_ROOT"
nvidia-smi
docker pull nvcr.io/nvidia/nre/nre-ga:26.04
bash labs/pandaset-nurec/run.sh download
```

The script reads the ZIP directory, then downloads scene 001’s roughly 416 MiB region, not the whole 44.5 GB archive. It checks each file’s ZIP CRC/size and records SHA-256 hashes. The full archive SHA-256 is **not** verified by this range download. Keep `data/001/LICENSE.txt`.

### 3. Fit the real scene and render three views

Run each line after the previous one finishes:

```bash
bash labs/pandaset-nurec/run.sh prepare
bash labs/pandaset-nurec/run.sh train
bash labs/pandaset-nurec/run.sh render
```

`prepare` writes calibrated NCore data, a measured-LiDAR seed and `ground-plane.json`. Pickle reading uses a strict constructor allowlist inside the network-disabled runtime, with only this lab’s output mounted. `train` runs 6,000 optimization steps. `render` produces **76 PNGs each** under `renders/front`, `renders/ego-elevated` and `renders/ego-quarter`. The pinned 26.04 container selects `gsplat` explicitly.

For optional enhancement, download the [official non-temporal checkpoint](https://huggingface.co/nvidia/Harmonizer) at revision `20ca33d4612b1e98e0526b3a7ee604af5b289f58`, after reviewing its NVIDIA Open Model License. Point to its containing folder:

```bash
export HARMONIZER_WEIGHTS="/absolute/path/to/Harmonizer"
bash labs/pandaset-nurec/run.sh enhance
```

### 4. Render the actual car model

Download the Blender archive from **the author-provided Google Drive link in the [original model page](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9)**, then extract it. Source size, SHA-256 and attribution are in [ego-car.json](../../../labs/reality-view/ego-car.json). Do not put the 1.2 GB archive in Git.

With Blender 4.5 installed, replace these two paths with your extracted files:

```bash
export VOLVO_BLEND="/absolute/path/to/Volvo S90.blend"
export VOLVO_TEXTURES="/absolute/path/to/textures"
blender --background --disable-autoexec "$VOLVO_BLEND" \
  --python labs/reality-view/render_ego_car.py -- \
  --textures "$VOLVO_TEXTURES" --views "$PANDASET_ROOT/ego-views.json" \
  --ground-plane "$PANDASET_ROOT/ground-plane.json" \
  --output "$PANDASET_ROOT/vehicle-layers"
```

`--disable-autoexec` prevents scripts embedded in the downloaded `.blend` from running. The output contains separate car-only and shadow-catcher PNGs for each display camera. The packager reduces the shadow layer to 22% strength for a readable overlay; lighting is not calibrated to the photographs. The [packaging script](../../../labs/pandaset-nurec/package.py) composites these layers onto matching NuRec frames and writes compact videos with source credits.

To export your completed run, install Pillow and FFmpeg, then run the packager with a Korean-capable font:

```bash
python3 labs/pandaset-nurec/package.py --input "$PANDASET_ROOT" \
  --output "$PANDASET_ROOT/published" \
  --font "/absolute/path/to/NotoSansKR.ttf"
```


## Check the result

The saved run used **6,000 NuRec steps, 456 calibrated images and a 320,000-Gaussian LiDAR seed**. NuRec reported **100.80 seconds for training**, excluding downloads, conversion and rendering. The USDZ is **110,694,637 bytes**. This small baseline is not a quality or runtime benchmark against another reconstruction method.

Check frame counts, calibrated transforms, hashes, video decoding and the recorded scope:

```bash
python3 labs/pandaset-nurec/check.py --decode-video
```

Compare the original camera photograph with the corresponding front render, then compare the two new views **before** and **after** enhancement. A visually cleaner lane marking is not necessarily a more faithful one. No ground-truth photograph exists for the elevated camera, so no novel-view accuracy score is invented.

Keep the [PandaSet terms and credits](../../../labs/pandaset-nurec/SOURCES.md) with exported results. The Volvo is an added visual reference; this experiment reconstructs measured surroundings and does not validate autonomous vehicle control.
