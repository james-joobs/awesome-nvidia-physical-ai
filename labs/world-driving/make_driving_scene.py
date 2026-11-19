"""Render our own six-camera, 22-frame input in Isaac Sim; no driving dataset needed."""

import argparse
import hashlib
import json
from importlib.metadata import version
import math
import os
from pathlib import Path
import signal
import subprocess

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--record-window", type=Path, help="FFmpeg executable for native Isaac Sim GUI recording")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.enable_cameras = True
launcher = AppLauncher(args)
app = launcher.app

import numpy as np
from PIL import Image
import omni.replicator.core as rep
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from pxr import Gf, Sdf, UsdGeom, UsdLux, UsdShade

args.output.mkdir(parents=True, exist_ok=True)
omni.usd.get_context().new_stage()
stage = omni.usd.get_context().get_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
world = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(world.GetPrim())


def material(name, rgb):
    mat = UsdShade.Material.Define(stage, "/World/Looks/" + name)
    shader = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild("Shader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*rgb))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(.7)
    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return mat


def block(name, center, size, mat):
    shape = UsdGeom.Cube.Define(stage, "/World/" + name)
    shape.CreateSizeAttr(1)
    shape.AddTranslateOp().Set(Gf.Vec3d(*center))
    shape.AddScaleOp().Set(Gf.Vec3d(*size))
    UsdShade.MaterialBindingAPI.Apply(shape.GetPrim()).Bind(mat)
    return shape


asphalt = material("Asphalt", (.12, .14, .16))
grass = material("Grass", (.13, .24, .13))
white = material("White", (.9, .91, .88))
yellow = material("Yellow", (.96, .7, .05))
red = material("RedCar", (.62, .045, .035))
blue = material("BlueCar", (.02, .18, .4))
glass = material("Glass", (.05, .12, .16))
concrete = material("Concrete", (.42, .45, .43))
block("Ground", (20, 0, -.12), (160, 160, .2), grass)
block("MainRoad", (20, 0, .005), (150, 8, .05), asphalt)
block("CrossRoad", (28, 0, .02), (8, 100, .05), asphalt)
for index, x in enumerate(range(-45, 96, 6)):
    if 22 < x < 34:
        continue
    block(f"CenterLine{index}", (x, 0, .04), (3, .12, .015), yellow)
for index, y in enumerate((-3.65, 3.65)):
    for side, x in enumerate((-12, 65)):
        block(f"Edge{index}_{side}", (x, y, .04), (68, .1, .015), white)
for index, y in enumerate(np.arange(-3.1, 3.2, .75)):
    block(f"Crosswalk{index}", (22.8, float(y), .06), (.8, .42, .015), white)
for index, (x, y, h) in enumerate(((42, -15, 12), (56, -14, 8), (40, 17, 10), (-18, 16, 6), (-25, -14, 7))):
    block(f"Building{index}", (x, y, h / 2), (9, 9, h), concrete)
for index, (x, y, body) in enumerate(((17, 2.05, blue), (28, -12, red))):
    block(f"Car{index}Body", (x, y, .65), (4.2, 1.8, .9), body)
    block(f"Car{index}Cabin", (x - .2, y, 1.2), (2, 1.6, .7), glass)
light = UsdLux.DomeLight.Define(stage, "/World/Sky")
light.CreateIntensityAttr(1400)
sun = UsdLux.DistantLight.Define(stage, "/World/Sun")
sun.CreateIntensityAttr(2600)
sun.AddRotateXYZOp().Set(Gf.Vec3f(315, 15, 20))

width, height = 640, 360
camera = UsdGeom.Camera.Define(stage, "/World/Camera")
camera.CreateHorizontalApertureAttr(20.955)
camera.CreateClippingRangeAttr(Gf.Vec2f(.1, 250))
camera_op = camera.AddTransformOp()
product = rep.create.render_product(str(camera.GetPath()), (width, height))
annotator = rep.AnnotatorRegistry.get_annotator("rgb")
annotator.attach([product])
get_active_viewport().camera_path = str(camera.GetPath())
profiles = {0: (55, (-1, -.1, 0), 12), 1: (0, (-2, -1, -.5, -.1, 0), 14),
            2: (-55, (-1, -.1, 0), 12), 3: (145, (-1, -.1, 0), 12),
            5: (-145, (-1, -.1, 0), 12), 6: (0, (-2, -1, -.5, -.1, 0), 30)}
shots = []
recorder = None
record_log = None
if args.record_window:
    camera_op.Set(Gf.Matrix4d(1).SetLookAt(Gf.Vec3d(0, -1.8, 1.6), Gf.Vec3d(30, -1.8, 1.4), Gf.Vec3d(0, 0, 1)).GetInverse())
    for _ in range(35):
        app.update()
    windows = subprocess.check_output(["xwininfo", "-root", "-tree"], text=True)
    rows = [row for row in windows.splitlines() if '"Isaac Lab ' in row and "mutter-x11-frames" not in row]
    if not rows:
        raise RuntimeError("Native Isaac Sim window was not found; use --viz kit")
    identifier = str(int(rows[0].split()[0], 16))
    record_log = (args.output / "record-window.log").open("w")
    recorder = subprocess.Popen([
        str(args.record_window), "-nostdin", "-hide_banner", "-loglevel", "warning", "-y",
        "-f", "x11grab", "-draw_mouse", "0", "-framerate", "24", "-window_id", identifier,
        "-i", f"{os.environ['DISPLAY']}.0", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.output / "six-camera-isaac-gui.mp4"),
    ], stdout=record_log, stderr=subprocess.STDOUT)
for camera_id, (degrees, times, focal) in profiles.items():
    for offset in times:
        eye = Gf.Vec3d(offset * 5, -1.8, 1.6)
        yaw = math.radians(degrees)
        target = eye + Gf.Vec3d(math.cos(yaw) * 30, math.sin(yaw) * 30, -.2)
        camera_op.Set(Gf.Matrix4d(1).SetLookAt(eye, target, Gf.Vec3d(0, 0, 1)).GetInverse())
        camera.GetFocalLengthAttr().Set(focal)
        for _ in range(14):
            app.update()
        rgb = np.asarray(annotator.get_data())[:, :, :3].copy()
        assert rgb.shape == (height, width, 3) and rgb.mean() > 3, (camera_id, offset, rgb.shape)
        name = f"camera-{camera_id}-t{round((offset + 2) * 1000000):07d}.png"
        Image.fromarray(rgb).save(args.output / name)
        shots.append({"camera_id": camera_id, "timestamp_us": round((offset + 2) * 1000000),
                      "relative_time_s": offset, "image": name,
                      "sha256": hashlib.sha256((args.output / name).read_bytes()).hexdigest()})
        print(f"RENDER camera={camera_id} t={offset:+.1f}s file={name}", flush=True)
stage.GetRootLayer().Export(str(args.output / "synthetic-intersection.usda"))
(args.output / "input.json").write_text(json.dumps({
    "kind": "self-authored synthetic interface smoke; not a driving benchmark",
    "isaac_sim_version": version("isaacsim"),
    "isaac_lab_version": version("isaaclab"),
    "coordinate_frame": "ego x forward, y left, z up; ego reference at query time",
    "width": width, "height": height, "ego_speed_m_s": 5, "shots": shots,
    "history_times_s": [round(-1.9 + .1 * i, 3) for i in range(20)],
    "history_xyz_m": [[round((-1.9 + .1 * i) * 5, 3), 0, 0] for i in range(20)],
}, indent=2) + "\n")
annotator.detach([product])
if recorder:
    recorder.send_signal(signal.SIGINT)
    recorder.wait(timeout=20)
    record_log.close()
app.close()
