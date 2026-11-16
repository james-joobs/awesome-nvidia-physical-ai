"""Generate and record actual Replicator outputs from the Isaac Sim GUI."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import traceback

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("scene", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--record-window", type=Path, metavar="FFMPEG",
                    help="Optional Linux X11 recording using this FFmpeg executable.")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.enable_cameras = True
args.output.mkdir(parents=True, exist_ok=True)
app = AppLauncher(args).app

import carb
import numpy as np
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from PIL import Image
from pxr import Gf, UsdGeom, UsdLux, UsdSemantics

WIDTH, HEIGHT = 960, 540


def update_for(seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.update()


def screen_recorder(log):
    for line in subprocess.check_output(["xwininfo", "-root", "-tree"], text=True).splitlines():
        if '"Isaac Lab ' in line and "mutter-x11-frames" not in line:
            identifier = str(int(line.split()[0], 16))
            break
    else:
        raise RuntimeError("Isaac Sim window not found")
    return subprocess.Popen([
        str(args.record_window), "-hide_banner", "-loglevel", "warning", "-y",
        "-f", "x11grab", "-draw_mouse", "0", "-framerate", "30",
        "-window_id", identifier, "-i", f"{os.environ['DISPLAY']}.0",
        "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.output / "replicator-gui.mp4"),
    ], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)


def capture_dataset(stage, directory):
    annotator_names = ("rgb", "distance_to_image_plane", "semantic_segmentation")
    sensor = "/World/SensorCamera"
    viewport = get_active_viewport()
    viewport.camera_path = "/World/FilmCamera"
    stage.SetEndTimeCode(900)
    for path, category in (("/World/Target", "target"), ("/World/Distractor", "distractor"),
                           ("/World/Occluder", "occluder"), ("/World/Workbench/Top", "workbench")):
        UsdSemantics.LabelsAPI.Apply(stage.GetPrimAtPath(path), "class").CreateLabelsAttr([category])
    assert stage.GetRootLayer().Export(str(args.output / "replicator-workbench.usda"))
    target = UsdGeom.Xformable(stage.GetPrimAtPath("/World/Target")).GetOrderedXformOps()[0]
    shield = UsdGeom.Xformable(stage.GetPrimAtPath("/World/Occluder")).GetOrderedXformOps()[0]
    lens = UsdGeom.Xformable(stage.GetPrimAtPath(sensor)).GetOrderedXformOps()[0]
    key = UsdLux.RectLight.Get(stage, "/World/Lighting/Key").GetIntensityAttr()
    product = rep.create.render_product(sensor, (WIDTH, HEIGHT))
    options = {"semantic_segmentation": {"colorize": False}}
    annotators = {name: rep.AnnotatorRegistry.get_annotator(name, init_params=options[name])
                  if name in options else rep.AnnotatorRegistry.get_annotator(name) for name in annotator_names}
    for annotator in annotators.values():
        annotator.attach([product])
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    timeline.commit()
    for _ in range(12):
        update_for(.50)
        live_rgb = np.asarray(annotators["rgb"].get_data())
        if live_rgb.shape[:2] == (HEIGHT, WIDTH) and live_rgb[:, :, :3].mean() > 5:
            break
    else:
        raise RuntimeError("Replicator RGB render product did not initialize")

    shots = []
    hashes = set()
    with (args.output / "recorder.log").open("w") as log:
        recorder = screen_recorder(log) if args.record_window else None
        begin = time.monotonic()
        try:
            update_for(1.2)
            for i in range(12):
                x = (-.24, -.09, .08, .25)[i % 4]
                energy = (950, 1550, 2300)[i // 4]
                occluded = i % 4 == 3
                target.Set(Gf.Vec3d(x, -.025, .87))
                shield.Set(Gf.Vec3d(x+.10 if occluded else .43, -.113 if occluded else .12, .935))
                key.Set(energy)
                eye = Gf.Vec3d(1.10 + (i//4)*.13, -1.67, 1.60 + (i//4)*.07)
                lens.Set(Gf.Matrix4d(1).SetLookAt(eye, Gf.Vec3d(0,0,.84), Gf.Vec3d(0,0,1)).GetInverse())
                if i == 6:
                    viewport.camera_path = sensor
                update_for(.72)
                rgb = np.asarray(annotators["rgb"].get_data(), dtype=np.uint8)
                depth = np.asarray(annotators["distance_to_image_plane"].get_data(), dtype=np.float32).squeeze()
                segmentation = annotators["semantic_segmentation"].get_data()
                ids = np.asarray(segmentation["data"], dtype=np.uint32).squeeze()
                labels = segmentation["info"]["idToLabels"]
                if isinstance(labels, str):
                    labels = json.loads(labels)
                target_ids = [int(v) for v,label in labels.items() if (
                    label.get("class") if isinstance(label, dict) else label
                ) == "target"]
                assert rgb.shape[:2] == depth.shape == ids.shape == (HEIGHT, WIDTH)
                digest = hashlib.sha256(rgb[:, :, :3].tobytes()).hexdigest()
                assert digest not in hashes, (i, "duplicate RGB buffer")
                hashes.add(digest)
                mask = np.isin(ids, target_ids)
                if not occluded:
                    assert mask.sum() >= 100, (i, labels)
                assert not np.isnan(depth[mask]).any() and np.isfinite(depth[mask]).all()
                frame = directory / f"{i:02d}"
                frame.mkdir()
                Image.fromarray(rgb[:, :, :3]).save(frame / "rgb.png")
                np.save(frame / "depth_m.npy", depth)
                np.save(frame / "semantic_ids.npy", ids)
                (frame / "semantic_labels.json").write_text(json.dumps(labels, indent=2) + "\n")
                yy, xx = np.nonzero(mask)
                bbox = None if len(xx) == 0 else [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())]
                info = {"frame": i, "target_x_m": x, "candidate_occluded": occluded, "key_light_intensity": energy,
                        "target_pixels": int(mask.sum()), "target_bbox_xyxy": bbox,
                        "target_median_depth_m": float(np.median(depth[mask])) if mask.any() else None,
                        "rgb_sha256": digest, "gui_wall_s": time.monotonic() - begin}
                shots.append(info)
                print(f"REPLICATOR_SAMPLE {i:02d} | RGB/DEPTH/IDS | {info['target_pixels']} target pixels", flush=True)
                update_for(.37)
            update_for(2)
        finally:
            if recorder:
                recorder.send_signal(signal.SIGINT)
                recorder.wait(timeout=14)
            for annotator in annotators.values():
                annotator.detach([product])
            timeline.stop()
    assert len(shots) == 12
    (args.output / "result.json").write_text(json.dumps({
        "resolution_px": [WIDTH, HEIGHT], "channels": list(annotators), "frames": shots,
    }, indent=2) + "\n")


try:
    settings = carb.settings.get_settings()
    settings.set_bool("/omni/replicator/captureOnPlay", True)
    settings.set_bool("/rtx/hydra/readTransformsFromFabricInRenderDelegate", False)
    settings.set_bool("/persistent/app/viewport/Viewport/Viewport0/scene/cameras/visible", False)
    context = omni.usd.get_context()
    assert context.open_stage(str(args.scene.resolve()))
    update_for(1.5)
    stage = context.get_stage()
    assert stage and stage.GetPrimAtPath("/World/SensorCamera")
    frames = args.output / "frames"
    frames.mkdir()
    capture_dataset(stage, frames)
except Exception:
    (args.output / "capture-failed").touch()
    traceback.print_exc()
    raise
finally:
    app.close()
