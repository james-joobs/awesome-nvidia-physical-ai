"""Run official Newton material examples and prepare USD scenes for GUI review.

Requires Newton's example dependencies, numpy and usd-core in this interpreter.
The generated USD contains recorded solver states; Isaac Sim displays a replay.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time

import newton
import numpy as np
import warp
from pxr import Gf, Usd, UsdGeom, UsdLux


CASES = {
    "cloth-xpbd": ("cloth_hanging", ["--solver", "xpbd", "--width", "64", "--height", "32"],
                   "newton.examples.cloth.example_cloth_hanging"),
    "cloth-vbd": ("cloth_hanging", ["--solver", "vbd", "--width", "64", "--height", "32"],
                  "newton.examples.cloth.example_cloth_hanging"),
    "cable-twist": ("cable_twist", [], "newton.examples.cable.example_cable_twist"),
}


def inspect_and_frame(path, name):
    stage = Usd.Stage.Open(str(path))
    if not stage or stage.GetEndTimeCode() <= stage.GetStartTimeCode():
        raise RuntimeError(f"No animated USD: {path}")
    low, high = np.full(3, np.inf), np.full(3, -np.inf)
    animated = []
    for prim in stage.Traverse():
        for attribute_name in ("points", "positions"):
            attribute = prim.GetAttribute(attribute_name)
            if not attribute or len(attribute.GetTimeSamples()) < 2:
                continue
            times = attribute.GetTimeSamples()
            samples = [np.asarray(attribute.Get(t), dtype=float) for t in (times[0], times[len(times)//2], times[-1])]
            if not all(array.ndim == 2 and array.shape[1] == 3 and np.isfinite(array).all() for array in samples):
                raise RuntimeError(f"Invalid point data: {prim.GetPath()}")
            nonempty = [array for array in samples if len(array)]
            if not nonempty:
                continue
            low = np.minimum(low, np.concatenate(nonempty).min(axis=0))
            high = np.maximum(high, np.concatenate(nonempty).max(axis=0))
            same_shape = samples[0].shape == samples[-1].shape
            displacement = float(np.max(np.linalg.norm(samples[-1] - samples[0], axis=1))) if same_shape and len(samples[0]) else None
            animated.append({"prim": str(prim.GetPath()), "attribute": attribute_name,
                             "first_shape": list(samples[0].shape), "time_samples": len(times),
                             "max_displacement_m": displacement})
    if not animated or not np.isfinite(low).all():
        raise RuntimeError("No animated point arrays to verify")
    # A separate camera layer leaves the official solver output intact.
    review = Usd.Stage.CreateNew(str(path.parent / f"{name}-review.usda"))
    review.GetRootLayer().subLayerPaths = [path.name]
    review.SetStartTimeCode(stage.GetStartTimeCode())
    review.SetEndTimeCode(stage.GetEndTimeCode())
    review.SetTimeCodesPerSecond(stage.GetTimeCodesPerSecond())
    UsdGeom.SetStageUpAxis(review, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(review, 1.0)
    world = UsdGeom.Xform.Define(review, "/World")
    review.SetDefaultPrim(world.GetPrim())
    center = (low + high)/2
    radius = max(1.0, float(np.linalg.norm(high-low)))
    eye = center + np.array([0.8, -1.25, 0.65])*radius*1.3
    camera = UsdGeom.Camera.Define(review, "/World/FilmCamera")
    look = Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye), Gf.Vec3d(*center), Gf.Vec3d(0,0,1))
    UsdGeom.Xformable(camera).AddTransformOp().Set(look.GetInverse())
    camera.CreateFocalLengthAttr(36)
    camera.CreateHorizontalApertureAttr(36)
    camera.CreateVerticalApertureAttr(20.25)
    camera.CreateClippingRangeAttr(Gf.Vec2f(0.01, radius*100))
    dome = UsdLux.DomeLight.Define(review, "/World/DomeLight")
    dome.CreateIntensityAttr(650)
    sun = UsdLux.DistantLight.Define(review, "/World/Sun")
    sun.CreateIntensityAttr(2000)
    UsdGeom.Xformable(sun).AddRotateXYZOp().Set(Gf.Vec3f(315, 20, 35))
    review.GetRootLayer().Save()
    return {"animated_arrays": animated, "bounds_m": [low.tolist(), high.tolist()],
            "simulated_seconds": (stage.GetEndTimeCode()-stage.GetStartTimeCode()) / stage.GetTimeCodesPerSecond(),
            "review_scene": f"{name}-review.usda"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cases", nargs="+", choices=list(CASES), default=list(CASES))
    parser.add_argument("--frames", type=int, default=240)
    args = parser.parse_args()
    if args.frames < 60:
        parser.error("Use at least 60 frames for a meaningful material experiment")
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"engine": "Newton", "version": newton.__version__, "warp": warp.__version__,
              "recording_mode": "solver-usd-replay", "cases": []}
    plan = []
    for name in args.cases:
        example, parameters, module_name = CASES[name]
        path = args.output.resolve() / f"{name}.usd"
        if path.exists():
            raise FileExistsError(path)
        command = [sys.executable, "-m", "newton.examples", example, *parameters,
                   "--device", "cuda:0", "--viewer", "usd", "--output-path", str(path),
                   "--num-frames", str(args.frames), "--test"]
        source = Path(importlib.import_module(module_name).__file__)
        start = time.monotonic()
        with (args.output / f"{name}.log").open("w") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        row = {"case": name, "command": command, "official_tests_passed": True,
               "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "wall_seconds": round(time.monotonic()-start, 2), **inspect_and_frame(path, name)}
        report["cases"].append(row)
        plan.append([name, f"{name}-review", "FilmCamera", 0, 0.65, 8])
        print(json.dumps(row), flush=True)
    (args.output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "takes.json").write_text(json.dumps(plan, indent=2) + "\n")


if __name__ == "__main__":
    main()
