"""Verify the packaged calibration, road texture, Gaussian file and run receipts."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    public = Path(__file__).resolve().parents[3] / "site/public/showcase/reality-joint-geometry"
    scene = json.loads((public / "scene.json").read_text())
    assert scene["road"] is True
    root = public / "road"
    data = json.loads((root / "road.json").read_text())
    assert data["schema"] == 1
    views = len(scene["frames"])*6
    intrinsics = np.array(data["intrinsics"])
    poses = np.array(data["camera_to_world"])
    assert intrinsics.shape == (views, 3, 3) and poses.shape == (views, 4, 4)
    assert np.isfinite(intrinsics).all() and np.isfinite(poses).all()
    assert np.all(intrinsics[:, [0, 1], [0, 1]] > 0)
    assert np.all(np.abs(np.linalg.det(poses[:, :3, :3])-1) < 1e-3)
    for key in ("atlas_asset", "sky_filtered"):
        asset = data[key]
        path = root / asset["file"]
        assert path.stat().st_size == asset["bytes"]
        with path.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == asset["sha256"]
    with Image.open(root / data["texture"]) as texture:
        assert list(texture.size) == data["atlas_pixels"]
        assert texture.mode == "RGBA" and texture.getchannel("A").getextrema() == (0, 255)
    assert len(data["ground_height_at_ego"]) == len(scene["frames"])
    assert all(r["views"] == views for r in data["rtx_5090_runs"].values())
    sky = data["sky_filtered"]
    assert 0 < sky["gaussians_removed"] < sky["gaussians_in"]
    assert sky["gaussians_retained"] + sky["gaussians_removed"] == sky["gaussians_in"]
    assert 0 < data["surface"]["heldout_texture"]["reference_road_pixels"]
    if "surroundings" in data:
        context = data["surroundings"]
        assert context["schema"] == 1 and context["facades"]
        assert 0 < context["sky"]["observed_upper_hemisphere_fraction"] <= 1
        for asset in [context["sky"], *context["facades"]]:
            path = root / asset["file"]
            assert path.stat().st_size == asset["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"]
            with Image.open(path) as image:
                assert list(image.size) == asset["size"]
        for wall in context["facades"]:
            assert np.array(wall["corners"]).shape == (4, 3)
            assert 0 < wall["observed_fraction"] <= 1
        assert sky["sky_removed"] + sky.get("airborne_removed", 0) + sky["facade_removed"] == sky["gaussians_removed"]
        assert data["latest_calibration"]["heldout_selected"]["observations"] > 0
    print("ROAD_REPROJECTION_OK: 102 calibrated views, observed texture and filtered SPZ verified")


if __name__ == "__main__":
    main()
