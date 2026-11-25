# Reproject camera RGB onto a fixed road surface

[한국어](README.ko.md) · [Reality View lab](../README.md)

Use **Reprojected RGB road + 3D scene** to orbit a road textured with observed RGB. Switch to **3DGS background + time-local vehicles** at the same time and viewpoint to compare, or select **Reprojected RGB road only** to inspect coverage.

| Stage | Input and output |
| --- | --- |
| Separate the scene | Mask2Former Cityscapes maps each RGB image to road, sky and other labels. |
| Refine cameras | LoMa-B matches stable pixels. Bundle adjustment refines six shared focal scales, the rig pose at each time, and 3D landmarks. |
| Fit the road | DA3 depth and video Depth Pro 2-B depth agree on plausible road points. LoMa road tracks add triangulated anchors. Fit one gently curved surface in the existing scene coordinates. |
| Bake the texture | For each road texel, project its 3D position into the calibrated cameras. Use the best-resolved road observation when at least two views support the texel. Mask edges and reject large depth discrepancies. |
| Composite | Draw the road texture on the fitted surface, attenuate nearby splats over covered road, and retain the surrounding Gaussian scene and time-local vehicle meshes. Filter high splats that repeatedly project into sky. |

Principal points and relative positions inside the camera rig stay fixed in this short clip. Bundle adjustment runs offline on 17 sampled times. Depth Pro 2 uses overlapping eight-frame windows. Its output is rescaled per camera to the existing reconstruction's relative units before blending with DA3. Vehicle meshes use the earlier DA3 layer so the road experiment can be compared at the same viewpoint.

## Results on the same PandaSet RGB clip

- The 5090 executed Mask2Former, LoMa and Depth Pro 2 on the same 102 images. LoMa tested 441 image pairs and returned 221,588 geometrically filtered links. Bundle adjustment retained 3,200 training tracks and 500 separate validation tracks.
- For each validation track, triangulate from two observations and project into the other views. On 1,887 such projections, p90 moved from 6.72 to 6.39 px at 756 × 420. The median was approximately 1.73 px in both cases.
- Five front images withheld from texture baking provided 32,783 mutually visible detail pixels. The mean local luminance detail error fell from 6.71 to 6.63 on an 8-bit scale when both calibration and depth refinement were added. These images were available during calibration and surface fitting.
- The texture is 1600 × 723. In the first pass, sky filtering removed 76,712 Gaussians from the existing 1,173,892-splat background. The viewer fills uncovered areas with the original surrounding representation or the clear color. Surface distances and camera heights are relative. Texture seams and residual artifacts can appear at extreme views and distant boundaries.

## Refine the skyline and walls

The default browser view uses three observed RGB layers. The road remains a fixed textured surface. Building and wall features matched by LoMa anchor near-vertical planes, which are textured only where building labels and depth agree in at least three views. The sky is a direction-only background textured with eroded Mask2Former sky pixels. About 13% of the upper hemisphere had sufficient observations, so the remaining directions fade to an estimated background color. The filtered Gaussian scene supplies surrounding detail between those surfaces.

A second offline BA allows small shared relative pose corrections for the five cameras around the front reference and regularizes changes between adjacent rig frames. Both solves use the same original LoMa matches and the same 1,887 validation projections.

| Calibration | Overall median | Overall p90 | Facade p90 |
| --- | ---: | ---: | ---: |
| RGB-derived initial cameras | 1.73 px | 6.72 px | 6.25 px |
| First LoMa + fixed rig BA | 1.73 px | 6.39 px | 5.52 px |
| LoMa + shared rig correction BA | 1.61 px | 5.97 px | 5.94 px |

The second solve reached its 220-evaluation limit. Its sky projection and sky filtering use the updated poses. Facade texture projection uses the first BA camera parameters, whose facade p90 was lower. Road texture detail also favored the first bake on 36,355 common pixels from five views withheld from texture baking, with mean detail errors of 6.70 and 6.79. Both the original road surface and texture remain the default. Minor facade seams, missing sky directions and surrounding reconstruction artifacts are still visible.

## Reproduce

Finish the [DA3 RGB-only preparation](../unified/README.md) and [persistent background export](../dense/README.md) first. Keep the generated input files in a separate working folder. On Linux with CUDA, initialize a Python 3.12 environment with a PyTorch build supported by your GPU. The measured run used PyTorch 2.9.1 CUDA 12.8, torchvision 0.24.1 and Transformers 5.24.1.

```bash
python -m pip install 'transformers==5.24.1' scipy \
  'git+https://github.com/davnords/LoMa@ecc947d44ddc9d50387e887bbedc743d65ffac00' \
  'git+https://github.com/apple-aiml-research/ml-depth-pro-2@aa389cbb0b74341664ed663a0966c859905cd6c0'
export ROAD_CODE=labs/nurec-rgb-reality/road
export ROAD_SITE=site/public/showcase/reality-joint-geometry
export ROAD_WORK="$HOME/physical-ai-labs/road-reprojection"
export ROAD_GEOMETRY=/path/to/da3-surround-priors/geometry.npz
export ROAD_BACKGROUND=/path/to/static-background.ply

for stage in mask match; do
  python "$ROAD_CODE/infer.py" "$stage" --geometry "$ROAD_GEOMETRY" --output "$ROAD_WORK/inference"
done
python "$ROAD_CODE/calibrate.py" --scene "$ROAD_SITE/scene.json" --inference "$ROAD_WORK/inference" --fixed-rig --output "$ROAD_WORK/refined"
python "$ROAD_CODE/infer.py" depth --geometry "$ROAD_GEOMETRY" --output "$ROAD_WORK/inference" \
  --calibration "$ROAD_WORK/refined/calibration.npz"
python "$ROAD_CODE/bake.py" --geometry "$ROAD_GEOMETRY" --scene "$ROAD_SITE/scene.json" \
  --inference "$ROAD_WORK/inference" --calibration "$ROAD_WORK/refined" --output "$ROAD_WORK/baked" --evaluate
python "$ROAD_CODE/calibrate.py" --scene "$ROAD_SITE/scene.json" --inference "$ROAD_WORK/inference" \
  --reference "$ROAD_WORK/refined/calibration.npz" --output "$ROAD_WORK/refined-v2"
python "$ROAD_CODE/bake.py" --geometry "$ROAD_GEOMETRY" --scene "$ROAD_SITE/scene.json" \
  --inference "$ROAD_WORK/inference" --calibration "$ROAD_WORK/refined-v2" --output "$ROAD_WORK/baked-v2" --evaluate
python "$ROAD_CODE/compare_ground.py" --geometry "$ROAD_GEOMETRY" --inference "$ROAD_WORK/inference" \
  --previous "$ROAD_WORK/refined" "$ROAD_WORK/baked" \
  --candidate "$ROAD_WORK/refined-v2" "$ROAD_WORK/baked-v2" --output "$ROAD_WORK/road-quality.json"
python "$ROAD_CODE/bake_surroundings.py" --geometry "$ROAD_GEOMETRY" --inference "$ROAD_WORK/inference" \
  --calibration "$ROAD_WORK/refined-v2/calibration.npz" --facade-calibration "$ROAD_WORK/refined/calibration.npz" \
  --output "$ROAD_WORK/surroundings"
python "$ROAD_CODE/filter_sky.py" --ply "$ROAD_BACKGROUND" --geometry "$ROAD_GEOMETRY" \
  --inference "$ROAD_WORK/inference" --calibration "$ROAD_WORK/refined-v2" \
  --surroundings "$ROAD_WORK/surroundings" --output "$ROAD_WORK/baked-v2"
npm exec --yes --package=@playcanvas/splat-transform@3.12.0 -- splat-transform \
  "$ROAD_WORK/baked-v2/sky-filtered.ply" --filter-harmonics 1 "$ROAD_WORK/baked-v2/sky-filtered.spz" --spz-version 3
python "$ROAD_CODE/package.py" --baked "$ROAD_WORK/baked-v2" --ground "$ROAD_WORK/baked" \
  --inference "$ROAD_WORK/inference" --surroundings "$ROAD_WORK/surroundings" \
  --ground-comparison "$ROAD_WORK/road-quality.json" --output "$ROAD_SITE/road"
python "$ROAD_CODE/check.py"
```

[LoMa source](https://github.com/davnords/LoMa) · [Mask2Former checkpoint and terms](https://huggingface.co/facebook/mask2former-swin-tiny-cityscapes-semantic) · [Depth Pro 2 code and terms](https://github.com/apple-aiml-research/ml-depth-pro-2) · [NuRec and PandaSet sources](../SOURCES.md).
