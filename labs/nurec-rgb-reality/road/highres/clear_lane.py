"""Remove static Gaussian floaters from the observed ego lane before SPZ export."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads((args.fit/"fit.json").read_text())
    centers = np.array([row["pose"] for row in report["front_path"]])[:, :2, 3]
    path = [centers[0]]
    for start, end in zip(centers, centers[1:]):
        steps = max(1, int(np.ceil(np.linalg.norm(end-start)/.3)))
        path.extend(np.linspace(start, end, steps+1)[1:])
    with (args.fit/"scene.ply").open("rb") as source:
        header = []
        while (line := source.readline()) and line != b"end_header\n":
            header.append(line)
        if not line:
            raise ValueError("Missing Gaussian PLY header")
        properties = [line for line in header if line.startswith(b"property float ")]
        points = np.fromfile(source, dtype="<f4").reshape(-1, len(properties))
    distances = cKDTree(path).query(points[:, :2])[0]
    extent = np.clip(np.exp(points[:, 3:6]).max(axis=1), 0, .85)
    low = points[:, 2] > .24
    high = points[:, 2] < 3.1
    keep = (distances >= 1.7+extent) | ~low | ~high
    count = np.count_nonzero(keep)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/"scene.ply").open("wb") as result:
        result.writelines(f"element vertex {count}\n".encode() if line.startswith(b"element vertex ") else line for line in header)
        result.write(b"end_header\n")
        points[keep].tofile(result)
    metadata = {
        "before_lane_cleanup_gaussians": len(points),
        "gaussians": int(count),
        "lane_cleanup": "Remove static Gaussians between 0.24 and 3.1 coordinate units above the traced ego lane, with a 1.7-unit radius plus bounded Gaussian extent.",
    }
    (args.output/"lane.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(f"Removed {len(points)-count} floaters above the recorded lane; kept {count} splats")


if __name__ == "__main__":
    main()
