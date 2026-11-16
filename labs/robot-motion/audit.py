"""Measure target tracking and completion frames in exported AutoData episodes."""

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    episodes = []
    with h5py.File(args.dataset, "r") as stream:
        group = stream["data"]
        for name, sample in sorted(group.items()):
            obs = sample["obs"]
            pose = obs["datagen_info/eef_pose/franka"][:]
            target = obs["datagen_info/target_eef_pose/franka"][:]
            wrist = pose[:, :3, 3]
            desired = target[:, :3, 3]
            error = np.linalg.norm(wrist - desired, axis=1)
            grip = np.sum(obs["gripper_pos"][:], axis=1)
            cubes = obs["cube_positions"][:].reshape(len(wrist), 3, 3)
            successful = sample["step_success"][:].astype(bool)
            count = len(wrist)
            assert pose.shape == target.shape == (count, 4, 4)
            assert count == len(sample["actions"]) == len(grip) == len(successful) == sample.attrs["num_samples"]
            assert np.isfinite(error).all() and np.isfinite(grip).all() and np.isfinite(cubes).all()
            found = np.flatnonzero(successful)
            target_tracking = {"mean_error_mm": float(error.mean()*1000),
                               "p95_error_mm": float(np.percentile(error, 95)*1000),
                               "peak_error_mm": float(error.max()*1000)}
            row = {"episode": name, "recorded_frames": count, "episode_marked_success": bool(sample.attrs["success"]),
                   "first_success_frame": None if not len(found) else int(found[0]),
                   "positive_success_frames": int(len(found)), "tracking": target_tracking,
                   "wrist": wrist.tolist(), "target": desired.tolist(), "error_mm": (error*1000).tolist(),
                   "gripper_position_sum": grip.tolist(), "cube_heights_m": cubes[:, :, 2].tolist()}
            episodes.append(row)
            print(f"{name} | {count} frames | first success {row['first_success_frame']} | p95 target error {target_tracking['p95_error_mm']:.1f} mm", flush=True)
        assert sum(row["recorded_frames"] for row in episodes) == group.attrs["total"]
    (args.output / "result.json").write_text(json.dumps({
        "source": args.dataset.name, "frame_index_origin": 0,
        "tracking": "Euclidean distance between recorded datagen wrist and target translations within each sampled frame",
        "episodes": episodes,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
