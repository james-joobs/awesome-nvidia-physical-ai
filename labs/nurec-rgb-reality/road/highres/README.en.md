# Frankfurt from new viewpoints

[한국어](README.ko.md) · [PandaSet road reprojection](../README.md)

Choose a route from the [public Voxel51 sample of KITScenes Multimodal](https://huggingface.co/datasets/Voxel51/kitscenes-multimodal) and start the viewer. Play the Volvo chase view, then pause and select **3D cameras** or **Camera RGB**. All six camera buttons share the same timeline. Drag in **Free orbit** to inspect lane markings and nearby facades.

| Route | Time | What you can see |
| --- | ---: | --- |
| Tram and intersections | 19.5 s | Tram, cyclists, pedestrians and crossing traffic |
| Tree-lined avenue | 27.0 s | Oncoming and parked vehicles along a residential street |
| Downtown bridge | 7.2 s | The original scene with the added chase and surround views |

LoMa matches static RGB features. COLMAP bundle adjustment fits the six cameras. Mask2Former separates road, sky and traffic. The road uses RGB reprojected onto a ground surface, the sky uses a directional RGB texture, and gsplat reconstructs the remaining static scene. All 936 camera views registered across the three routes. Camera files in the source are 3504 × 2272. The browser serves smaller copies when you choose **Camera RGB**.

The Volvo is a reference model. Surrounding vehicles, bikes and people use simple 3D models whose estimated positions come from semantic masks and camera rays intersecting the ground. Toggle **Show traffic** to inspect the background, or use **Show recorded path** to trace the camera route. The camera RGB shows the observed appearance. Unseen areas and distant surfaces may remain soft in 3D.

Other useful sources are the [full KITScenes release](https://kitscenes.org/multimodal/), [Zenseact Open Dataset](https://zod.zenseact.com/) and [Argoverse 2 Sensor](https://www.argoverse.org/av2.html).

## Reproduce

The commands below recreate the bridge. For the longer routes, add the fetch options and use the training arguments in the table.

| Route | `--scene` | `--first` | `--last` | `--stride` | Training arguments |
| --- | --- | ---: | ---: | ---: | --- |
| Tram and intersections | `03ed2585-0729-92ad-98af-fdd9ac1c3a80` | 2 | 197 | 5 | `--steps 10500` |
| Tree-lined avenue | `04a39028-c434-6cff-b3f4-9f8dbb9aa078` | 2 | 272 | 3 | `--steps 16500 --max-width 1440 --grow-grad2d .00018` |

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
python "$HQ_CODE/surround.py" --input "$HQ_WORK/data" --sfm "$HQ_WORK/sfm" \
  --fit "$HQ_WORK/fit" --output "$HQ_WORK/browser/road"
python "$HQ_CODE/check.py"
```

For the avenue, clear floating Gaussians above the traced ego lane before exporting the final scene. The Gaussian fit's held-out metric is measured before this browser export step.

```bash
python "$HQ_CODE/clear_lane.py" --fit "$HQ_WORK/fit" --output "$HQ_WORK/lane"
npm exec --yes --package=@playcanvas/splat-transform@3.12.0 -- splat-transform \
  "$HQ_WORK/lane/scene.ply" "$HQ_WORK/lane/scene.spz" --spz-version 3
python "$HQ_CODE/package.py" --input "$HQ_WORK/data" --sfm "$HQ_WORK/sfm" \
  --fit "$HQ_WORK/fit" --cleaned-lane "$HQ_WORK/lane" --output "$HQ_WORK/browser/road"
```

[Source, license and changes](../../../../site/public/showcase/reality-kitscenes/ATTRIBUTION.txt) · [KITScenes paper](https://arxiv.org/abs/2606.02956).
