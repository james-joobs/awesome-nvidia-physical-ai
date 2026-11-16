"""Lift Isaac Sim camera depth into world coordinates and test relative displacement."""

import argparse
import json
from pathlib import Path

import numpy as np
from pxr import Usd, UsdGeom

TRUE_CUBE_X = [.125, -.18, .23, .03]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.Open(str(args.capture / "workbench_scene.usda"))
    camera = UsdGeom.Camera.Get(stage, "/World/InspectionCamera")
    assert camera
    view = np.array(UsdGeom.XformCache().GetLocalToWorldTransform(camera.GetPrim()), dtype=np.float64)
    focal = camera.GetFocalLengthAttr().Get()
    aperture = camera.GetHorizontalApertureAttr().Get()
    assert focal > 0 and aperture > 0
    rows = []
    depths = args.capture / "replicator"
    for i, x_ref in enumerate(TRUE_CUBE_X):
        d = np.load(depths / f"distance_to_image_plane_{i:04}.npy", allow_pickle=False)
        seg = np.load(depths / f"semantic_segmentation_{i:04}.npy", allow_pickle=False)
        labels = json.loads((depths / f"semantic_segmentation_labels_{i:04}.json").read_text())
        mask_id = next(int(key) for key, value in labels.items() if value["class"] == "part")
        y, x = np.nonzero((seg == mask_id) & np.isfinite(d) & (d > 0))
        height, width = d.shape
        fx = focal / aperture * width
        z = d[y, x]
        local = np.column_stack(((x + .5 - width / 2) * z / fx, (height / 2 - y - .5) * z / fx, -z, np.ones_like(z)))
        world = (local @ view)[:, :3]
        assert world.shape[0] >= 1000 and np.isfinite(world).all()
        midpoint = np.median(world, axis=0)
        np.save(args.output / f"surface-{i:02}.npy", world[::8].astype(np.float32))
        rows.append({"frame": i, "authored_center_x_m": x_ref, "visible_surface_median_xyz_m": midpoint.tolist(),
                     "valid_surface_pixels": len(world)})
    initial = rows[0]["visible_surface_median_xyz_m"][0]
    for row in rows:
        estimate = row["visible_surface_median_xyz_m"][0] - initial
        reference = row["authored_center_x_m"] - TRUE_CUBE_X[0]
        row.update({"estimated_relative_x_m": estimate, "authored_relative_x_m": reference,
                    "absolute_displacement_error_mm": abs(estimate-reference)*1000})
        print(f"frame {row['frame']} | measured dx {estimate:+.3f} m | authored {reference:+.3f} m", flush=True)
    (args.output / "result.json").write_text(json.dumps({
        "camera": "/World/InspectionCamera", "depth_channel": "distance_to_image_plane",
        "projection_assumption": "centered camera with horizontal aperture preserved and square pixels",
        "baseline": "frame 0 surface median; used only for displacement, not absolute center estimation",
        "authored_cube_x_source": "workbench_final_take.py",
        "frames": rows,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
