"""Preview the real RGB, depth, and semantic ID arrays captured by Replicator."""

import argparse
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PALETTE = {"target": (125, 222, 133), "distractor": (74, 133, 204),
           "occluder": (234, 133, 97), "workbench": (179, 160, 112)}


def font(size):
    location = Path("/System/Library/Fonts/Avenir Next.ttc")
    return ImageFont.truetype(str(location) if location.exists() else "DejaVuSans.ttf", size)


def panels(frame, row):
    rgb = Image.open(frame / "rgb.png").convert("RGB")
    depth = np.load(frame / "depth_m.npy", allow_pickle=False)
    sid = np.load(frame / "semantic_ids.npy", allow_pickle=False)
    labels = json.loads((frame / "semantic_labels.json").read_text())
    assert depth.shape == sid.shape == (540, 960)
    shade = np.zeros((*depth.shape, 3), np.uint8)
    finite = np.isfinite(depth)
    ranges = [1.2, 1.9, 2.6, 3.4]
    gradient = np.array([(247, 224, 132), (98, 188, 161), (39, 102, 141), (13, 27, 48)])
    shade[finite] = np.stack([np.interp(depth[finite], ranges, gradient[:, k]) for k in range(3)], axis=1).astype(np.uint8)
    semantic = np.full((*sid.shape, 3), (19, 28, 35), np.uint8)
    for serial, label in labels.items():
        category = label.get("class") if isinstance(label, dict) else label
        semantic[sid == int(serial)] = PALETTE.get(category, (41, 52, 58))
    if row["target_bbox_xyxy"] is not None:
        drawing = ImageDraw.Draw(rgb)
        drawing.rectangle(tuple(row["target_bbox_xyxy"]), outline=(138, 241, 151), width=3)
    return rgb, Image.fromarray(shade), Image.fromarray(semantic)


def preview(frame, row, path):
    directions = ["RGB + box from semantic pixels", "Camera-plane depth [1.2–3.4 m]", "Semantic mask"]
    values = panels(frame, row)
    canvas = Image.new("RGB", (1440, 372), (18, 23, 27))
    draw = ImageDraw.Draw(canvas)
    for i, (image, text) in enumerate(zip(values, directions, strict=True)):
        x = 12 + i*480
        draw.text((x, 11), text, font=font(19), fill=(229, 239, 236))
        canvas.paste(image.resize((456, 256), Image.Resampling.LANCZOS), (x, 43))
    explanation = f"FRAME {row['frame']:02d}     •     CUBE PIXELS {row['target_pixels']:,}"
    draw.text((12, 321), explanation, font=font(19), fill=(229, 239, 236))
    draw.text((974, 322), "Target   •   Distractor   •   Occluder", font=font(17), fill=(153, 205, 167))
    canvas.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args()
    data = json.loads((args.dataset / "result.json").read_text())
    assert len(data["frames"]) == 12
    with TemporaryDirectory(prefix="replicator-preview-") as temporary:
        root = Path(temporary)
        for row in data["frames"]:
            i = row["frame"]
            preview(args.dataset / "frames" / f"{i:02d}", row, root / f"{i:02d}.png")
        (args.dataset / "replicator-sample.png").write_bytes((root / "03.png").read_bytes())
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "5/3",
            "-i", str(root / "%02d.png"), "-vf", "fps=30", "-c:v", "libx264",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.dataset / "replicator-samples.mp4"),
        ], check=True)
    with ZipFile(args.dataset / "replicator-dataset.zip", "w", compression=ZIP_DEFLATED) as archive:
        archive.write(args.dataset / "result.json", "result.json")
        for file in sorted((args.dataset / "frames").rglob("*")):
            if file.is_file():
                archive.write(file, str(file.relative_to(args.dataset)))


if __name__ == "__main__":
    main()
