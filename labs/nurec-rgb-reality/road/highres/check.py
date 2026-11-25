"""Verify the recorded high-resolution Reality View packages."""
import hashlib
import json
from collections import defaultdict
from math import dist
from pathlib import Path

from PIL import Image

CAMERAS = {"front", "front_left", "front_right", "rear", "rear_left", "rear_right"}


def verify_route(package, views, seconds, minimum_psnr):
    scene = json.loads((package/"road.json").read_text())
    fit = scene["scene_fit"]
    assert scene["schema"] == 1
    assert fit["model_views"] == fit["total_views"] == views
    assert fit["train_views"] + fit["heldout_views"] == fit["model_views"]
    assert len(fit["front_path"]) == views//len(CAMERAS)
    assert fit["native_size"] == [3504, 2272]
    assert fit["heldout_static_psnr_mean"] > minimum_psnr and fit["road_coverage"] > .1
    for record in [scene["sky_filtered"], fit["sky"], fit["atlas_asset"]]:
        file = package/record["file"]
        assert file.stat().st_size == record["bytes"]
        with file.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == record["sha256"]
    with Image.open(package/scene["texture"]) as image:
        assert list(image.size) == fit["road_size"]

    surround = json.loads((package/"surround.json").read_text())
    frames = surround["frames"]
    assert surround["schema"] == 1 and surround["source_scene"] == fit["scene"]
    assert len(frames) == len(fit["front_path"])
    assert frames[-1]["time"] == seconds
    assert surround["tracks"]["car"] > 0
    assert all(first["time"] < second["time"] for first, second in zip(frames, frames[1:]))
    positions = defaultdict(list)
    for frame, pose in zip(frames, fit["front_path"], strict=True):
        assert abs((pose["frame"]-fit["front_path"][0]["frame"])/10-frame["time"]) < .001
        assert CAMERAS == set(frame["rgb"]) == set(frame["cameras"])
        for track, category, x, y, heading in frame["actors"]:
            if category == "car":
                positions[track].append((x, y))
        for reference in frame["rgb"].values():
            with Image.open(package/reference) as image:
                assert image.format == "WEBP" and image.width == 768
                image.verify()
    assert any(dist(points[0], points[-1]) > 1.5 for points in positions.values())


def main():
    data = Path(__file__).resolve().parents[4]/"site/public/showcase"
    routes = (("", 150, 7.2, 20), ("tram", 240, 19.5, 20), ("avenue", 546, 27.0, 18))
    for route, views, seconds, minimum_psnr in routes:
        verify_route(data/"reality-kitscenes"/route/"road", views, seconds, minimum_psnr)
    for clip in ("reality-kitscenes", "reality-road-novel", "reality-kitscenes-surround"):
        assert (data/(clip+".mp4")).stat().st_size > 10000
        assert (data/(clip+".jpg")).stat().st_size > 1000
    print("KITSCENES_NOVEL_VIEW_OK: three reconstructions, six synchronized camera views per route, and recordings")


if __name__ == "__main__":
    main()
