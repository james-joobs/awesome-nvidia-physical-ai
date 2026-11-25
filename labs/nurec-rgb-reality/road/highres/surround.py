"""Package synchronized RGB views and calibrated camera poses."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("input", "sfm", "fit", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads((args.input/"input.json").read_text())
    rows = json.loads((args.sfm/"cameras.json").read_text())["records"]
    fit = json.loads((args.fit/"fit.json").read_text())
    pose_data = np.load(args.fit/"geometry.npz")
    registered = {(row["frame"], row["camera"]): (pose, k)
                  for row, pose, k in zip(rows, pose_data["poses"], pose_data["intrinsics"], strict=True)}
    path = fit["front_path"]
    frame_indices = {row["frame"]: i for i, row in enumerate(path)}
    frames = [{"time": round((row["frame"]-path[0]["frame"])/10, 3), "rgb": {}, "cameras": {}}
              for row in path]
    rgb = args.output/"rgb"
    rgb.mkdir(parents=True, exist_ok=True)
    for row in source["images"]:
        key = row["frame"], row["camera"]
        if row["frame"] not in frame_indices:
            continue
        index = frame_indices[row["frame"]]
        camera = source["camera_names"][row["camera"]]
        image = f"{index:03d}-{camera}.webp"
        with Image.open(args.input/"sources"/row["file"]) as original:
            original.thumbnail((768, 768), Image.Resampling.LANCZOS)
            original.save(rgb/image, quality=79)
        frames[index]["rgb"][camera] = f"rgb/{image}"
        if key not in registered:
            continue
        pose, k = registered[key]
        frames[index]["cameras"][camera] = {
            "pose": np.round(pose[:3], 5).tolist(),
            "fov": round(float(np.degrees(2*np.arctan(row["size"][1]/(2*k[1, 1])))), 2),
        }
    report = {"schema": 1, "source_scene": source["scene"], "frames": frames}
    (args.output/"surround.json").write_text(json.dumps(report, separators=(",", ":"))+"\n")
    print(f"{len(frames)} RGB timestamps, {sum(len(frame['cameras']) for frame in frames)} registered cameras")


if __name__ == "__main__":
    main()
