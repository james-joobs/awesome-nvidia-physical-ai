import argparse
import json
from pathlib import Path

from isaacsim import SimulationApp

parser = argparse.ArgumentParser(description="Run the shared box-stack scene using PhysX.")
parser.add_argument("output", type=Path)
output = parser.parse_args().output
output.mkdir(parents=True, exist_ok=True)
app = SimulationApp({"headless": True, "fast_shutdown": True})
import carb
import numpy as np
from omni.physx import get_physx_interface, get_physx_simulation_interface
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, UsdUtils

spec = json.loads(Path(__file__).with_name("scene.json").read_text())
carb.settings.get_settings().set_bool("/physics/updateToUsd", True)
stage = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.Xform.Define(stage, "/World")
scene = UsdPhysics.Scene.Define(stage, "/World/Physics")
scene.CreateGravityMagnitudeAttr(spec["gravity"])
scene.CreateGravityDirectionAttr(Gf.Vec3f(0, 0, -1))
material = UsdShade.Material.Define(stage, "/World/Contact")
material_api = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
material_api.CreateStaticFrictionAttr(spec["friction"])
material_api.CreateDynamicFrictionAttr(spec["friction"])
material_api.CreateRestitutionAttr(0.0)

def box(name, pos, half_extents, dynamic=False):
    path = f"/World/{name}"
    body = UsdGeom.Xform.Define(stage, path)
    body.AddTranslateOp().Set(Gf.Vec3d(*pos))
    collider = UsdGeom.Cube.Define(stage, f"{path}/Shape")
    collider.CreateSizeAttr(2.0)
    collider.AddScaleOp().Set(Gf.Vec3f(*half_extents))
    UsdPhysics.CollisionAPI.Apply(collider.GetPrim())
    UsdShade.MaterialBindingAPI.Apply(collider.GetPrim()).Bind(material, materialPurpose="physics")
    if dynamic:
        UsdPhysics.RigidBodyAPI.Apply(body.GetPrim())
        UsdPhysics.MassAPI.Apply(body.GetPrim()).CreateDensityAttr(spec["box_density"])
    return path

for part in ("table", "floor"):
    box(part, spec[f"{part}_pos"], spec[f"{part}_half_extents"])
half = spec["box_half_extent"]
paths = [box(f"Box{i}", pos, [half] * 3, True) for i, pos in enumerate(spec["boxes"])]
cache = UsdUtils.StageCache.Get()
stage_id = cache.Insert(stage).ToLongInt()
direct = get_physx_simulation_interface()
query = get_physx_interface()
direct.attach_stage(stage_id)
try:
    poses = [[[float(x) for x in pos] + [0.0, 0.0, 0.0, 1.0] for pos in spec["boxes"]]]
    for frame in range(spec["frames"]):
        dt = 1 / spec["step_hz"]
        direct.simulate(dt, frame * dt)
        direct.fetch_results()
        current = []
        for path in paths:
            pose = query.get_rigidbody_transformation(path)
            if not pose["ret_val"]:
                raise RuntimeError(f"PhysX returned no pose for {path}")
            current.append(list(pose["position"]) + list(pose["rotation"]))
        poses.append(current)
        if frame in (0, 119, 239):
            print(f"PHYSX | step {frame + 1} | top-body z = {current[-1][2]:.4f} m", flush=True)
finally:
    direct.detach_stage()
    cache.Erase(stage)
poses = np.array(poses, dtype=np.float32)
assert np.isfinite(poses).all()
assert np.max(np.abs(poses[-1, :, :3] - poses[0, :, :3])) > 0.1
np.save(output / "physx-poses.npy", poses)
print(f"PHYSX_DONE Isaac Sim 6.2 | {poses.shape}", flush=True)
app.close()
