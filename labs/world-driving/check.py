"""Check saved model products on a CPU, without importing either model runtime."""

import argparse
import json
import math
from pathlib import Path
import struct
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--cosmos", type=Path, help="Folder containing sample_outputs.json and vision.mp4")
parser.add_argument("--alpamayo", type=Path, help="Folder containing output.json and output.safetensors")
parser.add_argument("--ffmpeg", default="ffmpeg")
parser.add_argument("--ffprobe", default="ffprobe")
args = parser.parse_args()
if not args.cosmos and not args.alpamayo:
    parser.error("Choose --cosmos, --alpamayo, or both")
checks = {}
if args.cosmos:
    receipt = json.loads((args.cosmos / "sample_outputs.json").read_text())
    assert receipt["status"] == "success", receipt.get("message")
    probe = json.loads(subprocess.check_output([
        args.ffprobe, "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames", "-of", "json",
        str(args.cosmos / "vision.mp4"),
    ], text=True))["streams"][0]
    assert int(probe["nb_read_frames"]) == receipt["args"]["num_frames"], probe
    numerator, denominator = map(int, probe["r_frame_rate"].split("/"))
    assert abs(numerator / denominator - receipt["args"]["fps"]) < 1e-6, probe
    subprocess.run([args.ffmpeg, "-v", "error", "-xerror", "-i", str(args.cosmos / "vision.mp4"),
                    "-f", "null", "-"], check=True)
    checks["cosmos"] = {"decoded_video": probe,
                        "scope": "generation completed; prompt adherence still requires visual review"}
if args.alpamayo:
    record = json.loads((args.alpamayo / "output.json").read_text())
    expected_shapes = {"pred_xyz": [1, 1, 1, 64, 3], "pred_rot": [1, 1, 1, 64, 3, 3]}
    content = (args.alpamayo / "output.safetensors").read_bytes()
    header_length = struct.unpack("<Q", content[:8])[0]
    header = json.loads(content[8:8 + header_length])
    numeric = content[8 + header_length:]
    for name, shape in expected_shapes.items():
        tensor = header[name]
        assert tensor["shape"] == shape and tensor["dtype"] == "F32", (name, tensor)
        begin, end = tensor["data_offsets"]
        values = [entry[0] for entry in struct.iter_unpack("<f", numeric[begin:end])]
        assert len(values) == math.prod(shape) and all(map(math.isfinite, values)), name
    assert record["finite"] is True
    assert record["pred_xyz_shape"] == expected_shapes["pred_xyz"]
    assert record["pred_rot_shape"] == expected_shapes["pred_rot"]
    checks["alpamayo"] = {"finite_saved_trajectories": True, "shapes": expected_shapes,
                          "scope": "model interface smoke on synthetic observations; not driving evaluation"}
print(json.dumps(checks, indent=2))
