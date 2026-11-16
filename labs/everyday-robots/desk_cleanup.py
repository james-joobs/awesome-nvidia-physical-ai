"""Compare two cleanup objectives with Isaac Sim and record the PhysX poses."""

import argparse
import json
from pathlib import Path

from isaacsim import SimulationApp

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
output = parser.parse_args().output.resolve()
output.mkdir(parents=True, exist_ok=True)
app = SimulationApp({"headless": True, "fast_shutdown": True})

import carb
import numpy as np
from omni.physx import get_physx_interface, get_physx_simulation_interface
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, UsdShade, UsdUtils


def material(stage, name, color, friction=0.24):
    result = UsdShade.Material.Define(stage, f"/World/Looks/{name}")
    shader = UsdShade.Shader.Define(stage, result.GetPath().AppendChild("Shader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(.45)
    result.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    physics = UsdPhysics.MaterialAPI.Apply(result.GetPrim())
    physics.CreateStaticFrictionAttr(friction)
    physics.CreateDynamicFrictionAttr(friction)
    physics.CreateRestitutionAttr(0)
    return result


def cube(stage, path, location, size, material, collision=False):
    shape = UsdGeom.Cube.Define(stage, path)
    shape.CreateSizeAttr(1)
    shape.AddTranslateOp().Set(Gf.Vec3d(*location))
    shape.AddScaleOp().Set(Gf.Vec3d(*size))
    binding = UsdShade.MaterialBindingAPI.Apply(shape.GetPrim())
    binding.Bind(material)
    if collision:
        UsdPhysics.CollisionAPI.Apply(shape.GetPrim())
        binding.Bind(material, materialPurpose="physics")
    return shape


def main():
    carb.settings.get_settings().set_bool("/physics/updateToUsd", True)
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())
    physics = UsdPhysics.Scene.Define(stage, "/World/Physics")
    physics.CreateGravityDirectionAttr(Gf.Vec3f(0, 0, -1))
    physics.CreateGravityMagnitudeAttr(9.81)
    table_contact = material(stage, "DeskContact", (.48, .31, .19))
    colors = {"snack": material(stage, "Snack", (.93, .22, .045)), "mouse": material(stage, "Mouse", (.08, .17, .30)),
              "cup": material(stage, "Cup", (.66, .91, .92)), "bin": material(stage, "Bin", (.20, .52, .26), .45),
              "floor": material(stage, "Floor", (.1, .12, .14)), "white": material(stage, "White", (.94, .92, .80))}
    cube(stage, "/World/Floor", (0, 0, -.04), (16, 16, .08), colors["floor"], collision=True)
    items = {"snack": (-.36, (.11, .14, .04)), "cup": (0, (.09, .09, .13)), "mouse": (.36, (.10, .16, .05))}
    scenarios = {}
    for name, center in (("ClearEverything", -.82), ("SortTrashOnly", .82)):
        prefix = f"/World/{name}"
        bench = UsdGeom.Xform.Define(stage, prefix + "/Desk")
        bench.GetPrim().GetReferences().AddReference(str(Path(__file__).with_name("workbench-asset.usda").resolve()))
        bench.AddTranslateOp().Set(Gf.Vec3d(center, 0, 0))
        tabletop = stage.GetPrimAtPath(prefix + "/Desk/Workbench/Tabletop")
        assert tabletop.IsValid()
        UsdShade.MaterialBindingAPI.Apply(tabletop).Bind(table_contact, materialPurpose="physics")
        cube(stage, prefix + "/BinFloor", (center, .79, .42), (1.22, .74, .06), colors["bin"], collision=True)
        for index, x in enumerate((center - .62, center + .62)):
            cube(stage, prefix + f"/BinSide{index}", (x, .79, .52), (.025, .74, .22), colors["bin"], collision=True)
        for index, y in enumerate((.42, 1.16)):
            cube(stage, prefix + f"/BinEnd{index}", (center, y, .52), (1.22, .025, .22), colors["bin"], collision=True)
        body_paths = {}
        for item, (x, size) in items.items():
            path = prefix + "/" + item.capitalize()
            body = UsdGeom.Xform.Define(stage, path)
            body.AddTranslateOp().Set(Gf.Vec3d(center + x, -.065, .803 + size[2] / 2))
            cube(stage, path + "/Shape", (0, 0, 0), size, colors[item], collision=True)
            accent_z = size[2] / 2 + .001
            cube(stage, path + "/Accent", (0, 0, accent_z), (size[0] * .46, size[1] * .34, .003), colors["white"])
            rigid = UsdPhysics.RigidBodyAPI.Apply(body.GetPrim())
            rigid.CreateVelocityAttr(Gf.Vec3f(0, 2.30 if name == "ClearEverything" or item == "snack" else 0, 0))
            UsdPhysics.MassAPI.Apply(body.GetPrim()).CreateMassAttr(.15)
            body_paths[item] = path
        scenarios[name] = (center, body_paths)

    camera = UsdGeom.Camera.Define(stage, "/World/Camera")
    pose = Gf.Matrix4d(1).SetLookAt(Gf.Vec3d(0, 4.25, 3.05), Gf.Vec3d(0, .24, .62), Gf.Vec3d(0, 0, 1)).GetInverse()
    camera.AddTransformOp().Set(pose)
    camera.CreateFocalLengthAttr(24)
    ambient = UsdLux.DomeLight.Define(stage, "/World/Ambient")
    ambient.CreateIntensityAttr(420)
    light = UsdLux.DistantLight.Define(stage, "/World/Key")
    light.CreateIntensityAttr(1350)
    light.CreateAngleAttr(14)
    light.AddRotateXYZOp().Set(Gf.Vec3f(34, -17, 0))
    print("DESK_READY | Two CAD-defined workbenches | Same initial objects", flush=True)
    cache = UsdUtils.StageCache.Get()
    stage_id = cache.Insert(stage).ToLongInt()
    driver = get_physx_simulation_interface()
    query = get_physx_interface()
    body_order = [path for _, body_paths in scenarios.values() for path in body_paths.values()]
    poses = []
    driver.attach_stage(stage_id)
    try:
        for frame in range(150):
            driver.simulate(1 / 60, frame / 60)
            driver.fetch_results()
            positions = []
            for path in body_order:
                pose = query.get_rigidbody_transformation(path)
                assert pose["ret_val"], path
                positions.append(list(pose["position"]) + list(pose["rotation"]))
            poses.append(positions)
            if frame in (16, 33, 59, 149):
                print(f"PHYSX_STEP {frame + 1}/150", flush=True)
        results = {}
        for name, (center, body_paths) in scenarios.items():
            objects = {}
            for item, path in body_paths.items():
                pose = query.get_rigidbody_transformation(path)
                assert pose["ret_val"], path
                x, y, z = list(pose["position"])
                on_desk = abs(x - center) < .60 and abs(y) < .30 and z >= .80
                in_bin = abs(x - center) < .60 and .42 < y < 1.16 and .44 < z < .66
                objects[item] = {"xyz_m": [x, y, z], "on_desk": on_desk, "in_bin": in_bin}
            results[name] = {"objects": objects, "remaining_on_desk": sum(entry["on_desk"] for entry in objects.values()),
                             "task_passed": objects["snack"]["in_bin"] and objects["mouse"]["on_desk"] and objects["cup"]["on_desk"]}
        record = {"physics": "Isaac Sim 6.2.0 / PhysX", "simulated_seconds": 2.5,
                  "actuation": "initial linear velocities on selected objects", "scenarios": results,
                  "sample_rate_hz": 60, "body_paths": body_order,
                  "geometry_sizes_m": {kind: list(size) for kind, (_, size) in items.items()}}
        assert np.asarray(poses).shape == (150, 6, 7)
        assert np.isfinite(poses).all()
        np.save(output / "poses.npy", np.asarray(poses, dtype=np.float32))
        (output / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        print(f"RESULT {json.dumps(record)}", flush=True)
    finally:
        driver.detach_stage()
        cache.Erase(stage)


try:
    main()
finally:
    app.close()
