"""Check the recorded RGB, depth and semantic masks against Replicator's manifest."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def check(folder):
    report = json.loads((folder / "result.json").read_text())
    width, height = report["resolution_px"]
    frames = report["frames"]
    assert len(frames) == 12
    seen = set()
    for i, row in enumerate(frames):
        assert row["frame"] == i
        sample = folder / "frames" / f"{i:02d}"
        with Image.open(sample / "rgb.png") as png:
            rgb = np.asarray(png.convert("RGB"))
        depth = np.load(sample / "depth_m.npy", allow_pickle=False)
        ids = np.load(sample / "semantic_ids.npy", allow_pickle=False)
        labels = json.loads((sample / "semantic_labels.json").read_text())
        assert rgb.shape == (height, width, 3) and ids.shape == depth.shape == (height, width)
        digest = hashlib.sha256(rgb.tobytes()).hexdigest()
        assert digest == row["rgb_sha256"] and digest not in seen
        seen.add(digest)
        target_ids = [int(key) for key, value in labels.items()
                      if (value.get("class") if isinstance(value, dict) else value) == "target"]
        mask = np.isin(ids, target_ids)
        assert np.count_nonzero(mask) == row["target_pixels"] > 0
        assert np.isfinite(depth[mask]).all() and (depth[mask] > 0).all()
    print(f"Verified {len(frames)} RGB/depth/semantic triplets at {width}×{height}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    check(parser.parse_args().capture)
