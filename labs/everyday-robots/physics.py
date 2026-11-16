"""Compute the falling alarm and the drawer drive response with Isaac Sim PhysX."""

import json
import math
import sys
import traceback
from pathlib import Path

from isaacsim import SimulationApp

app = SimulationApp({"headless": True, "fast_shutdown": True})

from omni.physx import get_physx_interface, get_physx_simulation_interface
from pxr import Gf, Usd, UsdGeom, UsdPhysics, UsdUtils

DT = 1 / 120


def make_stage():
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    world = UsdGeom.Xform.Define(stage, "/World").GetPrim()
    stage.SetDefaultPrim(world)
    scene = UsdPhysics.Scene.Define(stage, "/World/Physics")
    scene.CreateGravityDirectionAttr(Gf.Vec3f(0, 0, -1))
    scene.CreateGravityMagnitudeAttr(9.81)
    return stage


def box(stage, name, center, size):
    shape = UsdGeom.Cube.Define(stage, name)
    shape.CreateSizeAttr(1.0)
    shape.AddTranslateOp().Set(Gf.Vec3d(*center))
    shape.AddScaleOp().Set(Gf.Vec3f(*size))
    UsdPhysics.CollisionAPI.Apply(shape.GetPrim())
    return shape


def body(stage, name, center, size, mass):
    prim = UsdGeom.Xform.Define(stage, name)
    prim.AddTranslateOp().Set(Gf.Vec3d(*center))
    box(stage, name + "/Collision", (0, 0, 0), size)
    UsdPhysics.MassAPI.Apply(prim.GetPrim()).CreateMassAttr(mass)
    return UsdPhysics.RigidBodyAPI.Apply(prim.GetPrim())


def simulate(stage, count, read, before=None):
    cache = UsdUtils.StageCache.Get()
    handle = cache.Insert(stage)
    driver = get_physx_simulation_interface()
    info = get_physx_interface()
    driver.attach_stage(handle.ToLongInt())
    try:
        for i in range(count):
            if before:
                before(i)
            driver.simulate(DT, i * DT)
            driver.fetch_results()
            if i % 4 == 0:
                read(info)
    finally:
        driver.detach_stage()
        cache.Erase(stage)


def alarm(output):
    stage = make_stage()
    z = .844
    box(stage, "/World/Floor", (0, 0, -.06), (20, 20, .12))
    # The drive trace ends 1 cm beyond the remaining tabletop edge.
    box(stage, "/World/Table", (-.61, 0, .78), (1.2, .60, .04))
    buzz = body(stage, "/World/Alarm", (0, 0, z), (.137, .14, .083), .35)
    buzz.CreateVelocityAttr(Gf.Vec3f(.40, 0, 0))
    samples = [[0, z, 0]]

    def read(info):
        pose = info.get_rigidbody_transformation("/World/Alarm")
        assert pose["ret_val"]
        x, _, height = pose["position"]
        qx, qy, qz, qw = pose["rotation"]
        pitch = math.degrees(math.asin(max(-1, min(1, 2 * (qw*qy-qz*qx)))))
        samples.append([float(x), float(height), float(pitch)])

    simulate(stage, 272, read)
    assert min(row[1] for row in samples) < .12
    (output / "alarm-physx.json").write_text(json.dumps({
        "engine": "Isaac Sim PhysX", "samples_fps": 30, "start_height_m": z,
        "resting_center_z_m": samples[-1][1], "samples": samples,
    }, indent=2) + "\n")
    print(f"FALL_OK: starts at {z:.3f} m, settles at {samples[-1][1]:.3f} m", flush=True)


def drawers(input_trace, output):
    inputs = json.loads(input_trace.read_text())["cases"]
    stage = make_stage()
    drives, samples = [], [[] for _ in inputs]
    for index, _ in enumerate(inputs):
        x = index * .82
        name = f"/World/Drawer_{index}"
        body(stage, name, (x, 0, .85), (.55, .35, .059), .8)
        joint = UsdPhysics.PrismaticJoint.Define(stage, f"/World/Slide_{index}")
        joint.CreateBody1Rel().SetTargets([name])
        joint.CreateAxisAttr("Y")
        joint.CreateLocalPos0Attr(Gf.Vec3f(x, 0, .85))
        joint.CreateLocalPos1Attr(Gf.Vec3f(0))
        joint.CreateLowerLimitAttr(0.0)
        joint.CreateUpperLimitAttr(.309)
        drive = UsdPhysics.DriveAPI.Apply(joint.GetPrim(), "linear")
        drive.CreateTypeAttr("force")
        drive.CreateStiffnessAttr(650)
        drive.CreateDampingAttr(38)
        drive.CreateMaxForceAttr(95)
        drives.append(drive.CreateTargetPositionAttr(0))

    def before(step):
        if step % 4 == 0:
            for drive, case in zip(drives, inputs, strict=True):
                drive.Set(.305 * case["trace"][step // 4]["drawer_closed_fraction"])

    def read(info):
        for index, row in enumerate(samples):
            pose = info.get_rigidbody_transformation(f"/World/Drawer_{index}")
            assert pose["ret_val"]
            row.append(max(0.0, float(pose["position"][1])))

    count = len(inputs[0]["trace"])
    simulate(stage, count * 4, read, before)
    assert all(len(row) == count for row in samples)
    assert samples[0][-1] > .285 and all(max(row) < .012 for row in samples[1:])
    cases = [{"scenario": case["scenario"], "final_position_m": row[-1], "position_m": row}
             for case, row in zip(inputs, samples, strict=True)]
    (output / "drawer-physx.json").write_text(json.dumps({
        "engine": "Isaac Sim PhysX prismatic drive", "sample_rate_hz": 30, "cases": cases,
    }, indent=2) + "\n")
    print(f"DRAWERS_OK: final positions {[(row['scenario'], round(row['final_position_m'], 4)) for row in cases]}", flush=True)


try:
    working = Path(sys.argv[1])
    working.mkdir(parents=True, exist_ok=True)
    alarm(working)
    drawers(Path(sys.argv[2]), working)
except Exception:
    traceback.print_exc()
    raise
finally:
    app.close()
