"""Build a cuRobo collision-geometry replay from a newly computed motion.npz.

CPU authoring only: requires numpy, usd-core and Pillow. This does not execute
Franka dynamics or a policy, and it does not use a full Franka visual mesh.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdShade, Vt

FPS, END, LEAD, FINISH = 30, 300, 26, 234
COLORS = {
    "robot": (0.64, 0.70, 0.75), "base": (0.10, 0.14, 0.17),
    "baseline": (0.92, 0.49, 0.06), "obstacle": (0.35, 0.65, 0.03),
    "red": (0.82, 0.10, 0.07), "goal": (0.05, 0.42, 0.66),
    "table": (0.89, 0.91, 0.92), "floor": (0.97, 0.98, 0.98),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def material(stage, name, color):
    mat = UsdShade.Material.Define(stage, "/World/Materials/" + name)
    shader = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild("Surface"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.42)
    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return mat


def bind(geometry, mat):
    UsdShade.MaterialBindingAPI.Apply(geometry.GetPrim()).Bind(mat)


def box(stage, path, position, size, mat):
    shape = UsdGeom.Cube.Define(stage, path)
    shape.CreateSizeAttr(1)
    shape.AddTranslateOp().Set(Gf.Vec3d(*map(float, position)))
    shape.AddScaleOp().Set(Gf.Vec3d(*map(float, size)))
    bind(shape, mat)
    return shape


def sphere(stage, path, position, radius, mat):
    shape = UsdGeom.Sphere.Define(stage, path)
    shape.CreateRadiusAttr(float(radius))
    transform = shape.AddTranslateOp()
    transform.Set(Gf.Vec3d(*map(float, position)))
    bind(shape, mat)
    return transform


def curve(stage, path, points, width, mat):
    shape = UsdGeom.BasisCurves.Define(stage, path)
    shape.CreateTypeAttr(UsdGeom.Tokens.linear)
    shape.CreateWrapAttr(UsdGeom.Tokens.nonperiodic)
    shape.CreateCurveVertexCountsAttr([len(points)])
    shape.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(np.asarray(points, dtype=np.float32)))
    shape.CreateWidthsAttr([width])
    shape.SetWidthsInterpolation(UsdGeom.Tokens.constant)
    bind(shape, mat)
    return shape


def label_texture(path, title, subtitle, accent):
    image = Image.new("RGB", (1600, 310), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold_path = font_path.with_name("DejaVuSans-Bold.ttf")
    font = ImageFont.truetype(str(font_path), 44) if font_path.exists() else ImageFont.load_default(size=44)
    bold = ImageFont.truetype(str(bold_path), 76) if bold_path.exists() else ImageFont.load_default(size=76)
    draw.rounded_rectangle((0, 40, 14, 252), radius=7, fill=tuple(int(v * 255) for v in accent))
    draw.text((52, 40), title, font=bold, fill=(23, 31, 37))
    draw.text((54, 151), subtitle, font=font, fill=(79, 90, 99))
    draw.text((54, 220), "cuRobo / Franka collision geometry", font=font, fill=(108, 117, 124))
    image.save(path, optimize=True)


def billboard(stage, path, center, eye, texture):
    # Camera-facing geometry; the label is part of the actual USD scene.
    normal = (eye - center) / np.linalg.norm(eye - center)
    right = np.cross(np.array([0., 0., 1.]), normal)
    right /= np.linalg.norm(right)
    up = np.cross(normal, right)
    corners = [center + x * 0.69 * right + y * 0.134 * up for x, y in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
    mesh = UsdGeom.Mesh.Define(stage, path)
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(np.asarray(corners, dtype=np.float32)))
    mesh.CreateFaceVertexCountsAttr([4])
    mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    mesh.CreateDoubleSidedAttr(True)
    UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex).Set(
        [(0, 0), (1, 0), (1, 1), (0, 1)])
    mat = UsdShade.Material.Define(stage, path + "Material")
    uv = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild("UV"))
    uv.CreateIdAttr("UsdPrimvarReader_float2")
    uv.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
    tex = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild("Texture"))
    tex.CreateIdAttr("UsdUVTexture")
    tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("./" + texture))
    tex.CreateInput("sourceColorSpace", Sdf.ValueTypeNames.Token).Set("sRGB")
    tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), "result")
    surface = UsdShade.Shader.Define(stage, mat.GetPath().AppendChild("Surface"))
    surface.CreateIdAttr("UsdPreviewSurface")
    surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0))
    surface.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")
    mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")
    bind(mesh, mat)


def validate_trace(trace, report):
    for name in ("baseline", "obstacle"):
        for suffix in ("tool", "q", "spheres"):
            data = trace[name + "_" + suffix]
            if not np.isfinite(data).all() or len(data) < 2:
                raise ValueError("Non-finite/incomplete trajectory: " + name + "_" + suffix)
        spheres = trace[name + "_spheres"]
        if spheres.ndim != 3 or spheres.shape[2] != 4:
            raise ValueError("Expected collision sphere array [steps, spheres, xyz+radius]")
        active = spheres[0, :, 3] > 0
        if active.sum() < 10 or not (spheres[:, active, 3] > 0).all():
            raise ValueError("Collision sphere activity changed or is incomplete")
    if not np.allclose(trace["baseline_q"][0], trace["obstacle_q"][0], atol=.001):
        raise ValueError("The two plans do not share a start")
    error = float(np.linalg.norm(trace["baseline_tool"][-1] - trace["obstacle_tool"][-1]))
    if error > .01:
        raise ValueError("The two plans do not share a tool goal")
    if report.get("baseline_tool_enters_new_obstacle") is not True or report.get("replanned_tool_enters_obstacle") is not False:
        raise ValueError("Result does not show a successful obstacle replan")
    center, dims = np.asarray(report["obstacle_center_m"]), np.asarray(report["obstacle_dimensions_m"])
    spheres = trace["obstacle_spheres"]
    active = spheres[0, :, 3] > 0
    outside = np.maximum(np.abs(spheres[:, active, :3] - center) - dims / 2, 0)
    clearance = float((np.linalg.norm(outside, axis=2) - spheres[:, active, 3]).min())
    if clearance < -1e-5:
        raise ValueError("A sampled robot collision sphere intersects the obstacle")
    return {"goal_difference_m": error, "sampled_sphere_min_clearance_m": clearance,
            "active_collision_spheres": int(active.sum())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("scene_directory", type=Path)
    args = parser.parse_args()
    source, output = args.run_directory.resolve(), args.scene_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    scene_path = output / "curobo-replan.usda"
    names = ["curobo-replan.usda", "takes.json", "scene-report.json", "baseline-label.png", "obstacle-label.png"]
    if any((output / name).exists() for name in names):
        raise FileExistsError("Use a new scene directory; scene outputs already exist")
    report = json.loads((source / "result.json").read_text())
    with np.load(source / "motion.npz", allow_pickle=False) as archive:
        trace = {name: archive[name] for name in archive.files}
    checks = validate_trace(trace, report)
    stage = Usd.Stage.CreateNew(str(scene_path))
    stage.SetStartTimeCode(0)
    stage.SetEndTimeCode(END)
    stage.SetTimeCodesPerSecond(FPS)
    stage.SetFramesPerSecond(FPS)
    UsdGeom.SetStageMetersPerUnit(stage, 1.)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    stage.GetRootLayer().customLayerData = {
        "evidence_mode": "collision-geometry-trajectory-replay",
        "description": "Saved cuRobo collision spheres and tool paths; not live physics, a live policy, or a full Franka mesh.",
        "motion_sha256": sha256(source / "motion.npz"), "result_sha256": sha256(source / "result.json"),
    }
    mats = {name: material(stage, name, color) for name, color in COLORS.items()}
    box(stage, "/World/Floor", (0, .15, -.035), (200, 200, .05), mats["floor"])
    eye, target = np.array([1.10, -3.70, 2.95]), np.array([0, .08, 1.17])
    camera = UsdGeom.Camera.Define(stage, "/World/FilmCamera")
    camera.AddTransformOp().Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye), Gf.Vec3d(*target), Gf.Vec3d(0, 0, 1)).GetInverse())
    camera.CreateFocalLengthAttr(42.)
    camera.CreateHorizontalApertureAttr(36.)
    camera.CreateVerticalApertureAttr(20.25)
    camera.CreateClippingRangeAttr(Gf.Vec2f(.01, 1000))
    dome = UsdLux.DomeLight.Define(stage, "/World/Dome")
    dome.CreateIntensityAttr(650)
    dome.CreateColorAttr(Gf.Vec3f(1))
    sun = UsdLux.DistantLight.Define(stage, "/World/Key")
    sun.CreateIntensityAttr(1800)
    sun.CreateAngleAttr(0.8)
    sun.AddRotateXYZOp().Set(Gf.Vec3f(315, 15, 20))

    for name, x, title, subtitle in (
        ("baseline", -.86, "BASELINE", "Before adding the obstacle"),
        ("obstacle", .86, "REPLANNED", "Same goal. New obstacle."),
    ):
        root = "/World/" + name
        offset = np.array([x, 0, .82])
        box(stage, root + "/Table", (x, .10, .78), (1.50, 1.16, .08), mats["table"])
        box(stage, root + "/Accent", (x, -.477, .79), (1.50, .018, .055), mats[name])
        box(stage, root + "/Plinth", (x - .04, 0, .84), (.32, .31, .035), mats["base"])
        for lx in (-.6, .6):
            box(stage, root + ("/LegL" if lx < 0 else "/LegR"), (x + lx, .15, .36), (.065, .8, .72), mats["base"])
        points = trace[name + "_tool"] + offset
        curve(stage, root + "/ToolPath", points, .009, mats[name])
        marker = sphere(stage, root + "/Tool", points[0], .021, mats[name])
        sphere(stage, root + "/Start", points[0], .016, mats["goal"])
        sphere(stage, root + "/Goal", points[-1], .025, mats["goal"])
        # Goal cross makes the shared endpoint visible even when the tool arrives.
        for axis in range(3):
            delta = np.eye(3)[axis] * .045
            curve(stage, root + f"/GoalAxis{axis}", [points[-1] - delta, points[-1] + delta], .004, mats["goal"])
        spheres = trace[name + "_spheres"]
        active = np.flatnonzero(spheres[0, :, 3] > 0)
        instancer = UsdGeom.PointInstancer.Define(stage, root + "/CollisionSpheres")
        prototype = UsdGeom.Sphere.Define(stage, root + "/CollisionSpheres/Prototype")
        prototype.CreateRadiusAttr(1.)
        bind(prototype, mats["robot"])
        instancer.CreatePrototypesRel().SetTargets([prototype.GetPath()])
        instancer.CreateProtoIndicesAttr([0] * len(active))
        instancer.CreateScalesAttr([Gf.Vec3f(float(r)) for r in spheres[0, active, 3]])
        instancer.CreatePositionsAttr(Vt.Vec3fArray.FromNumpy((spheres[0, active, :3] + offset).astype(np.float32)))
        for step, sample in enumerate(spheres):
            frame = LEAD + (FINISH - LEAD) * step / (len(spheres) - 1)
            instancer.GetPositionsAttr().Set(Vt.Vec3fArray.FromNumpy((sample[active, :3] + offset).astype(np.float32)), frame)
            marker.Set(Gf.Vec3d(*map(float, points[step])), frame)
        if name == "obstacle":
            center = np.asarray(report["obstacle_center_m"]) + offset
            dims = np.asarray(report["obstacle_dimensions_m"])
            box(stage, root + "/NewObstacle", center, dims, mats["red"])
            # Thin stand is illustrative support, not part of the planning world.
            height = center[2] - dims[2] / 2 - .82
            box(stage, root + "/DisplayStand", (center[0], center[1], .82 + height / 2), (.009, .009, height), mats["base"])
        texture = name + "-label.png"
        label_texture(output / texture, title, subtitle, COLORS[name])
        billboard(stage, root + "/Label", np.array([x - .02, .04, 1.91]), eye, texture)
    stage.GetRootLayer().Save()
    check_stage = Usd.Stage.Open(str(scene_path))
    if not check_stage.GetPrimAtPath("/World/FilmCamera"):
        raise RuntimeError("Saved scene is missing its recording camera")
    for name in ("baseline", "obstacle"):
        attr = check_stage.GetPrimAtPath("/World/" + name + "/CollisionSpheres").GetAttribute("positions")
        if len(attr.GetTimeSamples()) != len(trace[name + "_spheres"]):
            raise RuntimeError("Saved sphere animation is incomplete")
    (output / "takes.json").write_text(json.dumps([["curobo-replan", "curobo-replan", "FilmCamera", 0, 1, 10.6]], indent=2) + "\n")
    summary = {"scene": scene_path.name, "evidence_mode": "collision-geometry-trajectory-replay",
               "description": "Animated exact-radius active collision spheres and saved tool paths; no full Franka visual mesh or live dynamics.",
               "illustrative_geometry": "Tables, labels, goal markers and thin obstacle stand are presentation geometry, not additional planner collision objects.",
               "input_hashes": {name: sha256(source / name) for name in ("motion.npz", "result.json")},
               "generator_sha256": sha256(Path(__file__)), "camera": "/World/FilmCamera",
               "frames": END, "fps": FPS, "source_waypoints": {name: len(trace[name + "_tool"]) for name in ("baseline", "obstacle")},
               "checks": checks, "validated": True}
    (output / "scene-report.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
