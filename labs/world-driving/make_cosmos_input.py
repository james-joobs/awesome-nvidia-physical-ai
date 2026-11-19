"""Prepare a short, explicitly generative Cosmos test from our own simulator image."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--image", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--direction", choices=["left", "right"], default="right")
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
manifest = {
    "model_mode": "image2video",
    "prompt": (
        "A fixed camera watches a wooden workbench in a clean robotics simulation. "
        "A yellow cube is in the center, a mint green cube at the rear left and a tall dark block on the right. "
        f"The yellow cube slides slowly to the {args.direction} across the table. "
        "The green cube and the dark block remain stationary. "
        "Keep the camera fixed, preserve the tabletop, lighting, object colors and sizes. "
        "Continuous motion, no cuts, no added objects."
    ),
    "vision_path": str(args.image.resolve()),
    "format_prompt_as_json": False,
    "prompt_upsampling": False,
    "num_frames": 49,
    "fps": 24,
    "resolution": "480",
    "num_steps": 16,
}
args.output.write_text(json.dumps(manifest, indent=2) + "\n")
receipt = {
    "kind": "image-conditioned video generation; not a physics simulation or robot policy",
    "input_sha256": hashlib.sha256(args.image.read_bytes()).hexdigest(),
    "input_origin": "Our self-authored Isaac Sim Replicator workbench scene, frame 05",
    "manifest": manifest,
}
args.output.with_suffix(".provenance.json").write_text(json.dumps(receipt, indent=2) + "\n")
