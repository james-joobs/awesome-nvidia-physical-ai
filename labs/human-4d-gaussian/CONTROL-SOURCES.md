# Public SOMA control sample: sources and scope

This public sample is a **synthetic control with known geometry and motion**. It is not a reconstruction learned from a monocular video, and it does not contain the referenced YouTube performer, frames, appearance, estimated motion, or audio.

## Inputs

| Component | Official source | Terms |
|---|---|---|
| Official example motion | [NVlabs/SOMA-X `assets/example_animation.usd`](https://github.com/NVlabs/SOMA-X/blob/01ab5b5c0876058bd27d34b1607d74b2e55e0cf4/assets/example_animation.usd) | [Apache-2.0](https://github.com/NVlabs/SOMA-X/blob/01ab5b5c0876058bd27d34b1607d74b2e55e0cf4/LICENSE) |
| Native neutral SOMA geometry and rig | [NVIDIA SOMA-X](https://huggingface.co/nvidia/SOMA-X) | Apache-2.0; use the native SOMA backend, not separately licensed SMPL/MHR assets |
| Data contract and playback rules | [Official data asset documentation](https://github.com/NVlabs/SOMA-X/blob/01ab5b5c0876058bd27d34b1607d74b2e55e0cf4/docs/data_assets.md#example_animationusd) | Apache-2.0 |
| Public build script | [`control_sample.py`](control_sample.py) | Repository MIT license |

Pinned SOMA code: `01ab5b5c0876058bd27d34b1607d74b2e55e0cf4`.

Official motion SHA-256: `c09372492aaacdca3ca7ec5d737263d8e6042b66fdd29318d91848427fa40695`. The control builder rejects a different motion file, helping prevent accidental publication of a private clip's extracted motion.

## What is generated

1. Read the official animation at every authored playback time: 931 frames at 24 Hz, time codes 0 through 930 inclusive.
2. Prepare the native neutral SOMA identity with all 128 shape coefficients set to zero; disable pose correctives.
3. Keep the official local rotations and vertical motion. Remove horizontal root translation for an in-place presentation, then shift the global floor to zero.
4. Run NVIDIA Warp skinning and capture the real deformation matrices, including inverse bind transforms.
5. Place one isotropic Gaussian at each of the 18,056 rest vertices. Reuse the native eight skinning weights per vertex and 110 expanded skinning bones.
6. Give the control a procedural matte palette with baked rest-space shading. No photographed skin, garment texture, or identifiable person's likeness is sampled.
7. Render a fixed camera's RGB from the posed triangle mesh with nvdiffrast. Separately render a 360-degree Gaussian camera orbit with gsplat.

The reference RGB and Gaussian views are produced from the same known control. They are different rendering representations, so their pixels need not be identical. The Gaussian centers follow native linear blend skinning; Gaussian sizes are held isotropic and fixed rather than treated as a physically accurate deformed surface covariance.

## Small browser format

`site/public/showcase/human-4d-control/manifest.json` selects one `data/` segment. The data includes:

| File | Array layout |
|---|---|
| `gaussians.f32.gz` | `N × 14`: rest xyz, isotropic std xyz, quaternion xyzw, opacity, RGB |
| `bone-indices.u16.gz` | `N × 8` |
| `bone-weights.f32.gz` | `N × 8`, rows sum to one |
| `bone-matrices.f32.gz` | `931 × 110 × 4 × 4`, row-major, meters, inverse bind already included |
| `meta.json` | Counts, time base, framing camera, source hash, array hashes, 40 native position parity samples |

The native skinning check compares the exported weighted matrices with actual SOMA posed vertices. The saved maximum difference is a numerical export check, not reconstruction accuracy or a measurement of a real person.

## Rebuild

Obtain the pinned SOMA source, its native assets, and the official example animation from the sources above. Git LFS must resolve the USD asset; an unresolved pointer is not a usable USD file.

```bash
python control_sample.py --stage export \
  --soma-source /path/to/SOMA-X \
  --assets-dir /path/to/native-soma-assets \
  --out /path/to/control-output

python control_sample.py --stage render \
  --out /path/to/control-output \
  --ffmpeg /path/to/ffmpeg
```

The export stage requires the pinned SOMA API, PyTorch, NVIDIA Warp and USD support. The render stage requires gsplat, nvdiffrast, Pillow and FFmpeg. These stages can use separate environments. `--nvdiffrast-dir` is optional when the renderer is already installed. The build output `control-reference.npz` is an intermediate mesh cache; it is not needed by the public browser and should not be copied into Pages.

Include `SOMA-LICENSE.txt` and `NOTICE.txt` alongside distributed SOMA-derived control data. The project's independent wrapper code remains MIT; third-party libraries retain their own licenses.

### Validated execution environments

- Export: Python 3.12.16, Torch 2.10.0+cu128, Warp 1.19.0, the pinned SOMA source overlay.
- Rendering: Python 3.11.18, Torch 2.8.0+cu128, gsplat 1.5.3, nvdiffrast, CUDA 12.9 compiler for SM 12.0.
- Hardware: one NVIDIA RTX 5090. These are recorded working versions, not a claim that every learner needs these exact versions.
