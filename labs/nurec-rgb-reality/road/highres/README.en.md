# Frankfurt from new viewpoints

[한국어](README.ko.md) · [PandaSet road reprojection](../README.md)

This reconstruction uses a 7.2-second KITScenes Multimodal clip from the [public Voxel51 release](https://huggingface.co/datasets/Voxel51/kitscenes-multimodal). Start 3D and change the recording position, lateral offset and height. These controls display novel views of a static reconstruction. People and moving vehicles are masked during fitting. Some distant buildings and occlusion edges are incomplete.

| Data candidate | Camera capture and access |
| --- | --- |
| [KITScenes Multimodal](https://www.kitscenes.com/multimodal/) | 3504 × 2272 on the six ring streams in the tested clip. All nine cameras contribute 72.5 MP per time in the full rig. The official download is gated. The Voxel51 release provides a public sample under CC BY-NC 4.0 and the KITScenes terms. |
| [Zenseact Open Dataset](https://zod.zenseact.com/) | 8 MP wide-angle front camera and a CC BY-SA 4.0 license. An access request is required for the sequence downloads. Useful for a future front-view comparison. |
| [Argoverse 2 Sensor](https://www.argoverse.org/av2.html) | Seven surround cameras and a front stereo pair. Camera images are 2048 × 1550 or portrait. Public access through the [AWS bucket](https://registry.opendata.aws/argoverse/), CC BY-NC-SA 4.0. |

The Frankfurt clip's native images are 3504 × 2272. The Gaussian fit uses images resized to at most 1152 px wide. The road texture samples the native RGB into a 1920 × 852 atlas. Distance-weighted blending and feathered semantic boundaries reduce visible seams between camera images. Input data consists of RGB and the released camera intrinsics. LoMa and COLMAP recover the poses and sparse 3D points. The reconstruction uses six cameras at 25 times, with all 150 images registered and an in-fit mean reprojection error of **1.00 px** at up to 1440 px wide.

On one RTX 5090, the selected fit trained **292,762 Gaussians** in **29.2 s** for 7,600 steps, excluding setup, camera recovery and texture baking. The renderer penalizes Gaussian opacity on confirmed sky pixels. The browser draws a separate RGB sky panorama and keeps the ground texture fixed. On eight photos withheld from the appearance fit and texture baking, the static-pixel PSNR averaged **24.49 dB**. The photos were available for camera recovery. An earlier 3,800-step fit scored 25.08 dB on those pixels. The selected fit has cleaner sky and facade detail in the filmed novel views. These measurements characterize one clip.

## Reproduce

Install the [LoMa and Mask2Former environment](../README.md#reproduce) with CUDA PyTorch and Python 3.12, then add the COLMAP and gsplat wheels. CUDA builds the gsplat extension on the first run. The verified setup used PyTorch 2.9.1, pycolmap 4.2.1 and gsplat 1.5.3.

```bash
python -m pip install pycolmap==4.2.1 gsplat==1.5.3 ninja
export HQ_CODE=labs/nurec-rgb-reality/road/highres
export HQ_WORK="$HOME/physical-ai-labs/kitscenes-frankfurt"
mkdir -p "$HQ_WORK"

python "$HQ_CODE/fetch_kit.py" --out "$HQ_WORK/data" \
  --revision e6cdac8eb56b2a8ee329cd31b16800cda53ef3e0
python "$HQ_CODE/reconstruct.py" --input "$HQ_WORK/data" --output "$HQ_WORK/sfm"
python "$HQ_CODE/train.py" --input "$HQ_WORK/data" --sfm "$HQ_WORK/sfm" --output "$HQ_WORK/fit"
npm exec --yes --package=@playcanvas/splat-transform@3.12.0 -- splat-transform \
  "$HQ_WORK/fit/scene.ply" "$HQ_WORK/fit/scene.spz" --spz-version 3
python "$HQ_CODE/package.py" --input "$HQ_WORK/data" --sfm "$HQ_WORK/sfm" \
  --fit "$HQ_WORK/fit" --output "$HQ_WORK/browser/road"
python "$HQ_CODE/check.py"
```

[Source, license and changes](../../../../site/public/showcase/reality-kitscenes/ATTRIBUTION.txt) · [KITScenes paper](https://arxiv.org/abs/2606.02956).
