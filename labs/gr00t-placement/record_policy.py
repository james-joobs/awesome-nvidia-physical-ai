"""Run the official GR00T policy and save one real observation/action per reset.

Set GR00T_MODEL_PATH to a prepared checkpoint and GR00T_POLICY_OUTPUT to the
output directory. No robot actions are synthesized by this recorder.
"""

import json
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image
import torch

from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.policy.gr00t_policy import Gr00tPolicy
from gr00t.policy.server_client import PolicyServer


output = Path(os.environ["GR00T_POLICY_OUTPUT"]).resolve()
output.mkdir(parents=True, exist_ok=True)
policy = Gr00tPolicy(
    embodiment_tag=EmbodimentTag.OXE_DROID,
    model_path=os.environ["GR00T_MODEL_PATH"],
    device="cuda",
    strict=True,
)
print(f"GR00T N1.6-DROID | torch {torch.__version__} | {torch.cuda.get_device_name(0)}", flush=True)
get_action = policy.get_action
reset = policy.reset
episode = 0
count = 0
saved = set()


def record_reset(*args, **kwargs):
    global episode
    response = reset(*args, **kwargs)
    episode += 1
    return response


def record_action(observation, options=None):
    global count
    started = time.perf_counter()
    action, info = get_action(observation, options)
    elapsed = 1000 * (time.perf_counter() - started)
    count += 1
    arrays = {key: np.asarray(values) for key, values in action.items()}
    if not all(np.isfinite(a).all() and a.size > 0 for a in arrays.values()):
        raise RuntimeError("GR00T returned an invalid action")
    if count <= 3 or count % 25 == 0:
        print(f"ACTION {count} | reset {episode} | {elapsed:.1f} ms | {list(action)}", flush=True)
    if episode not in saved:
        save_dir = output / f"request-{count:04d}"
        save_dir.mkdir(parents=True, exist_ok=True)
        cameras = {}
        for index, (name, values) in enumerate(observation.get("video", {}).items()):
            array = np.asarray(values)
            if array.ndim != 5 or array.shape[-1] != 3:
                continue
            frame = array[0, -1]
            if frame.dtype != np.uint8:
                frame = (frame * 255 if frame.max() <= 1.0 else frame).clip(0, 255).astype(np.uint8)
            filename = f"camera-{index + 1}.png"
            Image.fromarray(frame).save(save_dir / filename)
            cameras[name] = {"file": filename, "shape": list(array.shape)}
        record = {
            "model": "GR00T N1.6-DROID",
            "observation_origin": "Isaac Lab-Arena DROID simulator",
            "request": count,
            "server_reset_count": episode,
            "instruction": observation.get("language", {}),
            "cameras": cameras,
            "observed_state": {k: np.asarray(v).tolist() for k, v in observation.get("state", {}).items()},
            "actions": {k: v.tolist() for k, v in arrays.items()},
            "action_shapes": {k: list(v.shape) for k, v in arrays.items()},
            "server_inference_ms": round(elapsed, 2),
        }
        (save_dir / "observation-action.json").write_text(json.dumps(
            record, indent=2, default=lambda value: np.asarray(value).tolist()) + "\n")
        saved.add(episode)
    return action, info


policy.get_action = record_action
policy.reset = record_reset
PolicyServer(policy, host="127.0.0.1", port=int(os.environ.get("GR00T_POLICY_PORT", "5555"))).run()
