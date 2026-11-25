"""Bake a fixed road texture from calibrated, visibility-filtered camera RGB."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from scipy.optimize import least_squares

from calibrate import unproject


def basis(x, y):
    return np.stack([np.ones_like(x), x / 25, y / 10, (x / 25) ** 2], axis=-1)


def fit_road(da3, depth_pro, labels, intrinsics, poses, sparse):
    height, width = labels.shape[1:]
    y, x = np.mgrid[:height:4, :width:4]
    uv = np.stack([x, y], axis=-1)
    clouds = []
    scales = []
    corrected = da3.copy()
    for camera in range(6):
        d, p = da3[camera::6, ::4, ::4], depth_pro[camera::6, ::4, ::4]
        valid = (d > 1.5) & (d < 15) & (p > 0) & (labels[camera::6, ::4, ::4] == 0)
        scale = np.median(d[valid] / p[valid])
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError(f"No valid relative depth scale for camera {camera}")
        scales.append(float(scale))
        dp = depth_pro[camera::6] * scale
        d = da3[camera::6]
        agreement = (dp > 0) & (np.abs(dp-d) < 0.24*np.maximum(d, 0.1))
        corrected[camera::6] = np.where(agreement, 0.6*d + 0.4*dp, d)
    for i, (k, pose) in enumerate(zip(intrinsics, poses, strict=True)):
        d = corrected[i, ::4, ::4]
        is_road = labels[i, ::4, ::4] == 0
        ray = np.dstack([unproject(uv, k), np.ones(d.shape)])
        cloud = (ray * d[..., None]) @ pose[:3, :3].T + pose[:3, 3]
        keep = is_road & (d > 1.5) & (d < 13) & (np.abs(cloud[..., 2]) < 0.55)
        clouds.append(cloud[keep][::4])
    dense = np.concatenate(clouds)
    sparse = sparse[np.abs(sparse[:, 2]) < 0.5]
    # Triangulated paint points anchor a smooth surface. Robust loss rejects curbs and hillsides.
    points = np.concatenate([dense, sparse])
    weights = np.r_[np.ones(len(dense)), np.full(len(sparse), np.clip(len(dense) / max(1, len(sparse)), 1, 25))]
    matrix = basis(points[:, 0], points[:, 1])
    coeff = least_squares(lambda b: np.r_[(matrix @ b - points[:, 2]) * np.sqrt(weights),
                                          b * [2, 5, 10, 8]], np.zeros(4),
                          loss="soft_l1", f_scale=0.09,
                          bounds=([-0.35, -0.35, -0.35, -0.35], [0.35]*4)).x
    details = {"near_road_depth_points": len(dense), "triangulated_road_points": len(sparse),
               "depth_pro_to_relative_scale": scales,
               "median_height_residual_relative_units": float(np.median(np.abs(matrix @ coeff - points[:, 2])))}
    return coeff, corrected, details


def texture_atlas(rgb, labels, depth, intrinsics, poses, bounds, coeff, shape, exclude=()):
    width, height = shape
    x0, y0, x1, y1 = bounds
    x, y = np.meshgrid(x0 + (np.arange(width)+0.5)*(x1-x0)/width,
                       y1 - (np.arange(height)+0.5)*(y1-y0)/height)
    world = np.dstack([x, y, basis(x, y) @ coeff])
    colors = np.zeros((height, width, 3), np.float32)
    scores = np.zeros((height, width), np.float32)
    votes = np.zeros((height, width), np.uint8)
    for i, (k, pose) in enumerate(zip(intrinsics, poses, strict=True)):
        if i in exclude:
            continue
        camera = (world - pose[:3, 3]) @ pose[:3, :3]
        z = camera[..., 2]
        u = (camera[..., 0]/np.maximum(z, .1)*k[0, 0]+k[0, 2]).astype(np.float32)
        v = (camera[..., 1]/np.maximum(z, .1)*k[1, 1]+k[1, 2]).astype(np.float32)
        safe_road = cv2.erode((labels[i] == 0).astype(np.uint8), np.ones((5, 5), np.uint8))
        road = cv2.remap(safe_road, u, v, cv2.INTER_NEAREST) > 0
        seen_depth = cv2.remap(depth[i], u, v, cv2.INTER_LINEAR)
        # Prevent projection through nearer surfaces. Keep incidence angles with usable detail.
        quality = (pose[2, 3] - world[..., 2]) * k[1, 1] / np.maximum(z, 1.0)**2
        valid = road & (z > 1.1) & (z < 24) & (quality > 2.3)
        valid &= (seen_depth > 0) & (np.abs(seen_depth - z) < np.maximum(.45, .30*z))
        votes += valid
        score = np.where(valid, quality, 0)
        better = score > scores
        if np.any(better):
            color = cv2.remap(rgb[i], u, v, cv2.INTER_LINEAR)
            colors[better] = color[better]
            scores[better] = score[better]
    # Shrink ragged edges. Fill color into the transparent margin for mipmap filtering.
    mask = votes >= 2
    if not np.any(mask):
        raise ValueError("No road texels have multi-view support")
    distance, nearest = distance_transform_edt(~mask, return_indices=True)
    colors[~mask] = colors[tuple(nearest[:, ~mask])]
    alpha = (np.clip(cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5) / 8, 0, 1)*255).astype(np.uint8)
    colors[distance > 24] = 0
    return np.dstack([np.rint(colors).astype(np.uint8), alpha]), votes


def compare_heldout(rgb, labels, intrinsics, poses, bounds, coeff, atlas, ids):
    """Measure brightness-normalized RGB errors only on jointly visible road pixels."""
    height, width = labels.shape[1:]
    y, x = np.mgrid[:height:2, :width:2]
    uv = np.stack([x, y], axis=-1)
    out = []
    x0, y0, x1, y1 = bounds
    for i in ids:
        ray = np.dstack([unproject(uv, intrinsics[i]), np.ones(x.shape)]) @ poses[i, :3, :3].T
        center = poses[i, :3, 3]
        down = ray[..., 2] < -0.03
        scale = -center[2] / np.minimum(ray[..., 2], -.03)
        for _ in range(8):
            xy = center[:2]+ray[..., :2]*scale[..., None]
            scale = (basis(xy[..., 0], xy[..., 1]) @ coeff-center[2])/np.minimum(ray[..., 2], -.03)
        u = ((xy[..., 0]-x0)/(x1-x0)*atlas.shape[1]-.5).astype(np.float32)
        v = ((y1-xy[..., 1])/(y1-y0)*atlas.shape[0]-.5).astype(np.float32)
        rgba = cv2.remap(atlas, u, v, cv2.INTER_LINEAR)
        visible = down & (rgba[..., 3] > 245) & (labels[i, ::2, ::2] == 0) & (scale > 1.4) & (scale < 14)
        gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY).astype(np.float32)
        gray -= cv2.GaussianBlur(gray, (0, 0), 2.0)
        known = cv2.cvtColor(rgb[i, ::2, ::2], cv2.COLOR_RGB2GRAY).astype(np.float32)
        known -= cv2.GaussianBlur(known, (0, 0), 2.0)
        visible = cv2.erode(visible.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        out.append((visible, np.abs(gray-known), np.abs(known)))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--scene", type=Path, required=True)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    with np.load(args.geometry) as raw:
        rgb, depth = raw["observed_rgb"], raw["depth"]
    with np.load(args.calibration / "calibration.npz") as refined:
        k, poses, sparse = [refined[name] for name in ("intrinsics", "camera_pose", "ground_points")]
    labels = np.load(args.inference / "labels.npy")
    depth_pro = np.load(args.inference / "depth-pro.npy", mmap_mode="r")
    coeff, corrected, details = fit_road(depth, depth_pro, labels, k, poses, sparse)
    centers = poses[1::6, :3, 3]
    bounds = [float(centers[:, 0].min()-7), -10, float(centers[:, 0].max()+13), 10]
    size = (args.width, round(args.width*(bounds[3]-bounds[1])/(bounds[2]-bounds[0])))
    calibration = json.loads((args.calibration / "calibration.json").read_text())
    if args.evaluate:
        ids = [6*f+1 for f in (2, 5, 8, 11, 14)]
        record = next(m for m in json.loads(args.scene.read_text())["models"] if m["id"] == "calibrated")
        initial_k, initial_pose = np.array(record["intrinsics"]), np.array(record["camera_to_world"])
        before, _ = texture_atlas(rgb, labels, depth, initial_k, initial_pose, bounds, coeff, size, ids)
        after, _ = texture_atlas(rgb, labels, corrected, k, poses, bounds, coeff, size, ids)
        a = compare_heldout(rgb, labels, initial_k, initial_pose, bounds, coeff, before, ids)
        b = compare_heldout(rgb, labels, k, poses, bounds, coeff, after, ids)
        errors = [[], []]
        for (av, ae, target), (bv, be, _) in zip(a, b, strict=True):
            shared = av & bv & (target > 3.0)
            errors[0].extend(ae[shared])
            errors[1].extend(be[shared])
        if errors[0]:
            details["heldout_texture"] = {
                "reference_road_pixels": len(errors[0]), "heldout_atlas_source_views": ids,
                "mean_luminance_detail_error_initial": float(np.mean(errors[0])),
                "mean_luminance_detail_error_refined": float(np.mean(errors[1])),
                "scope": "These views were withheld from texture baking, but were available for calibration and surface fitting."
            }
    atlas, votes = texture_atlas(rgb, labels, corrected, k, poses, bounds, coeff, size)
    args.output.mkdir(parents=True, exist_ok=True)
    Image.fromarray(atlas).save(args.output / "ground.webp", lossless=True, method=5)
    np.save(args.output / "road-samples.npy", votes)
    reference = json.loads(args.scene.read_text())["frames"]
    report = {
        "schema": 1, "texture": "ground.webp", "bounds_xy": bounds, "height_coefficients": coeff.tolist(),
        "camera_to_world": poses.tolist(), "intrinsics": k.tolist(),
        "ground_height_at_ego": [float(basis(np.array(x), np.array(y)) @ coeff) for x, y, _ in (f["ground_position"] for f in reference)],
        "atlas_pixels": list(size), "two_view_coverage_relative_units_squared": float((votes >= 2).mean()*(bounds[2]-bounds[0])*(bounds[3]-bounds[1])),
        "surface": details, "calibration": calibration,
        "source": "PandaSet RGB; existing RGB-only SfM/DA3; Mask2Former, LoMa-B and Depth Pro 2 B",
    }
    (args.output / "road.json").write_text(json.dumps(report, separators=(",", ":")) + "\n")
    print(json.dumps({key: report[key] for key in ("atlas_pixels", "two_view_coverage_relative_units_squared", "surface")}, indent=2))


if __name__ == "__main__":
    main()
