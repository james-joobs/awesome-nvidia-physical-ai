"""Extract road/sky labels, calibrated video depth and sparse RGB correspondences."""
import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

MASK_MODEL = "facebook/mask2former-swin-tiny-cityscapes-semantic"
MASK_REVISION = "01a04783d1e2981b13cf5aace8cd87774012de27"


def segment(rgb, output):
    from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation

    processor = AutoImageProcessor.from_pretrained(MASK_MODEL, revision=MASK_REVISION)
    model = Mask2FormerForUniversalSegmentation.from_pretrained(
        MASK_MODEL, revision=MASK_REVISION
    ).eval().cuda()
    labels = []
    for image in rgb:
        inputs = processor(images=Image.fromarray(image), return_tensors="pt").to("cuda")
        prediction = model(**inputs)
        semantic = processor.post_process_semantic_segmentation(
            prediction, target_sizes=[image.shape[:2]]
        )[0]
        labels.append(semantic.cpu().numpy().astype(np.uint8))
    # Cityscapes train IDs: road=0, sky=10, people and vehicles=11–18.
    if model.config.id2label[0].lower() != "road" or model.config.id2label[10].lower() != "sky":
        raise ValueError("Unexpected semantic label map")
    np.save(output / "labels.npy", labels)
    return {"model": MASK_MODEL, "revision": MASK_REVISION, "views": len(labels)}


def depths(rgb, intrinsics, output):
    from depth_pro_2 import create_model_and_transforms

    model, transform = create_model_and_transforms("depthpro2-b", device="cuda")
    depth = np.empty(rgb.shape[:3], np.float32)
    for camera in range(6):
        focal = float(np.median(intrinsics[camera::6, 0, 0]))
        images = (transform(image) for image in rgb[camera::6])
        predictions = model.infer_video(images, f_px=focal, window=8, overlap=4)
        indices = list(range(camera, len(rgb), 6))
        for index, prediction in zip(indices, predictions, strict=True):
            depth[index] = prediction["depth"].cpu().numpy()
        print(f"Depth Pro 2 camera {camera + 1}/6", flush=True)
    np.save(output / "depth-pro.npy", depth)
    return {"model": "apple/DepthPro2-B", "views": len(rgb), "video_window": 8, "overlap": 4}


def match(rgb, output):
    from loma import LoMa, LoMaB
    from loma.loma import filter_matches, to_pixel_coords

    model = LoMa(LoMaB()).eval().cuda()
    features = []
    for image in rgb:
        tensor = torch.from_numpy(image.copy()).permute(2, 0, 1)[None].cuda().float() / 255
        features.append(model.detect_and_describe(tensor))
    keypoints = np.stack([
        to_pixel_coords(points[0], h, w).cpu().numpy() for points, _, h, w in features
    ])
    pairs = []
    frames = len(rgb) // 6
    for frame in range(frames):
        for camera in range(6):
            first = 6 * frame + camera
            for delta in (1, 2):
                if frame + delta < frames:
                    pairs.append((first, first + 6 * delta))
            for other in range(camera + 1, 6):
                pairs.append((first, 6 * frame + other))
    rows = []
    for first, second in pairs:
        p1, d1, _, _ = features[first]
        p2, d2, _, _ = features[second]
        scores = model(p1, p2, d1, d2)["scores"]
        m0, _, confidence, _ = filter_matches(scores, 0.15)
        i = torch.where(m0[0] >= 0)[0].cpu().numpy()
        j = m0[0, i].cpu().numpy()
        if len(i) < 16:
            continue
        _, inliers = cv2.findFundamentalMat(
            keypoints[first, i], keypoints[second, j], cv2.USAC_MAGSAC, 1.2, 0.999, 10000
        )
        if inliers is None:
            continue
        keep = inliers.ravel().astype(bool)
        rows.extend(zip(np.repeat(first, keep.sum()), i[keep], np.repeat(second, keep.sum()),
                        j[keep], confidence[0, i].cpu().numpy()[keep], strict=True))
    np.savez_compressed(output / "matches.npz", keypoints=keypoints, links=np.array(rows))
    return {"model": "LoMa-B", "views": len(rgb), "tested_pairs": len(pairs), "inlier_links": len(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["mask", "depth", "match"])
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--calibration", type=Path, help="Refined camera intrinsics for Depth Pro 2")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with np.load(args.geometry) as data:
        rgb = data["observed_rgb"]
        intrinsics = data["intrinsics"]
    if args.calibration:
        with np.load(args.calibration) as calibrated:
            intrinsics = calibrated["intrinsics"]
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    with torch.inference_mode():
        if args.stage == "mask":
            report = segment(rgb, args.output)
        elif args.stage == "depth":
            report = depths(rgb, intrinsics, args.output)
        else:
            report = match(rgb, args.output)
    torch.cuda.synchronize()
    report.update(seconds=round(time.perf_counter() - start, 3),
                  peak_allocated_gib=round(torch.cuda.max_memory_allocated() / 2**30, 3))
    (args.output / f"{args.stage}.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
