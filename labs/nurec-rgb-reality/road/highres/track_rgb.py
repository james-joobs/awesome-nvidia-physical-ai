"""Detect and associate real traffic independently in each KITScenes RGB stream."""
import argparse
import json
from collections import Counter
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from scipy.optimize import linear_sum_assignment
from torchvision.ops import batched_nms
from transformers import AutoImageProcessor, AutoModelForObjectDetection

MODEL = "PekingU/rtdetr_r50vd"
REVISION = "df939e661d8c52e80608d1ec566561aabd25a4e7"
CLASSES = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "transit", 6: "transit", 7: "truck"}
CAMERAS = ("front", "front_left", "front_right", "rear", "rear_left", "rear_right")


def crop_signature(hsv, box):
    x0, y0, x1, y1 = (box * np.tile(hsv.shape[1::-1], 2)).astype(int)
    height, width = y1-y0, x1-x0
    crop = hsv[y0+height//8:y1-height//8, x0+width//8:x1-width//8]
    hist = cv2.calcHist([crop], [0, 1], None, [12, 6], [0, 180, 0, 256]).ravel()
    luminance = cv2.calcHist([crop], [2], None, [10], [0, 256]).ravel()
    return np.sqrt(np.r_[.65*hist/hist.sum(), .35*luminance/luminance.sum()])


@torch.inference_mode()
def detect(images, processor, model, device):
    tensors = processor(images=images, return_tensors="pt").to(device)
    output = model(**tensors)
    sizes = torch.tensor([(im.height, im.width) for im in images], device=device)
    for image, result in zip(images, processor.post_process_object_detection(
            output, threshold=.24, target_sizes=sizes), strict=True):
        boxes, scores, labels = [result[key].cpu() for key in ("boxes", "scores", "labels")]
        eligible = [i for i, label in enumerate(labels.tolist()) if label in CLASSES]
        boxes, scores, labels = boxes[eligible], scores[eligible], labels[eligible]
        # RT-DETR can report its bus and train classes for the same tram.
        groups = torch.where(labels == 6, 5, labels)
        keep = batched_nms(boxes, scores, groups, .6)
        scale = [image.width, image.height]*2
        hsv = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2HSV)
        frame = []
        for i in keep.tolist():
            box = np.clip(boxes[i].numpy()/scale, 0, 1)
            w, h = box[2:]-box[:2]
            if w*image.width < 12 or h*image.height < 14:
                continue
            # The recording vehicle can occupy the extreme bottom of the ring images.
            if box[1] > .79 and box[3] > .98:
                continue
            frame.append((CLASSES[int(labels[i])], float(scores[i]), box, crop_signature(hsv, box)))
        yield frame


@dataclass
class Track:
    id: int
    category: str
    box: np.ndarray
    signature: np.ndarray
    velocity: np.ndarray
    last: int


def center(box):
    return (box[:2]+box[2:])/2


def match_cost(track, detection, now):
    category, _, box, signature = detection
    if category != track.category:
        return 1e3
    gap = now-track.last
    displacement = np.clip(track.velocity*gap, -.14*gap, .14*gap)
    predicted = track.box+np.tile(displacement, 2)
    size = np.maximum(predicted[2:]-predicted[:2], box[2:]-box[:2])
    scaled = np.linalg.norm((center(box)-center(predicted))/(.045+size*.5+.035*gap))
    appearance = np.linalg.norm(track.signature-signature)/np.sqrt(2)
    scale_change = np.abs(np.log((box[2:]-box[:2])/(track.box[2:]-track.box[:2]))).mean()
    if scaled > 1.65 or appearance > .65 or scale_change > .95:
        return 1e3
    return .54*scaled+.50*appearance+.20*scale_change+.10*(gap-1)


def follow(detections, ids):
    active = {}
    published = []
    counts = Counter()
    for index, objects in enumerate(detections):
        active = {key: value for key, value in active.items() if index-value.last <= 2}
        frame = []
        assigned = set()
        # Strong detections start tracks. Weaker detections only extend an existing track.
        for strong in (True, False):
            candidates = [j for j, observation in enumerate(objects) if (observation[1] >= .50) == strong]
            options = [track for track in active.values() if track.id not in assigned]
            pairs = {}
            if options and candidates:
                cost = np.array([[match_cost(track, objects[j], index) for j in candidates]
                                 for track in options])
                rows, cols = linear_sum_assignment(cost)
                pairs = {candidates[j]: options[i] for i, j in zip(rows, cols, strict=True)
                         if cost[i, j] < (1.02 if strong else .68)}
            for j in candidates:
                category, score, box, signature = objects[j]
                track = pairs.get(j)
                if track is None:
                    if not strong:
                        continue
                    track = Track(next(ids), category, box, signature, np.zeros(2), index)
                else:
                    velocity = (center(box)-center(track.box))/(index-track.last)
                    track.velocity = .3*track.velocity+.7*velocity
                    track.signature = .45*track.signature+.55*signature
                    track.box = box
                    track.last = index
                assigned.add(track.id)
                active[track.id] = track
                counts[track.id] += 1
                frame.append([track.id, category, np.round(box, 5).tolist(), round(score, 3)])
        published.append(frame)
    return [[row for row in frame if counts[row[0]] >= 2] for frame in published]


def load_image(path):
    with Image.open(path) as image:
        return image.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packages", type=Path, nargs="+", help="Directories with surround.json and RGB frames")
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    processor = AutoImageProcessor.from_pretrained(MODEL, revision=REVISION)
    model = AutoModelForObjectDetection.from_pretrained(MODEL, revision=REVISION).eval().to(args.device)
    for package in args.packages:
        frames = json.loads((package/"surround.json").read_text())["frames"]
        ids = iter(range(1, 1000000))
        result = {name: [] for name in CAMERAS}
        for camera in CAMERAS:
            files = iter([package/frame["rgb"][camera] for frame in frames])
            predictions = []
            while batch := list(islice(files, 8)):
                predictions.extend(detect([load_image(path) for path in batch], processor, model, args.device))
            result[camera] = follow(predictions, ids)
        tracks = {item[0]: item[1] for series in result.values() for frame in series for item in frame}
        document = {"schema": 1, "detector": MODEL, "revision": REVISION,
                    "times": [frame["time"] for frame in frames], "cameras": result}
        (package/"tracks.json").write_text(json.dumps(document, separators=(",", ":"))+"\n")
        print(f"{len(frames)} times × 6 cameras: {len(tracks)} tracks, {dict(Counter(tracks.values()))}", flush=True)


if __name__ == "__main__":
    main()
