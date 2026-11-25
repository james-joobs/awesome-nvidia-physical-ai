"""Download only camera RGB from Voxel51's public KITScenes release."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from PIL import Image

REPO = "Voxel51/kitscenes-multimodal"
SCENE = "00fc1b9b-005e-554c-7733-c4c0adeca015"
RING = ["rear", "front", "front_left", "front_right", "rear_left", "rear_right"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scene", default=SCENE)
    parser.add_argument("--first", type=int, default=23)
    parser.add_argument("--last", type=int, default=95)
    parser.add_argument("--stride", type=int, default=3)
    parser.add_argument("--revision")
    args = parser.parse_args()
    revision = args.revision or HfApi().dataset_info(REPO).sha
    card = hf_hub_download(REPO, "samples.json", repo_type="dataset", revision=revision)
    source = json.loads(Path(card).read_text())["samples"]
    times = list(range(args.first, args.last+1, args.stride))
    methods = {f"camera_ring_{name}": i for i, name in enumerate(RING)}
    frames = {(row["frame"], row["sensor"]): row for row in source
              if row["scene_id"] == args.scene and row["sensor"] in methods and row["frame"] in times}
    native = args.out / "sources"
    images = args.out / "images"
    native.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)

    def save(item):
        (frame, sensor), row = item
        camera = methods[sensor]
        file = hf_hub_download(REPO, row["filepath"], repo_type="dataset", revision=revision)
        name = f"{frame:03d}-{camera}.jpg"
        with Image.open(file) as image:
            w, h = image.size
            image.convert("RGB").save(native / name, quality=96)
            small = image.convert("RGB")
            small.thumbnail((1440, 960), Image.Resampling.LANCZOS)
            small.save(images / name, quality=94)
        rw, rh = row["resolution"]["width"], row["resolution"]["height"]
        intrinsics = row["intrinsics"]
        f = intrinsics["focal_length"]
        k = [f*small.width/rw, f*small.height/rh,
             intrinsics["principal_point_u"]*small.width/rw, intrinsics["principal_point_v"]*small.height/rh]
        return {"file": name, "frame": frame, "camera": camera, "source_file":row["filepath"],
                "native_size": [w,h], "size": [small.width,small.height], "intrinsics": k}

    if len(frames) != len(times)*len(RING):
        raise ValueError("The requested clip does not have all six cameras")
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(save, sorted(frames.items())))
    manifest = {"source": REPO, "revision":revision, "scene":args.scene, "camera_names":RING, "frames":times,
                "images":rows, "uses_lidar":False, "uses_supplied_camera_intrinsics":True,
                "uses_supplied_ego_poses":False}
    (args.out/"input.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"Saved {len(rows)} RGB views with camera intrinsics")


if __name__ == "__main__":
    main()
