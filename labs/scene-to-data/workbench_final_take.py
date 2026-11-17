"""Render the actual CAD-derived scene and Replicator outputs on RTX."""
import argparse
import json
import time
from pathlib import Path

from isaacsim import SimulationApp

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mesh", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--headless", action="store_true", help="Capture without opening a viewport")
args = parser.parse_args()
cap = args.output.resolve()
cap.mkdir(parents=True, exist_ok=True)
app = SimulationApp({
    "headless": args.headless, "width": 1440, "height": 900, "window_width": 1440, "window_height": 900,
    "renderer": "RaytracedLighting", "anti_aliasing": 2, "fast_shutdown": True,
})

import carb
import numpy as np
from PIL import Image
import omni.physx
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from isaacsim.core.utils.semantics import add_labels
from omni.kit.viewport.utility import get_active_viewport
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, UsdShade

settings = carb.settings.get_settings()
settings.set_bool("/physics/updateToUsd", True)
settings.set_bool("/omni/replicator/captureOnPlay", False)
omni.usd.get_context().new_stage()
stage = omni.usd.get_context().get_stage()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
world = UsdGeom.Xform.Define(stage,"/World")
stage.SetDefaultPrim(world.GetPrim())
scene = UsdPhysics.Scene.Define(stage,"/World/Physics")
scene.CreateGravityDirectionAttr(Gf.Vec3f(0,0,-1))
scene.CreateGravityMagnitudeAttr(9.81)

def material(name, rgb, roughness, metallic=0.0):
    target = UsdShade.Material.Define(stage, "/World/Looks/"+name)
    shader = UsdShade.Shader.Define(stage,target.GetPath().AppendChild("Shader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor",Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*rgb))
    shader.CreateInput("roughness",Sdf.ValueTypeNames.Float).Set(roughness)
    shader.CreateInput("metallic",Sdf.ValueTypeNames.Float).Set(metallic)
    target.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),"surface")
    return target

def bind(prim, look):
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(look)

def block(name, location, dimensions, look):
    obj=UsdGeom.Cube.Define(stage, "/World/"+name)
    obj.CreateSizeAttr(1.0)
    obj.AddTranslateOp().Set(Gf.Vec3d(*location))
    obj.AddScaleOp().Set(Gf.Vec3d(*dimensions))
    bind(obj.GetPrim(),look)
    return obj

top_look=material("Top",(.48,.30,.15),.34)
metal=material("Metal",(.039,.16,.19),.31,.54)
shelf=material("Shelf",(.075,.19,.20),.43,.35)
floor=material("Floor",(.072,.099,.12),.56)
orange=material("Orange",(.90,.22,.031),.33,.05)
mint=material("Mark",(.06,.42,.38),.45)
light_label=material("White",(.72,.78,.79),.55)
root=UsdGeom.Xform.Define(stage,"/World/Workbench")
for part in json.loads(args.mesh.read_text()):
    m=UsdGeom.Mesh.Define(stage,root.GetPath().AppendChild(part["name"]))
    m.CreatePointsAttr([Gf.Vec3f(*p) for p in part["points"]])
    m.CreateFaceVertexCountsAttr([3]*(len(part["indices"])//3))
    m.CreateFaceVertexIndicesAttr(part["indices"])
    m.CreateSubdivisionSchemeAttr("none")
    m.CreateDoubleSidedAttr(True)
    bind(m.GetPrim(),top_look if part["name"]=="Tabletop" else shelf if part["name"]=="Shelf" else metal)
    if part["name"]=="Tabletop":
        UsdPhysics.CollisionAPI.Apply(m.GetPrim())
        UsdPhysics.MeshCollisionAPI.Apply(m.GetPrim()).CreateApproximationAttr("convexHull")
add_labels(root.GetPrim(), ["workbench"], instance_name="class")
ground=block("Floor",(0,0,-.037),(40,40,.07),floor)
UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
for i,x in enumerate((-0.83,0.83)):
    block(f"FloorMark{i}",(x,0,.001),(.021,1.65,.002),mint)
for i,y in enumerate((-.82,.82)):
    block(f"CrossMark{i}",(0,y,.001),(1.66,.021,.002),mint)
for i,x in enumerate((-.30,.30)):
    block(f"TopMark{i}",(x,.07,.801),(.007,.27,.002),light_label)
body = UsdGeom.Xform.Define(stage, "/World/TestPart")
cube_location = body.AddTranslateOp()
cube_location.Set(Gf.Vec3d(.125, -.075, 1.23))
cube = UsdGeom.Cube.Define(stage, body.GetPath().AppendChild("Geometry"))
cube.CreateSizeAttr(.123)
bind(cube.GetPrim(), orange)
UsdPhysics.CollisionAPI.Apply(cube.GetPrim())
UsdPhysics.RigidBodyAPI.Apply(body.GetPrim()).CreateRigidBodyEnabledAttr(True)
UsdPhysics.MassAPI.Apply(body.GetPrim()).CreateMassAttr(.21)
add_labels(cube.GetPrim(), ["part"], instance_name="class")

def aim(prim, pos, target):
    xf=Gf.Matrix4d(1).SetLookAt(Gf.Vec3d(*pos),Gf.Vec3d(*target),Gf.Vec3d(0,0,1)).GetInverse()
    UsdGeom.Xformable(prim).AddTransformOp().Set(xf)

camera=UsdGeom.Camera.Define(stage,"/World/InspectionCamera")
aim(camera.GetPrim(), (2.04,-2.42,1.83), (0,0,.61))
camera.CreateFocalLengthAttr(36)
camera.CreateClippingRangeAttr(Gf.Vec2f(.05,35))
ambient=UsdLux.DomeLight.Define(stage,"/World/Ambient")
ambient.CreateIntensityAttr(380)
key=UsdLux.RectLight.Define(stage,"/World/Key")
aim(key.GetPrim(),(-1.35,-1.19,2.82),(0,0,.5))
key.CreateWidthAttr(2.15)
key.CreateHeightAttr(1.65)
key.CreateIntensityAttr(1250)
rim=UsdLux.RectLight.Define(stage,"/World/Rim")
aim(rim.GetPrim(),(1.8,1.4,2.1),(0,0,.67))
rim.CreateWidthAttr(1.9)
rim.CreateHeightAttr(1.6)
rim.CreateIntensityAttr(710)
rim.CreateColorAttr(Gf.Vec3f(.55,.81,1.0))

cap.mkdir(exist_ok=True)
stage.Export(str(cap/"workbench_scene.usda"))
for _ in range(12):
    app.update()
viewport = None if args.headless else get_active_viewport()
if viewport:
    viewport.camera_path = camera.GetPath()
for _ in range(10):
    app.update()
rp=rep.create.render_product(camera.GetPath(),(1280,720))
timeline = omni.timeline.get_timeline_interface()
annotators = {
    "rgb": rep.AnnotatorRegistry.get_annotator("rgb"),
    "distance_to_image_plane": rep.AnnotatorRegistry.get_annotator("distance_to_image_plane"),
    "semantic_segmentation": rep.AnnotatorRegistry.get_annotator("semantic_segmentation",
                                                                 init_params={"colorize": False}),
}
for annotator in annotators.values():
    annotator.attach([rp])
for _ in range(12):
    rep.orchestrator.step(rt_subframes=8, pause_timeline=True)
    sample = np.asarray(annotators["rgb"].get_data())
    if sample.ndim == 3 and sample[:,:,:3].mean() > 5:
        break
else:
    raise RuntimeError("RTX camera did not produce an initialized RGB frame")
print("STAGE_READY: CAD-derived OpenUSD scene, Replicator camera 1280x720", flush=True)
if viewport:
    (cap/"viewport-ready").touch()
    until = time.monotonic() + 4
    while time.monotonic() < until:
        app.update()

def cube_position():
    value = omni.physx.get_physx_interface().get_rigidbody_transformation(str(body.GetPath()))
    return tuple(float(x) for x in value["position"]) if value.get("ret_val",False) else None

timeline.play()
positions = []
for index in range(48):
    rep.orchestrator.step(delta_time=1/30, rt_subframes=2, pause_timeline=False)
    positions.append(cube_position())
    if index in (0, 20, 47):
        print(f"PHYSICS_FRAME {index:02d} | part {positions[-1]}", flush=True)
timeline.stop()
for _ in range(3):
    app.update()

out = cap/"replicator"
out.mkdir(exist_ok=True)
focus_values = []
for frame, x in enumerate((.125, -.18, .23, .03)):
    cube_location.Set(Gf.Vec3d(x, -.075, .8615))
    key.GetIntensityAttr().Set(1100 + 170 * frame)
    for _ in range(3):
        app.update()
    rep.orchestrator.step(delta_time=0, rt_subframes=10, pause_timeline=True)
    rgb = np.asarray(annotators["rgb"].get_data(), np.uint8)
    depth = np.asarray(annotators["distance_to_image_plane"].get_data(), np.float32)
    value = annotators["semantic_segmentation"].get_data()
    ids = np.asarray(value["data"], np.uint32)
    labels = value["info"]["idToLabels"]
    part_labels = [int(i) for i,label in labels.items() if
                   (label.get("class") if isinstance(label,dict) else label) == "part"]
    part = np.isin(ids, part_labels)
    assert rgb.shape[0:2] == depth.shape == ids.shape == (720, 1280)
    assert part.any() and np.isfinite(depth[part]).all(), (frame, labels)
    Image.fromarray(rgb[:,:,:3]).save(out/f"rgb_{frame:04d}.png")
    np.save(out/f"distance_to_image_plane_{frame:04d}.npy",depth)
    np.save(out/f"semantic_segmentation_{frame:04d}.npy",ids)
    (out/f"semantic_segmentation_labels_{frame:04d}.json").write_text(json.dumps(labels))
    approx_part_depth = float(np.median(depth[part]))
    focus_values.append({"frame":frame, "part_pixels":int(part.sum()), "part_depth_m":approx_part_depth})
    print(f"CAPTURE_FRAME {frame:02d} | part pixels {part.sum()} | median depth {approx_part_depth:.3f} m",flush=True)
    if viewport:
        until=time.monotonic()+1.1
        while time.monotonic()<until:
            app.update()

valid = [point[2] for point in positions if point is not None]
expected = .8 + .123/2
summary = {"physics_frames":len(positions),"tabletop_top_m":.8,"expected_rest_center_m":expected,
           "first_cube_z_m":valid[0] if valid else None,"final_cube_z_m":valid[-1] if valid else None,
           "rest_within_2cm":bool(valid and abs(valid[-1]-expected)<.02),
           "replicator_frames":focus_values}
(cap/"workbench-result.json").write_text(json.dumps(summary,indent=2))
print("RESULT",json.dumps(summary),flush=True)
if viewport:
    (cap/"viewport-result").touch()
    until = time.monotonic() + 10
    while time.monotonic() < until:
        app.update()
app.close()
