"""Pair our simulator image with NVIDIA's pinned native camera-action example.

Use the published normalized sequence unchanged: inventing metric units or
normalizing this sequence a second time would change the input contract.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--image", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
revision = "2b17a2413bd86b2cf9b03823637108851e4ddf2d"
url = f"https://media.githubusercontent.com/media/nvidia-cosmos/cosmos-dependencies/{revision}/inputs/action/camera_action_44.json"
payload = subprocess.check_output(["curl", "-fsSL", "--max-time", "60", url])
digest = hashlib.sha256(payload).hexdigest()
assert digest == "547b977ccd6d435d579ba83e82e58618d0bebf2e8e7d8d577bf2e9c8883c5595", digest
actions = json.loads(payload)
assert len(actions) == 60 and all(len(row) == 9 for row in actions)
assert all(math.isfinite(value) for row in actions for value in row)
action_path = args.output.with_name("camera-action-60x9.json")
action_path.write_bytes(payload)
spec = {
    "name": "workbench-camera-actions",
    "action_chunk_size": 60,
    "action_path": str(action_path.resolve()),
    "domain_name": "camera_pose",
    "fps": 30,
    "view_point": "ego_view",
    "guidance": 1.0,
    "image_size": 480,
    "resolution": "480",
    "model_mode": "forward_dynamics",
    "num_frames": 61,
    "num_steps": 30,
    "prompt": "A wooden workbench holds a yellow cube, a mint green cube and a tall dark block. The camera moves around the stationary objects.",
    "shift": 5.0,
    "vision_path": str(args.image.resolve()),
}
args.output.write_text(json.dumps(spec, indent=2) + "\n")
args.output.with_suffix(".provenance.json").write_text(json.dumps({
    "input_origin": "Our self-authored Isaac Sim Replicator workbench scene, frame 05",
    "action_origin": url,
    "action_sha256": digest,
    "action_shape": [60, 9],
    "action_columns": "native normalized camera-pose channels: 3 translation + 6D rotation; not raw metric displacements",
    "normalization": "Preserve NVIDIA's published values unchanged. Framework pads the native channels to its model action width.",
    "output": "Initial observation plus 60 predicted RGB frames; not a physics solver or a new 3D reconstruction",
}, indent=2) + "\n")
