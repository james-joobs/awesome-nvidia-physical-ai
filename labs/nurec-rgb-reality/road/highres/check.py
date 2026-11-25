"""Verify the recorded high-resolution Reality View packages."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image

CAMERAS = {"front", "front_left", "front_right", "rear", "rear_left", "rear_right"}
ROUTES = {"bridge": ("", 150, 7.2, 20), "tram": ("tram", 240, 19.5, 20),
          "avenue": ("avenue", 546, 27.0, 18)}


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
    tracking = json.loads((package/"tracks.json").read_text())
    assert tracking["schema"] == 1 and set(tracking["cameras"]) == CAMERAS
    assert tracking["times"] == [frame["time"] for frame in frames]
    seen_cameras = {}
    cars = 0
    for camera, series in tracking["cameras"].items():
        counts = defaultdict(list)
        assert len(series) == len(frames)
        for observations in series:
            assert len(observations) == len({row[0] for row in observations})
            for track, category, (x1, y1, x2, y2), confidence in observations:
                assert 0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1 and 0 < confidence <= 1
                assert seen_cameras.setdefault(track, camera) == camera
                counts[track].append(category)
        for observations in counts.values():
            assert len(observations) >= 2 and len(set(observations)) == 1
            cars += observations[0] == "car" and len(observations) >= 3
    assert cars > 0
    assert all(first["time"] < second["time"] for first, second in zip(frames, frames[1:]))
    for frame, pose in zip(frames, fit["front_path"], strict=True):
        assert abs((pose["frame"]-fit["front_path"][0]["frame"])/10-frame["time"]) < .001
        assert CAMERAS == set(frame["rgb"]) == set(frame["cameras"])
        assert "actors" not in frame
        for reference in frame["rgb"].values():
            with Image.open(package/reference) as image:
                assert image.format == "WEBP" and image.size == (768, 498)
                image.verify()


def main(package=None, route="bridge"):
    if package is not None:
        _, views, seconds, minimum_psnr = ROUTES[route]
        verify_route(package, views, seconds, minimum_psnr)
        print(f"KITSCENES_NOVEL_VIEW_OK: {route}, {views} registered camera views, {seconds:g} seconds")
        return
    data = Path(__file__).resolve().parents[4]/"site/public/showcase"
    for route, views, seconds, minimum_psnr in ROUTES.values():
        verify_route(data/"reality-kitscenes"/route/"road", views, seconds, minimum_psnr)
    for clip in ("reality-kitscenes", "reality-road-novel", "reality-kitscenes-surround"):
        assert (data/(clip+".mp4")).stat().st_size > 10000
        assert (data/(clip+".jpg")).stat().st_size > 1000
    print("KITSCENES_NOVEL_VIEW_OK: three reconstructions, six synchronized camera views per route, and recordings")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, help="Verify this local road package")
    parser.add_argument("--route", choices=ROUTES, default="bridge", help="Preset of the local package")
    args = parser.parse_args()
    main(args.package, args.route)
