"""Extend nearby observed road RGB into small gaps beneath the Volvo footprint."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    manifest = args.package/"road.json"
    road = json.loads(manifest.read_text())
    fit = road["scene_fit"]
    if "contact_gap_filled_pixels" in fit:
        return
    path = args.package/road["texture"]
    image = np.array(Image.open(path).convert("RGBA"))
    height, width = image.shape[:2]
    low_x, low_y, high_x, high_y = road["bounds_xy"]
    pixel = ((high_y-low_y)/height, (high_x-low_x)/width)
    poses = np.array([item["pose"] for item in road["scene_fit"]["front_path"]])
    footprint = Image.new("1", (width, height))
    draw = ImageDraw.Draw(footprint)
    corners = np.array([[-1.48, -.98], [1.72, -.98], [1.72, .98], [-1.48, .98]])
    for start, end in zip(poses, poses[1:]):
        length = np.linalg.norm(end[:2, 3]-start[:2, 3])
        steps = max(1, int(np.ceil(length/.08)))
        for fraction in np.linspace(0, 1, steps+1):
            pose = (1-fraction)*start+fraction*end
            forward = pose[:2, 2]/np.linalg.norm(pose[:2, 2])
            left = np.array([-forward[1], forward[0]])
            center = pose[:2, 3]-1.35*forward
            points = center+corners[:, :1]*forward+corners[:, 1:]*left
            uv = np.column_stack(((points[:, 0]-low_x)/pixel[1], (high_y-points[:, 1])/pixel[0]))
            draw.polygon([tuple(point) for point in uv.round().astype(int)], fill=1)
    gaps = image[..., 3] < 141
    distance, nearest = distance_transform_edt(gaps, sampling=pixel, return_indices=True)
    fill = gaps & np.asarray(footprint) & (distance <= .55)
    if not fill.any():
        return
    image[fill, :3] = image[nearest[0][fill], nearest[1][fill], :3]
    image[fill, 3] = 244
    Image.fromarray(image).save(path, lossless=True)
    fit["contact_gap_filled_pixels"] = int(fill.sum())
    with path.open("rb") as stream:
        fit["atlas_asset"]["sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    fit["atlas_asset"]["bytes"] = path.stat().st_size
    manifest.write_text(json.dumps(road, separators=(",", ":"))+"\n")
    print(f"Filled {int(fill.sum())} texture pixels near visible road along the tire path")


if __name__ == "__main__":
    main()
