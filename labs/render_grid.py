"""Make the four-field preview from the included clips (FFmpeg + Pillow, no GPU).

Short clips loop. The labels distinguish planned motion, solver-state replay,
generated pixels and vehicle-trajectory replay. Original recordings stay intact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "site/public/showcase"
LABELS = ["cuRobo · planned paths", "Newton · solver replay",
          "Cosmos3 · generated RGB", "Alpamayo2 · trajectory replay"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key, default in (("curobo", "curobo-replan"), ("newton", "newton-materials"),
                         ("cosmos", "cosmos-camera-action"), ("driving", "alpamayo-trajectory")):
        parser.add_argument("--" + key, type=Path, default=MEDIA / (default + ".mp4"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=20)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--font", type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix(".json").exists():
        parser.error("Choose a new output filename; existing media and metadata are preserved")
    if not 0 < args.seconds <= 60:
        parser.error("--seconds must be between 0 and 60")
    if not shutil.which(args.ffmpeg):
        parser.error("FFmpeg executable not found")
    files = [getattr(args, key).resolve() for key in ("curobo", "newton", "cosmos", "driving")]
    for path in files:
        if not path.is_file():
            parser.error(f"Missing source clip: {path}")
    font_paths = [args.font] if args.font else [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
    font_path = next((path for path in font_paths if path.is_file()), None)
    if font_path is None:
        parser.error("Pass --font /path/to/a/font.ttf")
    font = ImageFont.truetype(str(font_path), 18)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="physical-ai-grid-") as folder:
        labels = []
        for index, text in enumerate(LABELS):
            label = Path(folder) / f"label-{index}.png"
            image = Image.new("RGBA", (640, 42), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            right = draw.textbbox((0, 0), text, font=font)[2]
            draw.rounded_rectangle((7, 5, right + 25, 37), radius=4, fill=(0, 0, 0, 175))
            draw.text((15, 10), text, font=font, fill="white")
            image.save(label)
            labels.append(label)
        command = [args.ffmpeg, "-nostdin", "-v", "error"]
        for path in files:
            command += ["-stream_loop", "-1", "-i", str(path)]
        for path in labels:
            command += ["-i", str(path)]
        filters = [f"[{i}:v]scale=640:360,setsar=1[b{i}]" for i in range(4)]
        filters += [f"[b{i}][{i+4}:v]overlay=0:318[v{i}]" for i in range(4)]
        filters += ["[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]"]
        command += ["-filter_complex", ";".join(filters), "-map", "[v]", "-t", str(args.seconds),
                    "-r", "30", "-c:v", "libx264", "-crf", "25", "-preset", "fast",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-n", str(args.output)]
        subprocess.run(command, check=True)
    report = {"scope": "edited overview of the included experiment recordings", "duration_s": args.seconds,
              "layout": "top-left cuRobo; top-right Newton; bottom-left Cosmos; bottom-right Alpamayo",
              "looping": "short inputs loop; Newton changes examples within its source clip",
              "inputs": [{"file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                         for path in files], "labels": LABELS, "font": str(font_path),
              "output_bytes": args.output.stat().st_size,
              "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
