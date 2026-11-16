"""Compare three OpenUSD layouts using the measured bounds of the CAD workbench."""

import argparse
import hashlib
import json
from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    source = Usd.Stage.Open(str(args.source))
    asset_layer = Sdf.Layer.CreateAnonymous()
    for path in ("/World", "/World/Looks", "/World/Workbench"):
        Sdf.CreatePrimInLayer(asset_layer, path)
    for path in ("/World/Looks", "/World/Workbench"):
        Sdf.CopySpec(source.GetRootLayer(), path, asset_layer, path)
    asset = Usd.Stage.Open(asset_layer)
    asset.GetPrimAtPath("/World").SetSpecifier(Sdf.SpecifierDef)
    asset.SetDefaultPrim(asset.GetPrimAtPath("/World"))
    UsdGeom.SetStageUpAxis(asset, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(asset, 1.0)
    asset.Export(str(root / "workbench-asset.usda"))

    stage = Usd.Stage.CreateInMemory()
    scene = UsdGeom.Xform.Define(stage, "/Cell").GetPrim()
    stage.SetDefaultPrim(scene)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    fixed = UsdGeom.Xform.Define(stage, "/Cell/Fixed")
    moved = UsdGeom.Xform.Define(stage, "/Cell/Moved")
    # Resolve both references from a file-backed version of the stage once authored.
    for bench in (fixed, moved):
        bench.GetPrim().GetReferences().AddReference(str((root / "workbench-asset.usda").resolve()))
    variants = scene.GetVariantSets().AddVariantSet("aisle")
    for name, separation in (("narrow", 1.15), ("borderline", 1.35), ("wide", 1.55)):
        variants.AddVariant(name)
        variants.SetVariantSelection(name)
        with variants.GetVariantEditContext():
            UsdGeom.Xformable(moved).AddTranslateOp().Set(Gf.Vec3d(0, separation, 0))
    variants.SetVariantSelection("wide")
    stage.GetRootLayer().Export(str(root / "aisle-layouts.usda"))
    path = root / "aisle-layouts.usda"
    path.write_text(path.read_text().replace(str((root / "workbench-asset.usda").resolve()), "./workbench-asset.usda"))

    measured = Usd.Stage.Open(str(path))
    variants = measured.GetDefaultPrim().GetVariantSets().GetVariantSet("aisle")
    measurements = []
    required = 0.8  # 0.60 m demo cart plus 0.10 m clearance per side.
    for name in ("narrow", "borderline", "wide"):
        variants.SetVariantSelection(name)
        bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
        boxes = []
        for prim_path in ("/Cell/Fixed/Workbench", "/Cell/Moved/Workbench"):
            prim = measured.GetPrimAtPath(prim_path)
            assert prim.IsValid(), prim_path
            world = bounds.ComputeWorldBound(prim).ComputeAlignedRange()
            boxes.append([list(world.GetMin()), list(world.GetMax())])
        gap = boxes[1][0][1] - boxes[0][1][1]
        row = {"variant": name, "clear_m": round(gap, 5), "fits_demo_cart": gap >= required, "bounds_m": boxes}
        print(f"{name:11s} | clear {gap:.3f} m | {'PASS' if row['fits_demo_cart'] else 'FAIL'}", flush=True)
        measurements.append(row)
    assert [item["fits_demo_cart"] for item in measurements] == [False, False, True]
    assert digest == hashlib.sha256(args.source.read_bytes()).hexdigest()
    (root / "result.json").write_text(json.dumps({
        "asset_sha256": digest, "cart_width_m": 0.60, "clearance_per_side_m": 0.10,
        "required_clearance_m": required, "layouts": measurements,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
