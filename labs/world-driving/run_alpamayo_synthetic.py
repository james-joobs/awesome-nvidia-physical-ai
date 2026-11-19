"""Use released Alpamayo2-Edge weights on self-authored Isaac Sim camera frames.

This checks the model interface and output shapes, not driving quality or safety.
"""

import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import subprocess
import time

import numpy as np
from PIL import Image
import torch

from alpamayo2_edge.checkpoint import load_model
from alpamayo2_edge.inference import run_data

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--model", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--nav-text", default="Continue straight through the intersection.")
parser.add_argument("--seed", type=int, default=43)
args = parser.parse_args()
pins = json.loads(Path(__file__).with_name("model-pins.json").read_text())["alpamayo"]
weight_digests = {}
for filename, expected in pins["weight_sha256"].items():
    digest = hashlib.sha256()
    with (args.model / filename).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    weight_digests[filename] = digest.hexdigest()
    if digest.hexdigest() != expected:
        raise ValueError(f"Checkpoint shard {filename} differs from the documented model revision")
manifest = json.loads((args.input / "input.json").read_text())
images = np.stack([np.asarray(Image.open(args.input / row["image"]).convert("RGB"))
                   for row in manifest["shots"]])
data = {
    "image_frames": torch.from_numpy(images).permute(0, 3, 1, 2).unsqueeze(1).contiguous(),
    "camera_indices": torch.tensor([row["camera_id"] for row in manifest["shots"]], dtype=torch.int64),
    "absolute_timestamps": torch.tensor([row["timestamp_us"] for row in manifest["shots"]], dtype=torch.int64),
    "ego_history_xyz": torch.tensor([manifest["history_xyz_m"]], dtype=torch.float32),
    "ego_history_rot": torch.eye(3).reshape(1, 1, 3, 3).repeat(1, 20, 1, 1),
    "nav_text": [args.nav_text],
}
args.output.mkdir(parents=True, exist_ok=True)
began = time.perf_counter()
torch.cuda.reset_peak_memory_stats()
model, loading_info = load_model(str(args.model.resolve()), device="cuda", dtype="bfloat16",
                                attn_implementation="sdpa", local_files_only=True)
settings = dict(seed=args.seed, top_p=.98, top_k=None, temperature=.6, num_traj_sets=1,
                num_traj_samples=1, max_generation_length=192,
                diffusion_kwargs={"inference_step": 10})
result = run_data(model, data, "isaac-synthetic-intersection", args.output, settings, "cuda")
receipt = {
    "scope": "actual Alpamayo2-Edge model inference on a self-authored synthetic interface test; not driving evaluation",
    "upstream_source": "https://github.com/NVlabs/alpamayo2-edge",
    "upstream_revision": "02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e",
    "model_id": "nvidia/Alpamayo2-Edge",
    "model_revision": "b92b6aa326bd3e2235db28f248ad5a30b5890e64",
    "verified_weight_sha256": weight_digests,
    "gpu": torch.cuda.get_device_name(0),
    "peak_allocated_gib": torch.cuda.max_memory_allocated() / 2**30,
    "total_elapsed_s": time.perf_counter() - began,
    "versions": {key: version(key) for key in ("torch", "torchvision", "transformers", "safetensors")},
    "input_shapes": {key: list(value.shape) for key, value in data.items() if isinstance(value, torch.Tensor)},
    "navigation": args.nav_text,
    "seed": args.seed,
    "result": result,
}
(args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt), flush=True)
