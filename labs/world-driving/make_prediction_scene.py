"""Show saved Alpamayo predictions as an animated USD proxy, without a model or GPU.

This is a replay of predicted poses. No vehicle physics or closed-loop policy
execution is added. Requires numpy and the USD Python bindings (usd-core).
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import struct

import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

parser = argparse.ArgumentParser()
parser.add_argument("--scene", type=Path, required=True)
parser.add_argument("--prediction", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
content = args.prediction.read_bytes()
header_size = struct.unpack("<Q", content[:8])[0]
header = json.loads(content[8:8 + header_size])
numeric = content[8 + header_size:]


def tensor(name):
    spec = header[name]
    assert spec["dtype"] == "F32", (name, spec)
    begin, end = spec["data_offsets"]
    return np.frombuffer(numeric[begin:end], dtype="<f4").reshape(spec["shape"])


xyz = tensor("pred_xyz")[0, 0, 0]
rot = tensor("pred_rot")[0, 0, 0]
assert xyz.shape == (64, 3) and rot.shape == (64, 3, 3)
assert np.isfinite(xyz).all() and np.isfinite(rot).all()
stage = Usd.Stage.Open(str(args.scene))
stage.SetStartTimeCode(0)
stage.SetEndTimeCode(192)
stage.SetTimeCodesPerSecond(30)
stage.SetFramesPerSecond(30)


def material(name, color, emissive=False):
    mat = UsdShade.Material.Define(stage, "/World/Looks/" + name)
    shader = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild("Shader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(.55)
    if emissive:
        shader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return mat


orange = material("PredictedRoute", (1, .36, .015), True)
lime = material("PredictedCar", (.3, .8, .045))
glass = material("PredictedGlass", (.02, .09, .12))
points = [Gf.Vec3f(0, -1.8, .13)] + [Gf.Vec3f(float(x), float(y - 1.8), float(z + .13)) for x, y, z in xyz]
path = UsdGeom.BasisCurves.Define(stage, "/World/PredictedRoute")
path.CreateTypeAttr("linear")
path.CreateCurveVertexCountsAttr([len(points)])
path.CreatePointsAttr(points)
path.CreateWidthsAttr([.15])
path.SetWidthsInterpolation(UsdGeom.Tokens.constant)
UsdShade.MaterialBindingAPI.Apply(path.GetPrim()).Bind(orange)
proxy = UsdGeom.Xform.Define(stage, "/World/PredictedVehicleProxy")
position = proxy.AddTranslateOp()
orientation = proxy.AddOrientOp()
for name, location, scale, look in (("Body", (.3, 0, .65), (4.2, 1.8, .9), lime),
                                    ("Cabin", (-.1, 0, 1.22), (2.0, 1.6, .65), glass)):
    block = UsdGeom.Cube.Define(stage, proxy.GetPath().AppendChild(name))
    block.CreateSizeAttr(1)
    block.AddTranslateOp().Set(Gf.Vec3d(*location))
    block.AddScaleOp().Set(Gf.Vec3d(*scale))
    UsdShade.MaterialBindingAPI.Apply(block.GetPrim()).Bind(look)
position.Set(Gf.Vec3d(0, -1.8, 0), 0)
orientation.Set(Gf.Quatf(1), 0)
rows = []
for index, (point, rotation) in enumerate(zip(xyz, rot, strict=True)):
    seconds = (index + 1) / 10
    yaw = math.atan2(float(rotation[1, 0]), float(rotation[0, 0]))
    position.Set(Gf.Vec3d(float(point[0]), float(point[1] - 1.8), float(point[2])), seconds * 30)
    orientation.Set(Gf.Quatf(math.cos(yaw / 2), Gf.Vec3f(0, 0, math.sin(yaw / 2))), seconds * 30)
    rows.append([seconds, *map(float, point), yaw])
center_x = float((xyz[:, 0].min() + xyz[:, 0].max()) / 2)
center_y = float((xyz[:, 1].min() + xyz[:, 1].max()) / 2) - 1.8
span = max(float(np.ptp(xyz[:, 0])), float(np.ptp(xyz[:, 1])), 20)
target = Gf.Vec3d(center_x, center_y, .6)
eye = target + Gf.Vec3d(-span * .8, -span * .9, span)
camera = UsdGeom.Camera.Define(stage, "/World/FilmCamera")
camera.CreateFocalLengthAttr(24)
camera.CreateHorizontalApertureAttr(20.955)
camera.CreateClippingRangeAttr(Gf.Vec2f(.1, 300))
camera.AddTransformOp().Set(Gf.Matrix4d(1).SetLookAt(eye, target, Gf.Vec3d(0, 0, 1)).GetInverse())
stage.Export(str(args.output / "alpamayo-trajectory.usda"))
(args.output / "takes.json").write_text(json.dumps([
    ["alpamayo-trajectory", "alpamayo-trajectory", "FilmCamera", 0.0, 1.0, 7.5]
], indent=2) + "\n")
with (args.output / "prediction.csv").open("w") as stream:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["time_s", "ego_x_m", "ego_y_m", "ego_z_m", "body_yaw_rad"])
    writer.writerows(rows)
metadata = {
    "mode": "model-trajectory-replay; no closed-loop driving or dynamics",
    "prediction_sha256": hashlib.sha256(content).hexdigest(),
    "points": 64,
    "time_step_s": .1,
    "ego_origin_in_usd_m": [0, -1.8, 0],
    "proxy": "Cosmetic car dimensions; transforms replay model positions and yaw-only body rotations",
    "first_predicted_xyz_m": xyz[0].tolist(),
    "last_predicted_xyz_m": xyz[-1].tolist(),
    "scene": "alpamayo-trajectory.usda",
}
(args.output / "prediction-scene.json").write_text(json.dumps(metadata, indent=2) + "\n")
print(json.dumps(metadata), flush=True)
