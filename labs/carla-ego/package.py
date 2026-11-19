"""Make labeled, lightweight web videos from the four original CARLA sensor takes."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CASES=[("city-clear","Town10HD / clear city"),("junction-rain","Town03 / heavy rain"),
       ("suburb-sunset","Town02 / wet sunset"),("highway-fog","Town04 / fog")]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--ffmpeg",default="ffmpeg")
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    font_path=next(Path(p) for p in ["/System/Library/Fonts/Supplemental/Arial.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if Path(p).exists())
    font=ImageFont.truetype(str(font_path),18)
    reports=[]
    for name,label in CASES:
        overlay=Image.new("RGBA",(768,432))
        draw=ImageDraw.Draw(overlay)
        draw.rectangle((0,0,768,34),fill=(0,0,0,180))
        draw.text((12,7),f"CARLA 0.9.16  |  Ego RGB  |  {label}",font=font,fill="white")
        png=args.output/f"carla-{name}-label.png";overlay.save(png)
        target=args.output/f"carla-{name}.mp4"
        subprocess.run([args.ffmpeg,"-hide_banner","-loglevel","error","-y","-i",str(args.input/name/"ego.mp4"),"-i",str(png),
            "-filter_complex","[0:v]scale=768:432[v];[v][1:v]overlay=0:0", "-an","-c:v","libx264","-crf","26","-pix_fmt","yuv420p","-movflags","+faststart",str(target)],check=True)
        subprocess.run([args.ffmpeg,"-hide_banner","-loglevel","error","-y","-ss","4","-i",str(target),"-frames:v","1",str(target.with_suffix(".jpg"))],check=True)
        report=json.loads((args.input/name/"result.json").read_text())
        report["published"]={"file":target.name,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"resolution":[768,432],"edit":"20 fps / original speed; label overlay; resize and H.264 CRF26"}
        reports.append(report)
        png.unlink()
    inputs=[]
    for name,_ in CASES:
        inputs.extend(["-i",str(args.output/f"carla-{name}.mp4")])
    grid=args.output/"carla-ego.mp4"
    filters=";".join(f"[{i}:v]scale=640:360[v{i}]" for i in range(4))+";[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|640_0|0_360|640_360[out]"
    subprocess.run([args.ffmpeg,"-hide_banner","-loglevel","error","-y",*inputs,"-filter_complex",filters,"-map","[out]","-an","-c:v","libx264","-crf","25","-pix_fmt","yuv420p","-movflags","+faststart",str(grid)],check=True)
    subprocess.run([args.ffmpeg,"-hide_banner","-loglevel","error","-y","-ss","4","-i",str(grid),"-frames:v","1",str(grid.with_suffix(".jpg"))],check=True)
    (args.output/"carla-recorded.json").write_text(json.dumps({"date":"2026-11-20","server_version":"0.9.16","seed":42,
        "controller":"Traffic Manager; rule-based closed-loop simulation, not a learned driving policy",
        "grid_order":[c[0] for c in CASES],"cases":reports,
        "grid":{"file":grid.name,"sha256":hashlib.sha256(grid.read_bytes()).hexdigest(),"frames":320,"fps":20,"resolution":[1280,720]}},indent=2)+"\n")


if __name__=="__main__":
    main()
