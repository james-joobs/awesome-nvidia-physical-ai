"""Check the CAD workbench capture on a CPU, from an archive or a fresh run."""

import argparse
import json
import shutil
from math import isfinite
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image
from pxr import Usd, UsdGeom, UsdPhysics

from backproject import TRUE_CUBE_X, reconstruct

LAB = Path(__file__).resolve().parent
SIZE = (1280, 720)
CHANNELS = ("rgb_{:04}.png", "distance_to_image_plane_{:04}.npy",
            "semantic_segmentation_{:04}.npy", "semantic_segmentation_labels_{:04}.json")
FRAME_FILES = [tuple(pattern.format(i) for pattern in CHANNELS) for i in range(len(TRUE_CUBE_X))]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unpack_recording(capture):
    target = capture / "replicator"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LAB / "workbench_scene.usda", capture / "workbench_scene.usda")
    with ZipFile(LAB / "replicator-data.zip") as archive:
        for names in FRAME_FILES:
            for name in names:
                (target / name).write_bytes(archive.read(f"replicator/{name}"))


def check_scene(capture):
    stage = Usd.Stage.Open(str(capture / "workbench_scene.usda"))
    require(UsdGeom.GetStageMetersPerUnit(stage) == 1, "Expected USD scene units in meters")
    require(UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z, "Expected a Z-up USD stage")
    tabletop = stage.GetPrimAtPath("/World/Workbench/Tabletop")
    require(tabletop and tabletop.HasAPI(UsdPhysics.CollisionAPI), "Missing tabletop collision geometry")
    bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    box = bounds.ComputeWorldBound(tabletop).ComputeAlignedBox()
    dimensions = np.array(box.GetSize()) * 1000
    require(np.allclose(dimensions, (1200, 600, 40), rtol=0, atol=.5),
            f"Unexpected tabletop dimensions (mm): {dimensions}")
    cube = UsdGeom.Cube.Get(stage, "/World/TestPart/Geometry")
    require(cube and cube.GetSizeAttr().HasAuthoredValue(), "Missing test cube size")
    expected_z = float(box.GetMax()[2] + cube.GetSizeAttr().Get() / 2)
    return dimensions.tolist(), expected_z


def check_frames(capture, output):
    folder = capture / "replicator"
    expected_rgb = {files[0] for files in FRAME_FILES}
    require({file.name for file in folder.glob("rgb_*.png")} == expected_rgb,
            f"Expected {len(expected_rgb)} numbered RGB frames in {folder}")
    stats = []
    for index, (rgb_file, depth_file, ids_file, labels_file) in enumerate(FRAME_FILES):
        with Image.open(folder / rgb_file) as png:
            rgb = png.convert("RGB")
        depth = np.load(folder / depth_file, allow_pickle=False)
        ids = np.load(folder / ids_file, allow_pickle=False)
        labels = json.loads((folder / labels_file).read_text())
        require(rgb.size == SIZE and depth.shape == ids.shape == SIZE[::-1], f"Frame {index}: mismatched shapes")
        require(depth.dtype.kind == "f" and ids.dtype.kind in "iu", f"Frame {index}: wrong depth or mask dtype")
        part_ids = [int(key) for key, label in labels.items()
                    if (label.get("class") if isinstance(label, dict) else label) == "part"]
        mask = np.isin(ids, part_ids)
        part_depth = depth[mask]
        require(part_depth.size >= 1000, f"Frame {index}: fewer than 1,000 labeled cube pixels")
        require(np.isfinite(part_depth).all() and (part_depth > 0).all(),
                f"Frame {index}: cube depth must be finite and positive")
        stats.append({"frame": index, "part_pixels": int(part_depth.size),
                      "median_camera_depth_m": float(np.median(part_depth))})
        if index == 0:
            valid = np.isfinite(depth) & (depth > 0)
            depth_gray = np.zeros(depth.shape, dtype=np.uint8)
            depth_gray[valid] = (255 * (1 - np.clip(depth[valid] / 6, 0, 1))).astype(np.uint8)
            images = (rgb, Image.fromarray(depth_gray), Image.fromarray(mask.astype(np.uint8) * 255))
            preview = Image.new("RGB", (1280, 240))
            for panel, image in enumerate(images):
                preview.paste(image.resize((426, 240)), (panel * 427, 0))
            preview.save(output / "frame-00.png")
    return stats


def check(capture, recorded):
    if recorded:
        require(not (capture / "workbench-result.json").exists(),
                "Use a separate directory for archived frames to preserve the fresh capture")
    output = capture / "check"
    output.mkdir(parents=True, exist_ok=True)
    report_file = output / "report.json"
    report_file.unlink(missing_ok=True)
    if recorded:
        unpack_recording(capture)

    dimensions, expected_z = check_scene(capture)
    final_z = None
    if not recorded:
        summary = json.loads((capture / "workbench-result.json").read_text())
        initial_z, final_z = summary["first_cube_z_m"], summary["final_cube_z_m"]
        require(initial_z is not None and final_z is not None and isfinite(initial_z) and isfinite(final_z)
                and initial_z > expected_z + .05 and abs(final_z - expected_z) <= .02,
                f"Cube did not settle on the tabletop at {expected_z:.4f} m (final: {final_z})")

    frames = check_frames(capture, output)
    points = reconstruct(capture, output / "point-cloud")
    max_error = max(frame["absolute_displacement_error_mm"] for frame in points["frames"])
    require(isfinite(max_error) and max_error <= 10, f"X displacement error {max_error:.2f} mm exceeds 10 mm")
    report = {
        "input": "recorded" if recorded else "fresh",
        "tabletop_mm": dimensions,
        "resolution_px": SIZE,
        "frames": frames,
        "max_displacement_error_mm": max_error,
        "expected_rest_center_m": expected_z,
        "checked_physics_log": not recorded,
        "final_cube_center_m": final_z,
    }
    report_file.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(frames)} RGB/depth/mask sets at {SIZE[0]}x{SIZE[1]}")
    print(f"PASS: maximum X displacement error {max_error:.2f} mm (limit: 10 mm)")
    if not recorded:
        print(f"PASS: captured cube center {final_z:.4f} m (expected {expected_z:.4f} m)")
    print(f"Report: {report_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="Run directory for inputs and generated results")
    parser.add_argument("--recorded", action="store_true", help="Unpack and check the bundled camera frames")
    args = parser.parse_args()
    try:
        check(args.capture, args.recorded)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Check failed: {error}\n")
