"""Package synchronized RGB views, calibrated camera poses and semantic ground tracks."""
import argparse
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment

CLASSES = {
    11: "person", 12: "rider", 13: "car", 14: "truck",
    15: "bus", 16: "tram", 17: "motorcycle", 18: "bicycle",
}
LENGTH = {"car": 4.2, "truck": 7.5, "bus": 9, "tram": 11, "motorcycle": 1.6}


def detect(row, pose, intrinsic, labels_path, floor):
    labels = cv2.imread(str(labels_path / row["file"].replace(".jpg", ".png")), 0)
    if labels is None:
        raise ValueError(f"Missing semantic labels for {row['file']}")
    height, width = labels.shape
    inverse = np.linalg.inv(intrinsic)
    for semantic_id, name in CLASSES.items():
        count, instances, stats, _ = cv2.connectedComponentsWithStats(
            (labels == semantic_id).astype(np.uint8), connectivity=8)
        for component in range(1, count):
            x, y, w, h, area = stats[component]
            if area < 105 or w < 6 or h < 9 or y+h > .94*height:
                continue
            iy, ix = np.nonzero(instances[y:y+h, x:x+w] == component)
            bottom = np.quantile(iy, .96)
            u = x+np.median(ix[iy >= bottom-2])
            ray = pose[:3, :3] @ inverse @ [u, y+bottom, 1.0]
            if ray[2] >= -.035:
                continue
            depth = (floor-pose[2, 3])/ray[2]
            if not 2.1 < depth < 55:
                continue
            contact = pose[:2, 3]+depth*ray[:2]
            # Visible tires meet the ground closer to the camera than the center
            # of the vehicle. Use a conservative class-dependent inward offset.
            point = contact+ray[:2]/np.linalg.norm(ray[:2])*LENGTH.get(name, .8)*.22
            yield name, point, float(area/(width*height))


def merge(detections):
    kept = []
    for name, point, quality in sorted(detections, key=lambda item: item[2], reverse=True):
        radius = 1.4 if name in LENGTH else .65
        if all(other != name or np.linalg.norm(point-center) > radius for other, center in kept):
            kept.append((name, point))
    return kept


def tracks(series):
    previous, history = {}, {}
    next_id = 1
    for frame, hits in enumerate(series):
        ids = list(previous)
        assigned = {}
        if ids and hits:
            costs = np.full((len(ids), len(hits)), 1e4)
            for i, track_id in enumerate(ids):
                name, position, velocity, last = previous[track_id]
                gap = frame-last
                radius = (6.0 if name in LENGTH else 2.3)*gap
                for j, (kind, point) in enumerate(hits):
                    distance = np.linalg.norm(position+velocity*gap-point)
                    if kind == name and distance < radius:
                        costs[i, j] = distance
            ii, jj = linear_sum_assignment(costs)
            assigned = {j: ids[i] for i, j in zip(ii, jj, strict=True) if costs[i, j] < 1e4}
        for j, (name, point) in enumerate(hits):
            if j in assigned:
                track_id = assigned[j]
                _, old, velocity, last = previous[track_id]
                velocity = .35*velocity+.65*(point-old)/(frame-last)
            else:
                track_id = next_id
                next_id += 1
                velocity = np.zeros(2)
                history[track_id] = (name, [])
            history[track_id][1].append((frame, point))
            previous[track_id] = (name, point, velocity, frame)
        previous = {key: value for key, value in previous.items() if frame-value[3] < 2}
    return history


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
    frames = [{"time": round((row["frame"]-path[0]["frame"])/10, 3), "rgb": {}, "cameras": {}, "actors": []}
              for row in path]
    hits = [[] for _ in frames]
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
        floor = np.clip(path[index]["pose"][2][3]-1.8, -.65, .65)
        hits[index].extend(detect(row, pose, k, args.sfm/"labels", floor))
    kinds = Counter()
    for track_id, (name, positions) in tracks([merge(frame) for frame in hits]).items():
        if len(positions) < 3:
            continue
        indices = np.array([index for index, point in positions])
        points = np.array([point for index, point in positions])
        # Consistent tracks represent distance better than single-frame masks.
        if np.percentile(np.linalg.norm(np.diff(points, axis=0), axis=1), 80) > 7:
            continue
        smoothed = points.copy()
        smoothed[1:-1] = .2*points[:-2]+.6*points[1:-1]+.2*points[2:]
        heading = None
        kinds[name] += 1
        for i, (index, point) in enumerate(zip(indices, smoothed, strict=True)):
            delta = smoothed[min(i+1,len(points)-1)]-smoothed[max(0,i-1)]
            if np.linalg.norm(delta) > .65:
                heading = float(np.arctan2(delta[1], delta[0]))
            frames[index]["actors"].append([track_id, name, *np.round(point, 2), heading])
    report = {"schema": 1, "source_scene": source["scene"], "frames": frames, "tracks": dict(kinds)}
    (args.output/"surround.json").write_text(json.dumps(report, separators=(",", ":"))+"\n")
    print(f"{len(frames)} RGB timestamps, {sum(len(frame['cameras']) for frame in frames)} registered cameras; tracks {dict(kinds)}")


if __name__ == "__main__":
    main()
