"""Refine an RGB-derived rig with LoMa tracks and regularized bundle adjustment."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from scipy.spatial.transform import Rotation


def tracks_from_matches(keypoints, links, labels):
    parent = {}
    views = {}

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    height, width = labels.shape[1:]
    for first, i, second, j, _ in links[np.argsort(-links[:, 4])]:
        a, b = (int(first), int(i)), (int(second), int(j))
        for view, feature in (a, b):
            x, y = np.rint(keypoints[view, feature]).astype(int)
            if not (2 <= x < width - 2 and 2 <= y < height - 2):
                break
            # Keep fixed structures and road paint. Exclude dynamic boundaries and sky.
            if np.max(labels[view, y-2:y+3, x-2:x+3]) >= 10:
                break
        else:
            for key in (a, b):
                if key not in parent:
                    parent[key] = key
                    views[key] = {key[0]}
            ra, rb = root(a), root(b)
            if ra != rb and not views[ra].intersection(views[rb]):
                parent[rb] = ra
                views[ra].update(views.pop(rb))
    groups = {}
    for a in parent:
        groups.setdefault(root(a), []).append(a)
    return [np.array(group) for group in groups.values() if len(group) >= 3]


def unproject(pixel, k):
    return (pixel - k[..., :2, 2]) / k[..., (0, 1), (0, 1)]


def triangulate(pixel, k, poses):
    rays = np.column_stack([unproject(pixel, k), np.ones(len(pixel))])
    rays = np.einsum("nij,nj->ni", poses[:, :3, :3], rays)
    rays /= np.linalg.norm(rays, axis=-1, keepdims=True)
    matrix = np.eye(3) - rays[:, :, None] * rays[:, None, :]
    cameras = poses[:, :3, 3]
    return np.linalg.lstsq(matrix.sum(0), np.einsum("nij,nj->i", matrix, cameras),
                          rcond=1e-8)[0]


def project(world, k, poses):
    camera = np.einsum("nji,nj->ni", poses[:, :3, :3], world - poses[:, :3, 3])
    pixel = camera[:, :2] / np.maximum(camera[:, 2:], 1e-3)
    return pixel * k[:, (0, 1), (0, 1)] + k[:, :2, 2], camera[:, 2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, required=True)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference", type=Path, help="Earlier calibration.npz to validate and retain if needed")
    parser.add_argument("--fixed-rig", action="store_true", help="Reproduce the first road and facade camera fit")
    args = parser.parse_args()
    record = next(m for m in json.loads(args.scene.read_text())["models"] if m["id"] == "calibrated")
    initial = np.array(record["camera_to_world"])
    intrinsics = np.array(record["intrinsics"])
    labels = np.load(args.inference / "labels.npy")
    with np.load(args.inference / "matches.npz") as matches:
        pixels = matches["keypoints"]
        groups = tracks_from_matches(pixels, matches["links"], labels)

    accepted = []
    for track in groups:
        v, f = track.T
        uv = pixels[v, f]
        xyz = triangulate(uv, intrinsics[v], initial[v])
        projected, depth = project(xyz, intrinsics[v], initial[v])
        if np.min(depth) > 0.5 and np.max(depth) < 95 and np.max(np.linalg.norm(projected - uv, axis=1)) < 7:
            u, y = np.rint(uv).astype(int).T
            ids = labels[v, y, u]
            category = "road" if np.all(ids == 0) else "facade" if np.all(np.isin(ids, [2, 3])) else "other"
            accepted.append((v, uv, xyz, category))
    if len(accepted) < 100:
        raise ValueError(f"Insufficient well-conditioned tracks: {len(accepted)}")
    rng = np.random.default_rng(2026)
    rng.shuffle(accepted)
    split = min(500, max(30, len(accepted) // 5))
    validation = accepted[:split]
    training = accepted[split:split + 3200]
    view = np.concatenate([t[0] for t in training])
    pixel = np.concatenate([t[1] for t in training])
    landmark = np.repeat(np.arange(len(training)), [len(t[0]) for t in training])
    xyz0 = np.array([t[2] for t in training])
    frames = len(initial) // 6
    frame = np.arange(len(initial)) // 6
    physical = np.arange(len(initial)) % 6
    centers = initial[1::6, :3, 3]
    rig_start = 6 * frames
    rig_cameras = [] if args.fixed_rig else [0, 2, 3, 4, 5]
    camera_count = rig_start + 6 * len(rig_cameras)

    def cameras(parameters):
        adjusted_k = intrinsics.copy()
        adjusted_k[:, (0, 1), (0, 1)] *= np.exp(parameters[:6])[physical, None]
        variation = np.vstack([np.zeros(6), parameters[6:rig_start].reshape(-1, 6)])
        rotation = Rotation.from_rotvec(variation[:, :3]).as_matrix()[frame]
        rig = np.zeros((6, 6))
        rig[rig_cameras] = parameters[rig_start:camera_count].reshape(-1, 6)
        local_rotation = Rotation.from_rotvec(rig[:, :3]).as_matrix()[physical]
        adjusted_pose = initial.copy()
        adjusted_pose[:, :3, :3] = rotation @ initial[:, :3, :3] @ local_rotation
        rig_offset = initial[:, :3, 3] - centers[frame]
        rig_offset += np.einsum("nij,nj->ni", initial[:, :3, :3], rig[physical, 3:])
        adjusted_pose[:, :3, 3] = np.einsum("nij,nj->ni", rotation, rig_offset)
        adjusted_pose[:, :3, 3] += centers[frame] + variation[frame, 3:]
        return adjusted_k, adjusted_pose

    def residual(parameters):
        k, poses = cameras(parameters)
        landmarks = parameters[camera_count:].reshape(-1, 3)
        projections, _ = project(landmarks[landmark], k[view], poses[view])
        # Remove the gauge freedoms with the first rig pose and a soft prior on the rig.
        pose = parameters[6:rig_start].reshape(-1, 6)
        priors = pose * [42, 42, 42, 12, 12, 24]
        rig_prior = parameters[rig_start:camera_count].reshape(-1, 6) * [100, 100, 100, 45, 45, 45]
        smooth = (np.empty((0, 6)) if args.fixed_rig else
                  np.diff(np.vstack([np.zeros(6), pose]), n=2, axis=0) * [85, 85, 85, 19, 19, 38])
        return np.r_[(projections - pixel).ravel(), parameters[:6] * 70, priors.ravel(),
                     rig_prior.ravel(), smooth.ravel()]

    x0 = np.r_[np.zeros(camera_count), xyz0.ravel()]
    sparsity = lil_matrix((len(residual(x0)), len(x0)), dtype=np.int8)
    for observation, (v, p) in enumerate(zip(view, landmark, strict=True)):
        row = slice(observation * 2, observation * 2 + 2)
        sparsity[row, v % 6] = 1
        if v // 6:
            sparsity[row, 6 * (v // 6):6 * (v // 6 + 1)] = 1
        if v % 6 in rig_cameras:
            i = rig_start + 6 * rig_cameras.index(v % 6)
            sparsity[row, i:i+6] = 1
        sparsity[row, camera_count + p * 3:camera_count + p * 3 + 3] = 1
    for i in range(camera_count):
        sparsity[len(view) * 2 + i, i] = 1
    for f in range(0 if args.fixed_rig else frames-2):
        row = len(view)*2 + camera_count + 6*f
        for df in range(3):
            if f+df:
                sparsity[row:row+6, 6*(f+df):6*(f+df+1)] = 1

    limits = np.r_[np.full(6, 0.10), np.tile([0.035] * 3 + [0.16, 0.16, 0.08], frames - 1),
                   np.tile([0.02] * 3 + [0.045] * 3, len(rig_cameras)),
                   np.full(xyz0.size, np.inf)]
    budget = 65 if args.fixed_rig else 220
    result = least_squares(residual, x0, jac_sparsity=sparsity.tocsr(), bounds=(-limits, limits),
                           loss="soft_l1", f_scale=1.2, x_scale="jac", max_nfev=budget, verbose=1)
    k, poses = cameras(result.x)

    def heldout(k, poses):
        error = {"all": [], "road": [], "facade": [], "other": []}
        for views, uv, _, category in validation:
            xyz = triangulate(uv[[0, -1]], k[views[[0, -1]]], poses[views[[0, -1]]])
            projected, _ = project(xyz, k[views[1:-1]], poses[views[1:-1]])
            values = np.linalg.norm(projected - uv[1:-1], axis=1)
            error["all"].extend(values)
            error[category].extend(values)
        summary = {name: {"median_px": float(np.median(values)),
                          "p90_px": float(np.percentile(values, 90)), "observations": len(values)}
                   for name, values in error.items() if values}
        return {**summary.pop("all"), "by_surface": summary}

    before, after = heldout(intrinsics, initial), heldout(k, poses)
    reference_k, reference_poses = intrinsics, initial
    if args.reference:
        with np.load(args.reference) as reference:
            reference_k, reference_poses = reference["intrinsics"], reference["camera_pose"]
    reference_score = heldout(reference_k, reference_poses)
    use_refinement = (
        after["median_px"] <= reference_score["median_px"] + (0 if args.fixed_rig else 0.03)
        and after["p90_px"] < reference_score["p90_px"]
    )
    args.output.mkdir(parents=True, exist_ok=True)
    selected_k, selected_pose = (k, poses) if use_refinement else (reference_k, reference_poses)
    ground_points = [
        triangulate(uv, selected_k[v], selected_pose[v])
        for v, uv, _, category in training if category == "road"
    ]
    facade_points = [
        triangulate(uv, selected_k[v], selected_pose[v])
        for v, uv, _, category in training if category == "facade"
    ]
    np.savez_compressed(args.output / "calibration.npz", intrinsics=selected_k,
                        camera_pose=selected_pose, ground_points=np.array(ground_points).reshape(-1, 3),
                        facade_points=np.array(facade_points).reshape(-1, 3))
    report = {"training_tracks": len(training), "training_observations": len(view),
              "validation_tracks": len(validation), "heldout_initial": before, "heldout_refined": after,
              "heldout_previous": reference_score, "heldout_selected": after if use_refinement else reference_score,
              "solver_converged": bool(result.success), "solver_evaluations": int(result.nfev),
              "refinement_selected": use_refinement, "road_tracks": len(ground_points),
              "facade_tracks": len(facade_points), "shared_rig_correction_selected": use_refinement and not args.fixed_rig,
              "focal_scale_by_camera": np.exp(result.x[:6]).tolist(),
              "max_camera_shift": float(np.max(np.linalg.norm(poses[:, :3, 3] - initial[:, :3, 3], axis=1)))}
    (args.output / "calibration.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
