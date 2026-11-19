#!/usr/bin/env python3
"""Small, dependency-free process harness for real Physical AI lab scripts."""

import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


class LabError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise LabError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_once(path, value):
    # Exclusive creation prevents a later run from silently replacing evidence.
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def registry(root):
    data = read_json(root / "labs/scenarios.json")
    return {item["id"]: item for item in data["scenarios"]}


def executable(value):
    found = shutil.which(value)
    # Preserve a venv's Python symlink: resolving it would select the base env.
    return str(Path(found).absolute()) if found else value


def command_for(item, args, root, output):
    if item["status"] != "runnable":
        raise LabError("This recipe requires manual setup: " + "; ".join(item["prerequisites"]))
    if args.headless and not item.get("headless_args"):
        raise LabError("This scenario does not support --headless")
    values = {"python": executable(args.python), "ffmpeg": executable(args.ffmpeg),
              "root": str(root), "output": str(output), "seed": str(args.seed)}
    for name in item.get("required_paths", {}):
        value = getattr(args, name, None)
        require(value is not None, "--" + name + " is required for " + item["id"])
        values[name] = str(Path(value).expanduser().resolve())
    command = [part.format_map(values) for part in item["command"]]
    if args.no_guardrails:
        require(item.get("validator") == "cosmos", "--no-guardrails is supported only by cosmos-i2v")
        command.append("--no-guardrails")
    return command + (item.get("headless_args", []) if args.headless else [])


def doctor(item, args, root):
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    python = executable(args.python)
    check("python", bool(shutil.which(python)), python)
    for relative in ["labs/scenarios.json", *item.get("sources", [])]:
        path = root / relative
        check("source:" + relative, path.is_file(), str(path))
    if item["status"] != "runnable":
        check("recipe", False, item["prerequisites"])
        return {"scenario": item["id"], "ready": False, "checks": checks}
    for name, definition in item.get("required_paths", {}).items():
        value = getattr(args, name, None)
        path = Path(value).expanduser().resolve() if value else None
        ok = path is not None and (path.is_dir() if definition["kind"] == "directory" else path.is_file())
        check("argument:" + name, ok, str(path) if path else "Supply --" + name)
        for relative in definition.get("files", []):
            check(name + ":" + relative, bool(path and (path / relative).is_file()), str(path / relative) if path else "missing --" + name)
        if name == "model" and path and path.is_dir():
            shards = [p for p in path.rglob("*") if p.is_file() and p.suffix in (".safetensors", ".pt", ".bin")]
            check("model:checkpoint-files", bool(shards) and all(p.stat().st_size > 0 for p in shards), "Checkpoint files must exist and be nonempty")
            index = path / "model.safetensors.index.json"
            if index.is_file():
                try:
                    names = set(read_json(index).get("weight_map", {}).values())
                    if names:
                        check("model:index-shards", all((path / name).is_file() for name in names), "Every indexed shard must exist")
                except (OSError, ValueError, TypeError) as exc:
                    check("model:index-shards", False, str(exc))
    if item.get("validator") == "cosmos":
        search = str(Path(python).parent) + os.pathsep + os.environ.get("PATH", "")
        check("uv", bool(shutil.which("uv", path=search)), "Required by upstream Cosmos subprocesses")
    if item.get("required_paths") and all(getattr(args, name, None) for name in item["required_paths"]):
        try:
            for path in input_files(item, args):
                check("input-file:" + str(path), path.is_file(), "JSON manifest or referenced image")
        except (OSError, ValueError, KeyError, TypeError, LabError) as exc:
            check("input-manifest", False, str(exc))
    try:
        probe = subprocess.run([python, "-c",
            "import importlib.util,json,sys; print(json.dumps({m:importlib.util.find_spec(m) is not None for m in sys.argv[1:]}))",
            *item.get("modules", [])], capture_output=True, text=True, timeout=30,
            cwd=Path(args.backend).expanduser().resolve() if getattr(args, "backend", None) and Path(args.backend).expanduser().is_dir() else None)
        modules = json.loads(probe.stdout) if probe.returncode == 0 else {}
        for module in item.get("modules", []):
            check("module:" + module, modules.get(module, False), "checked with " + python)
        check("python-probe", probe.returncode == 0, probe.stderr[-1500:])
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        check("python-probe", False, str(exc))
    if item.get("gpu"):
        try:
            gpu = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=15)
            check("gpu", gpu.returncode == 0 and bool(gpu.stdout.strip()), (gpu.stdout + gpu.stderr)[-2000:])
        except (OSError, subprocess.TimeoutExpired) as exc:
            check("gpu", False, str(exc))
    display = item.get("display") and not args.headless
    if display:
        check("DISPLAY", bool(os.environ.get("DISPLAY")), os.environ.get("DISPLAY", "not set"))
    if item.get("ffmpeg"):
        check("ffmpeg", bool(shutil.which(args.ffmpeg)), executable(args.ffmpeg))
        check("xwininfo", bool(shutil.which("xwininfo")), "X11 window discovery")
    return {"scenario": item["id"], "ready": all(c["ok"] for c in checks), "checks": checks}


def input_files(item, args):
    """The supported manifests reference local files; record the actual images too."""
    if "input" not in item.get("required_paths", {}):
        return []
    supplied = Path(args.input).expanduser().resolve()
    manifest = supplied / "input.json" if supplied.is_dir() else supplied
    data = read_json(manifest)
    paths = [manifest]
    if item["validator"] == "cosmos":
        require(isinstance(data.get("vision_path"), str), "Cosmos input requires a local vision_path")
        image = Path(data["vision_path"]).expanduser()
        paths.append(image.resolve() if image.is_absolute() else (manifest.parent / image).resolve())
    elif item["validator"] == "alpamayo":
        require(isinstance(data.get("shots"), list) and data["shots"], "Alpamayo input requires camera shots")
        paths.extend((manifest.parent / row["image"]).resolve() for row in data["shots"])
    return sorted(set(paths))


def resource_info(item, args):
    if not item.get("required_paths"):
        return {}
    result = {"seed": args.seed, "inputs": [],
              "cosmos_guardrails": "disabled explicitly" if args.no_guardrails else "upstream default retained"}
    try:
        result["inputs"] = [{"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}
                            for path in input_files(item, args) if path.is_file()]
    except (OSError, ValueError, KeyError, TypeError, LabError) as exc:
        result["input_error"] = str(exc)
    model = Path(args.model).expanduser().resolve()
    metadata_names = {"config.json", "model_index.json", "model.safetensors.index.json", "LICENSE", "README.md"}
    metadata = [{"path": path.relative_to(model).as_posix(), "sha256": digest(path)}
                for path in sorted(model.iterdir()) if path.is_file() and path.name in metadata_names] if model.is_dir() else []
    revisions = set()
    if (model / ".cache/huggingface/download").is_dir():
        for path in (model / ".cache/huggingface/download").rglob("*.metadata"):
            lines = path.read_text().splitlines()
            if lines and len(lines[0]) == 40 and set(lines[0].lower()) <= set("0123456789abcdef"):
                revisions.add(lines[0])
    result["model"] = {"path": str(model), "declared_reference": item.get("model_reference"),
                       "observed_huggingface_revisions": sorted(revisions), "metadata": metadata,
                       "checkpoint_files": [{"path": path.relative_to(model).as_posix(), "bytes": path.stat().st_size}
                                            for path in sorted(model.rglob("*")) if path.is_file() and path.suffix in (".safetensors", ".pt", ".bin")],
                       "hash_scope": "Input files and model metadata are hashed; checkpoint shards are listed by size, not hashed."}
    if getattr(args, "backend", None):
        backend = Path(args.backend).expanduser().resolve()
        revision = subprocess.run(["git", "-C", str(backend), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        result["backend"] = {"path": str(backend), "git_revision": revision.stdout.strip() if revision.returncode == 0 else None}
    return result


def artifacts(output):
    result = []
    for path in sorted(output.rglob("*")):
        if path.is_symlink():
            raise LabError("Symlink artifacts are not supported: " + str(path))
        if path.is_file() and path.name not in {"run.json", "RUNNING"}:
            result.append({"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size,
                           "sha256": digest(path)})
    return result


def require(condition, message):
    if not condition:
        raise LabError(message)


def finite_list(values, count=None):
    return (isinstance(values, list) and (count is None or len(values) == count)
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in values))


def npy_array(data):
    """Read only the simple float arrays this lab writes, without NumPy."""
    require(data[:6] == b"\x93NUMPY", "Invalid NPY artifact")
    version = data[6]
    require(version in (1, 2, 3), "Unsupported NPY version")
    width = 2 if version == 1 else 4
    offset = 8 + width
    length = int.from_bytes(data[8:offset], "little")
    header = ast.literal_eval(data[offset:offset + length].decode("latin1"))
    dtype = header["descr"]
    require(not header["fortran_order"] and dtype in ("<f4", "<f8", "=f4", "=f8", "|f4", "|f8"), "Unsupported NPY layout")
    shape = header["shape"]
    values = [v[0] for v in struct.iter_unpack("<f" if dtype.endswith("4") else "<d", data[offset + length:])]
    require(len(values) == math.prod(shape) and finite_list(values), "Invalid/nonfinite NPY data")
    return shape, values


def validate(output, item, headless=False):
    require(not (output / "capture-failed").exists(), "Native GUI capture reported capture-failed")
    validator = item["validator"]
    if validator == "cosmos":
        receipts = sorted(output.rglob("sample_outputs.json"))
        require(bool(receipts), "No Cosmos sample_outputs.json receipt")
        products = []
        for path in receipts:
            receipt = read_json(path)
            require(receipt.get("status") == "success", "Cosmos sample failed: " + str(receipt.get("message")))
            movies = sorted(path.parent.glob("*.mp4"))
            require(bool(movies), "Successful Cosmos receipt has no local MP4")
            for movie in movies:
                require(movie.stat().st_size > 1000, "Empty/truncated Cosmos MP4")
                with movie.open("rb") as stream:
                    require(b"ftyp" in stream.read(64), "Cosmos output is not an MP4 container")
                products.append({"file": movie.relative_to(output).as_posix(), "frames_requested": receipt.get("args", {}).get("num_frames"),
                                 "fps_requested": receipt.get("args", {}).get("fps")})
        return {"passed": True, "checks": ["official success receipt", "local nonempty MP4 container"], "products": products,
                "scope": "Video generation completion only. Prompt adherence, physical accuracy and motion quality require separate visual review."}
    if validator == "alpamayo":
        receipt = read_json(output / "receipt.json")
        require("interface" in receipt.get("scope", "").lower() and "synthetic" in receipt.get("scope", "").lower(),
                "Alpamayo receipt must identify a synthetic interface test")
        record = receipt.get("result", {})
        shapes = {"pred_xyz": [1, 1, 1, 64, 3], "pred_rot": [1, 1, 1, 64, 3, 3]}
        require(record.get("finite") is True, "Alpamayo output is not finite")
        tensors = sorted(output.rglob("output.safetensors"))
        require(len(tensors) == 1, "Expected one Alpamayo output.safetensors artifact")
        with tensors[0].open("rb") as stream:
            length_bytes = stream.read(8)
            require(len(length_bytes) == 8, "Truncated safetensors header")
            length = struct.unpack("<Q", length_bytes)[0]
            require(length < 1_000_000, "Unexpectedly large safetensors header")
            header = json.loads(stream.read(length))
            numeric = stream.read()
        for name, shape in shapes.items():
            require(record.get(name + "_shape") == shape, "Unexpected Alpamayo reported shape: " + name)
            tensor = header[name]
            require(tensor["shape"] == shape and tensor["dtype"] == "F32", "Unexpected saved tensor shape/dtype: " + name)
            begin, end = tensor["data_offsets"]
            values = [entry[0] for entry in struct.iter_unpack("<f", numeric[begin:end])]
            require(len(values) == math.prod(shape) and finite_list(values), "Nonfinite/incomplete Alpamayo tensor: " + name)
        return {"passed": True, "checks": ["synthetic interface receipt", "expected finite trajectory tensors"],
                "scope": "Real model inference on self-authored synthetic observations; not a driving benchmark, safety assessment or closed-loop driving.",
                "model_id": receipt.get("model_id"), "model_revision": receipt.get("model_revision"), "shapes": shapes}
    if validator in ("friction", "bounce"):
        capture = read_json(output / "capture.json")
        takes = capture.get("takes", [])
        take = next((t for t in takes if t.get("file") == validator + ".mp4"), None)
        require(take is not None and take.get("scene") == validator + "-live", "Expected live-physics take missing")
        movie = output / (validator + ".mp4")
        require(movie.is_file() and movie.stat().st_size > 50_000, "Missing/truncated GUI movie")
        with movie.open("rb") as stream:
            require(b"ftyp" in stream.read(64), "Movie is not an MP4 container")
        physics = read_json(output / (validator + ".physics.json"))
        samples, summary = physics["samples"], physics["summary"]
        require(len(samples) > 30 and all(len(sample["positions_m"]) == 3 and
                all(finite_list(p, 3) for p in sample["positions_m"]) for sample in samples), "Invalid physics samples")
        require(take.get("live_physx") == summary, "Capture summary and physics summary disagree")
        if validator == "friction":
            distances = summary.get("distances_m")
            require(finite_list(distances, 3) and distances[0] > distances[1] + .10 > distances[2] + .17 and distances[2] > .035,
                    "Friction distance ordering failed")
            require(all(abs(distances[i] - (samples[-1]["positions_m"][i][0] + .80)) < 1e-6 for i in range(3)),
                    "Friction summary does not match sampled positions")
        else:
            heights = summary.get("peak_center_z_m_after_initial_contact")
            require(finite_list(heights, 3) and heights[1] > heights[0] + .09 and heights[2] > heights[1] + .18,
                    "Bounce-height ordering failed")
            for i in range(3):
                sampled = [sample["positions_m"][i][2] for sample in samples]
                contact = next((j for j, z in enumerate(sampled) if z < .945), None)
                require(contact is not None and len(sampled) > contact + 2, "No contact/rebound samples")
                require(abs(heights[i] - max(sampled[contact + 2:])) < 1e-6, "Bounce summary does not match sampled positions")
        return {"passed": True, "checks": ["native GUI movie", "live PhysX samples", "physical ordering"], "summary": summary}
    report = read_json(output / "result.json")
    if validator == "newton":
        cases = report.get("cases", [])
        require(report.get("recording_mode") == "solver-usd-replay" and len(cases) == 3, "Newton material cases incomplete")
        require({case["case"] for case in cases} == {"cloth-xpbd", "cloth-vbd", "cable-twist"}, "Unexpected Newton cases")
        for case in cases:
            require(case.get("official_tests_passed") is True, "Official Newton test did not pass")
            for relative in (case["case"] + ".usd", case["review_scene"]):
                path = output / relative
                require(path.is_file() and path.stat().st_size > 0, "Missing Newton USD: " + relative)
            require(case.get("simulated_seconds", 0) > 0 and case.get("animated_arrays"), "No Newton animation evidence")
        return {"passed": True, "checks": ["three official example tests", "nonempty solver and review USD", "animation inspection"],
                "limitation": "USD contains saved Newton solver states; later Isaac Sim display is a replay.", "summary": report}
    if validator == "warp":
        require(report.get("frames") == 200 and report.get("particles", 0) > 0, "Warp did not finish 200 frames")
        distance = report.get("mean_particle_displacement_m")
        require(isinstance(distance, (int, float)) and math.isfinite(distance) and distance > 0, "No finite particle motion")
        require(report.get("displayed_particles", 0) == 0 if headless else report.get("displayed_particles", 0) > 0,
                "Warp viewer/headless output disagrees")
        return {"passed": True, "checks": ["200 frames", "finite positive particle displacement", "viewer mode"], "summary": report}
    require(validator == "curobo", "Unknown scenario validator")
    require(report.get("same_start_and_goal") is True and report.get("baseline_tool_enters_new_obstacle") is True
            and report.get("replanned_tool_enters_obstacle") is False, "cuRobo comparison failed")
    with zipfile.ZipFile(output / "motion.npz") as archive:
        arrays = {name: npy_array(archive.read(name + ".npy"))
                  for name in ("baseline_tool", "obstacle_tool", "baseline_q", "obstacle_q")}
    for name, (shape, _) in arrays.items():
        require(len(shape) == 2 and shape[0] > 1 and shape[1] == (3 if name.endswith("tool") else 7), "Unexpected trajectory shape: " + name)
    before, after = arrays["baseline_tool"][1], arrays["obstacle_tool"][1]
    require(all(abs(a - b) < .01 for a, b in zip(before[-3:], after[-3:])), "Replanned tool goal differs")
    require(all(abs(a - b) < .001 for a, b in zip(arrays["baseline_q"][1][:7], arrays["obstacle_q"][1][:7])), "Replanned start differs")
    center, dims = report["obstacle_center_m"], report["obstacle_dimensions_m"]
    require(finite_list(center, 3) and finite_list(dims, 3) and all(x > 0 for x in dims), "Invalid obstacle")

    def intersects(values):
        return any(all(abs(values[i + j] - center[j]) < dims[j] / 2 for j in range(3)) for i in range(0, len(values), 3))

    require(intersects(before) and not intersects(after), "Tool trajectories do not match obstacle claim")
    return {"passed": True, "checks": ["finite trajectory arrays", "same start and tool goal", "sampled tool avoids obstacle"],
            "limitation": "Tool-center samples are checked here; complete swept robot collision validation belongs to cuRobo.", "summary": report}


def run(item, args, root):
    output = Path(args.output).expanduser().resolve()
    command = command_for(item, args, root, output)
    preflight = doctor(item, args, root)
    mode = item.get("headless_evidence_mode", item["evidence_mode"]) if args.headless else item["evidence_mode"]
    if args.dry_run:
        return {"status": "planned", "scenario": item["id"], "command": command, "cwd": str(root),
                "evidence_mode": mode, "output": str(output), "preflight": preflight, "writes": False}, 0
    require(not output.exists(), "Output already exists; choose a new run directory: " + str(output))
    output.mkdir(parents=True)
    started = now()
    sources = [{"path": relative, "sha256": digest(root / relative) if (root / relative).is_file() else None}
               for relative in ["labs/cli.py", "labs/scenarios.json", *item["sources"]]]
    request = {"schema_version": 1, "scenario": item, "command": command, "cwd": str(root), "source_hashes": sources,
               "resources": resource_info(item, args),
               "started_at": started, "evidence_mode": mode, "headless": args.headless, "preflight": preflight}
    write_once(output / "request.json", request)
    (output / "RUNNING").touch(exist_ok=False)
    status, returncode, validation, error = "failed", None, {"passed": False}, None
    try:
        require(preflight["ready"], "Preflight failed; inspect run.json preflight checks")
        with (output / "run.log").open("x", encoding="utf-8") as log:
            process = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT, check=False)
        returncode = process.returncode
        require(returncode == 0, "Scenario process exited with code " + str(returncode))
        validation = validate(output, item, args.headless)
        status = "passed"
    except KeyboardInterrupt:
        error = "Interrupted by user"
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)
    finally:
        (output / "RUNNING").unlink(missing_ok=True)
        manifest = {**request, "status": status, "finished_at": now(), "process_returncode": returncode,
                    "validation": validation, "error": error, "artifacts": artifacts(output)}
        write_once(output / "run.json", manifest)
    return {"status": status, "scenario": item["id"], "run": str(output), "manifest": str(output / "run.json"),
            "evidence_mode": mode, "validation": validation, "error": error}, 0 if status == "passed" else 1


def verify(output):
    manifest = read_json(output / "run.json")
    require(manifest["status"] == "passed", "Run did not pass: " + str(manifest.get("error")))
    require(not (output / "RUNNING").exists(), "Run is still marked RUNNING")
    require(artifacts(output) == manifest["artifacts"], "Artifact list/size/SHA-256 changed since completion")
    validation = validate(output, manifest["scenario"], manifest.get("headless", False))
    return {"status": "verified", "run": str(output), "evidence_mode": manifest["evidence_mode"],
            "artifacts": len(manifest["artifacts"]), "validation": validation}


def parser():
    result = Parser(description=__doc__)
    result.add_argument("--json", action="store_true", help="Write one JSON object to stdout; child output goes to run.log")
    commands = result.add_subparsers(dest="action", required=True, parser_class=Parser)
    for name in ("list", "doctor", "run", "verify", "preview"):
        sub = commands.add_parser(name)
        sub.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
        if name in ("verify", "preview"):
            sub.add_argument("run", type=Path)
        else:
            sub.add_argument("--source", type=Path, default=ROOT, help="Repository checkout root")
        if name in ("doctor", "run"):
            sub.add_argument("scenario")
            sub.add_argument("--python", default=os.environ.get("PHYSICAL_AI_PYTHON", sys.executable))
            sub.add_argument("--ffmpeg", default=os.environ.get("PHYSICAL_AI_FFMPEG", "ffmpeg"))
            sub.add_argument("--headless", action="store_true", help="Supported by warp-dem only")
            sub.add_argument("--input", type=Path, help="Scenario input JSON or input directory")
            sub.add_argument("--model", type=Path, help="Local model checkpoint directory")
            sub.add_argument("--backend", type=Path, help="Prepared backend source checkout (Cosmos)")
            sub.add_argument("--seed", type=int, default=19, help="Model sampling seed (default: 19)")
            sub.add_argument("--no-guardrails", action="store_true", help="Cosmos only: explicitly disable upstream content filters")
        if name == "run":
            sub.add_argument("--output", required=True)
            sub.add_argument("--dry-run", action="store_true", help="Inspect command and readiness without writing/executing the scenario")
    return result


def main():
    json_mode = "--json" in sys.argv[1:]
    try:
        args = parser().parse_args()
        code = 0
        if args.action in ("verify", "preview"):
            output = args.run.expanduser().resolve()
            if args.action == "verify":
                value = verify(output)
            else:
                manifest = read_json(output / "run.json")
                value = {"status": manifest["status"], "scenario": manifest["scenario"]["id"], "evidence_mode": manifest["evidence_mode"],
                         "validation": manifest["validation"], "error": manifest.get("error"),
                         "files": [{**item, "absolute_path": str(output / item["path"])} for item in manifest["artifacts"]],
                         "note": "Inspect-only preview; use verify to check integrity. No viewer or browser is launched."}
        else:
            root = args.source.expanduser().resolve()
            items = registry(root)
            if args.action == "list":
                value = {"scenarios": list(items.values())}
            else:
                require(args.scenario in items, "Unknown scenario: " + args.scenario)
                item = items[args.scenario]
                if args.action == "doctor":
                    require(not args.headless or item.get("headless_args"), "This scenario does not support --headless")
                    value = doctor(item, args, root)
                    code = 0 if value["ready"] else 1
                else:
                    value, code = run(item, args, root)
    except (LabError, OSError, ValueError, KeyError, zipfile.BadZipFile, struct.error) as exc:
        value, code = {"status": "error", "error": str(exc)}, 1
    if json_mode:
        print(json.dumps(value, ensure_ascii=False, allow_nan=False))
    elif "scenarios" in value:
        for item in value["scenarios"]:
            print(f"{item['id']:22} {item['status']:12} {item['title']}")
    else:
        print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
