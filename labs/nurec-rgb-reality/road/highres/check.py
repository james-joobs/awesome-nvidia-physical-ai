"""Verify the recorded high-resolution Reality View package."""
import hashlib
import json
from pathlib import Path
from PIL import Image


def main():
    data = Path(__file__).resolve().parents[4]/"site/public/showcase"
    package = data/"reality-kitscenes/road"
    scene = json.loads((package/"road.json").read_text())
    fit = scene["scene_fit"]
    assert scene["schema"] == 1
    assert fit["model_views"] == fit["total_views"] == 150
    assert fit["train_views"] + fit["heldout_views"] == fit["model_views"]
    assert len(fit["front_path"]) == 25
    assert fit["native_size"] == [3504, 2272]
    assert fit["heldout_static_psnr_mean"] > 20 and fit["road_coverage"] > .1
    for record in [scene["sky_filtered"], fit["sky"], fit["atlas_asset"]]:
        file = package/record["file"]
        assert file.stat().st_size == record["bytes"]
        with file.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == record["sha256"]
    with Image.open(package/scene["texture"]) as image:
        assert list(image.size) == fit["road_size"]
    for clip in ("reality-kitscenes", "reality-road-novel"):
        assert (data/(clip+".mp4")).stat().st_size > 10000
        assert (data/(clip+".jpg")).stat().st_size > 1000
    print("KITSCENES_NOVEL_VIEW_OK: scene, road, sky and both recording files verified")


if __name__ == "__main__":
    main()
