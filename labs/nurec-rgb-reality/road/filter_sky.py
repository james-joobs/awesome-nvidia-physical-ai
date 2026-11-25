"""Cull high sky splats and splats covered by observed facade textures."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def facade_mask(xyz, radii, folder, records):
    covered = np.zeros(len(xyz), dtype=bool)
    for wall in records:
        u0, z0, u1, z1 = wall["bounds"]
        plane_distance = xyz[:, :2] @ wall["normal_xy"] - wall["offset"]
        u = (xyz[:, :2] @ wall["tangent_xy"] - u0)/(u1-u0)
        v = (z1-xyz[:, 2])/(z1-z0)
        ids = np.flatnonzero((np.abs(plane_distance) < .30+np.minimum(.28, radii))
                            & (u > .01) & (u < .99) & (v > .01) & (v < .99))
        with Image.open(folder / wall["file"]) as image:
            alpha = np.array(image.getchannel("A"))
        y, x = (v[ids]*alpha.shape[0]).astype(int), (u[ids]*alpha.shape[1]).astype(int)
        covered[ids[alpha[y, x] >= 218]] = True
    return covered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ply", type=Path, required=True)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, help="DA3 geometry for depth-aware sky rejection")
    parser.add_argument("--surroundings", type=Path, help="Folder of facade textures and manifest")
    args = parser.parse_args()

    names, header = [], []
    with args.ply.open("rb") as stream:
        if stream.readline().strip() != b"ply":
            raise ValueError("Expected a PLY")
        header.append("ply")
        for line in stream:
            line = line.decode("ascii").strip()
            header.append(line)
            if line.startswith("element vertex"):
                count = int(line.split()[-1])
            if line.startswith("property "):
                _, kind, name = line.split()
                if kind != "float":
                    raise ValueError("Expected all-float Gaussian PLY")
                names.append(name)
            if line == "end_header":
                break
        if "format binary_little_endian 1.0" not in header:
            raise ValueError("Expected binary little-endian PLY")
        data = np.fromfile(stream, dtype=[(n, "<f4") for n in names], count=count)
    if len(data) != count:
        raise ValueError("Incomplete Gaussian PLY")

    xyz = np.column_stack([data[n] for n in ("x", "y", "z")])
    scale_names = [f"scale_{i}" for i in range(3)]
    scale = np.column_stack([data[name] for name in scale_names])
    radii = np.exp(np.clip(scale.max(axis=1), -11, 3))
    candidates = np.flatnonzero(xyz[:, 2] > 1.65)
    query = xyz[candidates]
    labels = np.load(args.inference / "labels.npy", mmap_mode="r")
    with np.load(args.calibration / "calibration.npz") as refined:
        intrinsics, poses = refined["intrinsics"], refined["camera_pose"]
    sky = np.zeros(len(query), dtype=np.uint16)
    solid = np.zeros_like(sky)
    depth_support = np.zeros_like(sky)
    tight_support = np.zeros_like(sky)
    free_space = np.zeros_like(sky)
    skyline_overlap = np.zeros_like(sky)
    depth = None
    if args.geometry:
        with np.load(args.geometry) as raw:
            depth = raw["depth"]
    height, width = labels.shape[1:]
    for i, (k, pose) in enumerate(zip(intrinsics, poses, strict=True)):
        camera = (query - pose[:3, 3]) @ pose[:3, :3]
        z = camera[:, 2]
        uv = camera[:, :2] / np.maximum(z[:, None], 0.25)
        u, v = np.rint(uv*k[(0, 1), (0, 1)] + k[:2, 2]).astype(int).T
        inside = (z > 0.25) & (u >= 5) & (u < width-5) & (v >= 5) & (v < height-5)
        indices = np.flatnonzero(inside)
        sky_mask = (labels[i] == 10).astype(np.uint8)
        core = cv2.erode(sky_mask, np.ones((9, 9), dtype=np.uint8))
        possible = cv2.dilate(sky_mask, np.ones((9, 9), dtype=np.uint8))
        samples = v[indices], u[indices]
        sky[indices] += core[samples]
        solid[indices] += 1 - possible[samples]
        if depth is not None:
            # Trim very wide kernels crossing the observed skyline while keeping their centers.
            footprint = 2.2*max(k[0, 0], k[1, 1])*radii[candidates[indices]]/z[indices]
            distance_to_sky = cv2.distanceTransform(1-core, cv2.DIST_L2, 5)[samples]
            skyline_overlap[indices] += (footprint > distance_to_sky) & (footprint > 10)
            measured = depth[i, *samples]
            observed_surface = (possible[samples] == 0) & (measured > 0)
            distance = np.abs(measured-z[indices])
            depth_support[indices] += observed_surface & (distance < np.maximum(.40, .13*z[indices]))
            tight_support[indices] += observed_surface & (distance < np.maximum(.20, .055*z[indices]))
            # A Gaussian in front of the measured surface has no RGB-D support along this ray.
            static = (labels[i][samples] < 10) & (measured > 0)
            free_space[indices] += static & (measured-z[indices] > np.maximum(.7, .19*z[indices]))
    cutoff = (sky >= 3) & (sky >= 3 * solid)
    floating = np.zeros(len(query), dtype=bool)
    if depth is not None:
        cutoff |= (sky >= 5) & (sky*3 >= solid*2) & (sky >= 4*depth_support) & (depth_support <= 2)
        # A large, high splat can smear across much more sky than its center.
        # Require repeat sky votes and weak surface support before removing it.
        cutoff |= ((query[:, 2] > 2.7) & (radii[candidates] > .34)
                   & (sky >= 3) & (sky*2 >= solid) & (tight_support <= 2)
                   & (sky >= 3*tight_support))
        floating = ((query[:, 2] > 2.5) & (radii[candidates] > .18)
                    & (sky >= 2) & (sky + free_space >= 6)
                    & (sky + free_space >= 3*tight_support)
                    & (free_space + sky >= .55*(solid + sky)))
        floating &= ~cutoff
    sky_removed = np.zeros(count, dtype=bool)
    sky_removed[candidates[cutoff]] = True
    airborne = np.zeros(count, dtype=bool)
    airborne[candidates[floating]] = True
    walls_removed = np.zeros(count, dtype=bool)
    if args.surroundings:
        walls = json.loads((args.surroundings / "surroundings.json").read_text())["facades"]
        walls_removed = facade_mask(xyz, radii, args.surroundings, walls)
    remove = sky_removed | airborne | walls_removed
    wide = candidates[(query[:, 2] > 2.3) & (radii[candidates] > .32)
                      & (skyline_overlap >= 4) & (skyline_overlap*2 >= solid+sky)]
    wide = wide[~remove[wide]]
    reduction = np.log(radii[wide]/.32)
    for name in scale_names:
        data[name][wide] -= reduction
    retained = int((~remove).sum())
    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / "sky-filtered.ply"
    header = [f"element vertex {retained}" if line.startswith("element vertex ") else line for line in header]
    with out.open("wb") as stream:
        stream.write(("\n".join(header)+"\n").encode("ascii"))
        stream.write(data[~remove].tobytes())
    details = {"gaussians_in": count, "gaussians_removed": int(remove.sum()),
               "gaussians_retained": retained, "relative_minimum_height": 1.65,
               "minimum_sky_votes": 3, "minimum_sky_to_non_sky_ratio": 3,
               "sky_removed": int(sky_removed.sum()), "airborne_removed": int(airborne.sum()),
               "facade_removed": int((walls_removed & ~sky_removed & ~airborne).sum()),
               "skyline_kernels_trimmed": len(wide),
               "depth_aware_sky": depth is not None,
               "ply_sha256": hashlib.file_digest(out.open("rb"), "sha256").hexdigest()}
    (args.output / "sky-filter.json").write_text(json.dumps(details, indent=2)+"\n")
    print(json.dumps(details))


if __name__ == "__main__":
    main()
