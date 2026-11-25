"""Build an observed RGB sky panorama and multi-view facade textures."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

from calibrate import unproject


def sample(array, uv, method=cv2.INTER_LINEAR):
    return cv2.remap(array, uv[..., 0].astype(np.float32), uv[..., 1].astype(np.float32), method)


def project_grid(camera, k):
    z = camera[..., 2]
    return camera[..., :2] * k[(0, 1), (0, 1)] / np.maximum(z[..., None], .1) + k[:2, 2], z


def bake_sky(rgb, labels, poses, k, out):
    width, height = 1024, 512
    yaw = (np.arange(width) + .5) * (2*np.pi/width) - np.pi
    pitch = np.pi/2 - (np.arange(height) + .5)*np.pi/height
    azimuth, elevation = np.meshgrid(yaw, pitch)
    directions = np.dstack([np.cos(azimuth)*np.cos(elevation),
                             np.sin(azimuth)*np.cos(elevation), np.sin(elevation)])
    summed = np.zeros(directions.shape, np.float32)
    weight = np.zeros(directions.shape[:2], np.float32)
    for image, label, pose, intrinsics in zip(rgb, labels, poses, k, strict=True):
        uv, forward = project_grid(directions @ pose[:3, :3], intrinsics)
        mask = cv2.erode((label == 10).astype(np.uint8), np.ones((13, 13), np.uint8))
        seen = sample(mask, uv, cv2.INTER_NEAREST) > 0
        # Prefer central, unobstructed sky pixels from all cameras and times.
        score = np.where(seen, np.maximum(forward, 0)**12, 0)
        summed += sample(image, uv).astype(np.float32)*score[..., None]
        weight += score
    valid = (weight >= 1.25) & (elevation >= 0)
    if not valid.any():
        raise ValueError("No multi-view sky samples")
    observed = summed / np.maximum(weight[..., None], 1e-6)
    neutral = np.median(observed[valid], axis=0)
    # Wrap the longitude so extrapolated color is smooth at the panorama seam.
    distance, indices = distance_transform_edt(~np.tile(valid, (1, 3)), return_indices=True)
    nearest = observed[indices[0, :, width:width*2], indices[1, :, width:width*2] % width]
    fade = np.clip(distance[:, width:width*2] / 32, 0, 1)[..., None]
    filled = nearest*(1-fade) + neutral*fade
    sky = np.where(valid[..., None], observed, filled)
    # Below the horizon the environment fades to the scene's neutral clear color.
    blend = np.clip(-elevation / .25, 0, 1)[..., None]
    sky = sky*(1-blend) + np.array([220, 225, 229])*blend
    Image.fromarray(np.rint(sky).clip(0, 255).astype(np.uint8)).save(out / "sky.webp", quality=91)
    return {"file": "sky.webp", "size": [width, height],
            "observed_upper_hemisphere_fraction": float(valid.sum()/(elevation >= 0).sum()),
            "unobserved_fill": "nearest sky color tapered to the median, neutral below the horizon"}


def collect_facade_points(depth, labels, poses, k):
    h, w = labels.shape[1:]
    row, col = np.mgrid[:h:5, :w:5]
    pixels = np.stack([col, row], axis=-1)
    points = []
    for i, pose in enumerate(poses):
        d = depth[i, ::5, ::5]
        ray = np.dstack([unproject(pixels, k[i]), np.ones(d.shape)])
        xyz = (ray*d[..., None]) @ pose[:3, :3].T + pose[:3, 3]
        building = cv2.erode(np.isin(labels[i], [2, 3]).astype(np.uint8), np.ones((7, 7), np.uint8))
        keep = building[::5, ::5].astype(bool) & (d > 1) & (d < 34)
        keep &= (xyz[..., 2] > .2) & (xyz[..., 2] < 10.5)
        keep &= (xyz[..., 0] > -30) & (xyz[..., 0] < 28) & (np.abs(xyz[..., 1]) < 19)
        points.append(xyz[keep])
    return np.concatenate(points)


def vertical_surfaces(points, tracks, limit=9):
    rng = np.random.default_rng(75)
    tracks = tracks[(np.abs(tracks[:, 1]) < 19) & (tracks[:, 0] > -31) & (tracks[:, 0] < 29)
                    & (tracks[:, 2] > .15) & (tracks[:, 2] < 10)]
    accepted = []

    def overlapping(normal, tangent, offset, bounds):
        for old_normal, old_tangent, old_offset, old in accepted:
            if abs(normal @ old_normal) < .98:
                continue
            endpoints = np.array(bounds)[[0, 2], None]*tangent + offset*normal
            projected = np.sort(endpoints @ old_tangent)
            overlap = min(projected[1], old[2]) - max(projected[0], old[0])
            if overlap > .5*min(bounds[2]-bounds[0], old[2]-old[0]):
                if np.max(np.abs(endpoints @ old_normal-old_offset)) < 2.4:
                    return True
        return False

    for _ in range(limit):
        use_tracks = len(tracks) >= 32
        minimum = 22 if use_tracks else 1050
        pool = tracks if use_tracks else points
        if len(pool) < minimum:
            break
        cloud = pool[rng.choice(len(pool), min(10000, len(pool)), replace=False), :2]
        pairs = cloud[rng.integers(len(cloud), size=(400, 2))]
        lines = pairs[:, 1] - pairs[:, 0]
        lengths = np.linalg.norm(lines, axis=-1)
        normals = lines[:, [1, 0]] * [-1, 1] / np.maximum(lengths[:, None], 1e-6)
        offsets = np.einsum("ni,ni->n", pairs[:, 0], normals)
        score = (np.abs(cloud @ normals.T - offsets) < (.22 if use_tracks else .26)).sum(axis=0)
        score[lengths < 2] = 0
        best = int(score.argmax())
        normal, offset = normals[best], offsets[best]
        near = np.abs(pool[:, :2] @ normal - offset) < (.26 if use_tracks else .36)
        if near.sum() < minimum:
            if use_tracks:
                tracks = tracks[:0]
                continue
            break
        group = pool[near]
        if use_tracks:
            tracks = tracks[~near]
            points = points[np.abs(points[:, :2] @ normal-offset) >= .38]
        else:
            points = points[~near]
        q = group[:, :2]
        mean = q.mean(axis=0)
        _, vectors = np.linalg.eigh(np.cov((q-mean).T))
        normal = vectors[:, 0]
        tangent = np.array([normal[1], -normal[0]])
        distance = float(np.median(q @ normal))
        u = group[:, :2] @ tangent
        # Split large holes along the plane to prevent one facade spanning an intersection.
        bin_size = 1.3 if use_tracks else .65
        occupied = np.unique(np.floor(u / bin_size).astype(int))
        for segment in np.split(occupied, np.where(np.diff(occupied) > 3)[0] + 1):
            if len(segment) < 4:
                continue
            select = (u >= segment[0]*bin_size) & (u < (segment[-1]+1)*bin_size)
            if select.sum() < (17 if use_tracks else 550):
                continue
            u0, u1 = np.percentile(u[select], [.5, 99.5])
            z0, z1 = np.percentile(group[select, 2], [.1, 99.8])
            if z1-z0 >= 1 and u1-u0 >= 2:
                bounds = [float(u0-.25), max(.05, float(z0-.7)),
                          float(u1+.25), min(11, float(z1+.40))]
                if not overlapping(normal, tangent, distance, bounds):
                    accepted.append((normal, tangent, distance, bounds))
                    yield normal, tangent, distance, bounds


def bake_wall(rgb, labels, depth, poses, k, normal, tangent, offset, bounds):
    u0, z0, u1, z1 = bounds
    width = int(np.clip(np.ceil((u1-u0)*66), 150, 1024))
    height = int(np.clip(np.ceil((z1-z0)*66), 100, 520))
    u, h = np.meshgrid(u0 + (np.arange(width)+.5)*(u1-u0)/width,
                       z1 - (np.arange(height)+.5)*(z1-z0)/height)
    xy = u[..., None]*tangent + offset*normal
    world = np.dstack([xy, h])
    best = np.zeros((height, width), np.float32)
    count = np.zeros_like(best, dtype=np.uint8)
    color = np.zeros(world.shape, dtype=np.uint8)
    for i, (pose, intrinsics) in enumerate(zip(poses, k, strict=True)):
        relative = world-pose[:3, 3]
        uv, z = project_grid(relative @ pose[:3, :3], intrinsics)
        wall = cv2.erode(np.isin(labels[i], [2, 3]).astype(np.uint8), np.ones((7, 7), np.uint8))
        semantic = sample(wall, uv, cv2.INTER_NEAREST) > 0
        seen = sample(depth[i], uv)
        incidence = np.abs(relative[..., :2] @ normal) / np.maximum(np.linalg.norm(relative, axis=-1), .1)
        valid = semantic & (z > 1.2) & (z < 36) & (incidence > .27)
        valid &= (seen > 0) & (seen-z > -np.maximum(.55, .16*z))
        valid &= seen-z < np.maximum(.75, .24*z)
        count += valid
        score = np.where(valid, incidence**2 / np.maximum(z, 1), 0)
        choose = score > best
        if choose.any():
            color[choose] = sample(rgb[i], uv)[choose]
            best[choose] = score[choose]
    mask = count >= 3
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
    if mask.mean() < .13:
        return None
    dist, nearest = distance_transform_edt(~mask, return_indices=True)
    color[~mask] = color[tuple(nearest[:, ~mask])]
    alpha = np.clip(cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)*40, 0, 255).astype(np.uint8)
    color[dist > 12] = 0
    return np.dstack([color, alpha]), float(mask.mean())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--facade-calibration", type=Path, help="Previous camera solution when facade validation favors it")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with np.load(args.geometry) as raw:
        rgb, depth = raw["observed_rgb"], raw["depth"]
    with np.load(args.calibration) as calibration:
        k, poses, tracks = [calibration[n] for n in ("intrinsics", "camera_pose", "facade_points")]
    wall_k, wall_poses = k, poses
    if args.facade_calibration:
        with np.load(args.facade_calibration) as calibration:
            wall_k, wall_poses = calibration["intrinsics"], calibration["camera_pose"]
    labels = np.load(args.inference / "labels.npy")
    args.output.mkdir(parents=True, exist_ok=True)
    sky = bake_sky(rgb, labels, poses, k, args.output)
    print(json.dumps(sky), flush=True)
    clouds = collect_facade_points(depth, labels, wall_poses, wall_k)
    walls = []
    for normal, tangent, offset, bounds in vertical_surfaces(clouds, tracks):
        result = bake_wall(rgb, labels, depth, wall_poses, wall_k, normal, tangent, offset, bounds)
        if result is None:
            continue
        image, coverage = result
        name = f"facade-{len(walls):02d}.webp"
        Image.fromarray(image).save(args.output / name, quality=92)
        u0, z0, u1, z1 = bounds
        corners = [[*(u*tangent + offset*normal), z] for u, z in [(u0,z0),(u1,z0),(u1,z1),(u0,z1)]]
        walls.append({"file": name, "corners": corners, "normal_xy": normal.tolist(),
                      "tangent_xy": tangent.tolist(), "offset": offset, "bounds": bounds,
                      "observed_fraction": coverage, "size": [image.shape[1], image.shape[0]]})
        print(name, round(coverage, 3), np.round(corners,1).tolist(), flush=True)
    if not walls:
        raise ValueError("No multi-view facades")
    (args.output / "surroundings.json").write_text(json.dumps({
        "schema": 1, "sky": sky, "facades": walls, "depth_surface_points": len(clouds),
        "facade_track_anchors": len(tracks), "minimum_facade_views": 3,
        "facade_camera_solution": "previous" if args.facade_calibration else "updated",
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
