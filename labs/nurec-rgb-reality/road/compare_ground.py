"""Compare two road bakes on the same held-out source-view detail pixels."""
import argparse
import json
from pathlib import Path

import numpy as np

from bake import compare_heldout, fit_road, texture_atlas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--previous", type=Path, nargs=2, required=True, metavar=("CALIBRATION", "BAKE"))
    parser.add_argument("--candidate", type=Path, nargs=2, required=True, metavar=("CALIBRATION", "BAKE"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with np.load(args.geometry) as raw:
        rgb, depth = raw["observed_rgb"], raw["depth"]
    depth_pro = np.load(args.inference / "depth-pro.npy", mmap_mode="r")
    labels = np.load(args.inference / "labels.npy")
    excluded = [13, 31, 49, 67, 85]
    heldout = []
    for calibration, bake in (args.previous, args.candidate):
        with np.load(calibration / "calibration.npz") as raw:
            k, poses, sparse = [raw[key] for key in ("intrinsics", "camera_pose", "ground_points")]
        report = json.loads((bake / "road.json").read_text())
        _, corrected, _ = fit_road(depth, depth_pro, labels, k, poses, sparse)
        bounds, coeff = report["bounds_xy"], np.array(report["height_coefficients"])
        atlas, _ = texture_atlas(rgb, labels, corrected, k, poses, bounds, coeff,
                                 report["atlas_pixels"], excluded)
        heldout.append(compare_heldout(rgb, labels, k, poses, bounds, coeff, atlas, excluded))
    errors = [[], []]
    for (seen_a, diff_a, target), (seen_b, diff_b, _) in zip(*heldout, strict=True):
        valid = seen_a & seen_b & (target > 3)
        errors[0].extend(diff_a[valid])
        errors[1].extend(diff_b[valid])
    if not errors[0]:
        raise ValueError("No jointly visible detail pixels in withheld frames")
    report = {"reference_detail_pixels": len(errors[0]), "previous": float(np.mean(errors[0])),
              "candidate": float(np.mean(errors[1])), "atlas_source_views_excluded": excluded}
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
