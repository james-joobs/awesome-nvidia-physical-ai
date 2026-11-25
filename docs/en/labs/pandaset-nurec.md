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

The example uses **456 images from six cameras** and a **320,000-point LiDAR seed**. The adapter synchronizes camera poses and reserves every eighth image for validation.

### 2. What is real, reconstructed or added?

The road, buildings and surrounding traffic come from PandaSet photographs and LiDAR. NuRec optimizes Gaussian appearance and geometry; the elevated and quarter views are newly rendered images, not ordinary video playback. The added cameras use `fx=fy=512`, giving a 90° horizontal pinhole view.

The **Volvo S90 Recharge**, by [lazercar](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9), is an added ego-position reference. Blender renders it from the same camera, aligns it to the road plane and composites it after enhancement.

### 3. Why can another viewpoint look imperfect?

This is a **static reconstruction**: moving traffic can leave ghosts, and unseen surfaces can have gaps. Harmonizer, **built on NVIDIA Cosmos**, adjusts each frame’s appearance. Continue to the [Alpamayo lab](reality-view.md) to explore predicted driving paths.

## Run the lab

### 1. Inspect the saved result on any computer

Open the [comparison video](../../../labs/pandaset-nurec/evidence/pandaset-nurec.en.mp4), [Volvo quarter view](../../../labs/pandaset-nurec/evidence/volvo-quarter.mp4), or [NuRec without the car layer](../../../labs/pandaset-nurec/evidence/nurec-quarter.mp4). The [evidence folder](../../../labs/pandaset-nurec/evidence) includes matched frames and the measurement receipt.

From a terminal opened in this repository:

```bash
python3 labs/pandaset-nurec/check.py
```

This reads files only; it does not launch a GPU job. With FFmpeg installed, add `--decode-video` to decode every saved MP4.

### 2. Download one permitted scene

Review the [PandaSet and vehicle terms](../../../labs/pandaset-nurec/SOURCES.md). The download script selects one scene from a pinned community mirror and retains its source notices.

Use an NVIDIA Linux machine with Docker GPU access. The tested machine has RTX 5090 32 GB and about 32 GB host RAM. Allow at least 15 GB free space; the optional car source adds roughly 3 GB unpacked. Review [GPU onboarding](../onboarding/nvidia-linux.md) if `nvidia-smi` or Docker cannot see your GPU.

```bash
export PANDASET_ROOT="$HOME/physical-ai-labs/pandaset-road"
mkdir -p "$PANDASET_ROOT"
nvidia-smi
docker pull nvcr.io/nvidia/nre/nre-ga:26.04
bash labs/pandaset-nurec/run.sh download
```

The script downloads about **416 MiB for scene 001** and keeps `data/001/LICENSE.txt` with the data.

### 3. Fit the real scene and render three views

Run each line after the previous one finishes:

```bash
bash labs/pandaset-nurec/run.sh prepare
bash labs/pandaset-nurec/run.sh train
bash labs/pandaset-nurec/run.sh render
```

`prepare` writes NCore data, the LiDAR seed and `ground-plane.json`. `train` fits the scene for 6,000 steps. `render` saves **76 PNGs per view** in `renders/front`, `renders/ego-elevated` and `renders/ego-quarter`.

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

`--disable-autoexec` prevents embedded Blender scripts from running. The output contains car and shadow PNGs; the [packager](../../../labs/pandaset-nurec/package.py) combines them with the matching NuRec views.

To export your completed run, install Pillow and FFmpeg, then run the packager with a Korean-capable font:

```bash
python3 labs/pandaset-nurec/package.py --input "$PANDASET_ROOT" \
  --output "$PANDASET_ROOT/published" \
  --font "/absolute/path/to/NotoSansKR.ttf"
```


## Check the result

Compare the original front-camera image, the reconstructed view and Harmonizer’s output. Look at lane edges, building outlines and moving traffic.

```bash
python3 labs/pandaset-nurec/check.py --decode-video
```

The checker validates the saved cameras, files and videos. [Run details](../../../labs/pandaset-nurec/recorded.json) · [Data and vehicle credits](../../../labs/pandaset-nurec/SOURCES.md) · [RGB-only reconstruction](rgb-reality-view.md)
