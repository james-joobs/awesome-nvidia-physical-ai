# fVDB Reality Capture

[← Catalog](../../README.md) · [한국어](../ko/fvdb-reality-capture.md)

Reconstruct a 3D Gaussian scene from photos and camera poses, render a new viewpoint, and choose an export for the next step.

## How do captured photos produce a new viewpoint?

### From the capture to Gaussians

The official `safety_park` example uses a COLMAP capture. Each image has camera intrinsics and a pose, and the capture includes sparse 3D points found by matching features across images. fVDB Reality Capture loads the capture into an `SfmScene`. It initializes Gaussians at the sparse points and repeatedly adjusts their position, size, rotation, opacity, and appearance to make the rendered images at known poses match the source photos.

### Read the input and output in the official run

| Stage | Recorded `safety_park` values | What they mean |
|---|---|---|
| Load COLMAP output | 124 images and 199,702 sparse points | The points are matched 3D locations across views. |
| Clean and resize | 124 images and 168,661 points | The log shows `000079.jpg` going from 3,840 × 2,160 to 960 × 540. The pipeline also filters points. |
| Initialize → optimize | 168,661 initial Gaussians → 1,552,032 on the final progress line | The optimizer can add or remove Gaussians. Their count describes the radiance field. |

![Sparse points projected into camera images in the official safety_park tutorial](https://raw.githubusercontent.com/openvdb/fvdb-reality-capture/7b3264827e782959f55a6536acb2db1d5e8b2ce1/docs/tutorials/radiance_field_and_mesh_reconstruction_files/radiance_field_and_mesh_reconstruction_6_1.png)

The official run demonstrates loading and reconstruction. To measure novel-view quality, hold out camera views during fitting and compare renders against those photos. [Official tutorial, source data, and run log](https://github.com/openvdb/fvdb-reality-capture/blob/7b3264827e782959f55a6536acb2db1d5e8b2ce1/docs/tutorials/radiance_field_and_mesh_reconstruction.md)

## Choose an export for the next step

| File | Content | Use |
|---|---|---|
| `reconstructed_model.ply` or Gaussian USD | Splat positions, scales, orientations, and appearance | Render a novel view or preview the scene. |
| `reconstructed_mesh.ply` | Vertices and faces describing a triangle surface | Inspect or edit surfaces, and use the geometry as a starting point for a collider. |

The two PLY exports store different attributes. For simulated contact, check the mesh scale and surface before authoring a collision shape. [OpenUSD](openusd.md) · [SimReady](simready.md) · [NuRec for driving sensor reconstruction](nurec.md)

## Official sources and license

[fVDB Reality Capture repository](https://github.com/openvdb/fvdb-reality-capture) · [Apache-2.0 code license](https://github.com/openvdb/fvdb-reality-capture/blob/7b3264827e782959f55a6536acb2db1d5e8b2ce1/LICENSE). Check the terms of the sample data and dependencies separately.
