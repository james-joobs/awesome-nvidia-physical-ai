"""Call an existing Cosmos backend, retaining its guardrails and exact arguments."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--backend", type=Path, required=True)
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--model", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--seed", type=int, default=19)
parser.add_argument("--no-guardrails", action="store_true", help="Explicitly disable upstream content filters")
args = parser.parse_args()
command = [sys.executable, "-m", "cosmos_framework.scripts.inference", "-i", str(args.input.resolve()),
           "-o", str(args.output.resolve()), "--checkpoint-path", str(args.model.resolve()),
           "--parallelism-preset=latency", "--seed", str(args.seed), "--no-use-torch-compile"]
if args.no_guardrails:
    command.append("--no-guardrails")
args.output.mkdir(parents=True, exist_ok=True)
environment = os.environ.copy()
environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
environment["COSMOS_TRAINING"] = "0"
with (args.output / "backend-command.json").open("x") as stream:
    json.dump({"command": command, "cwd": str(args.backend.resolve()),
               "guardrails": "disabled explicitly" if args.no_guardrails else "upstream default retained",
               "seed": args.seed, "python_bin_prepended_to_path": str(Path(sys.executable).parent)}, stream, indent=2)
    stream.write("\n")
raise SystemExit(subprocess.run(command, cwd=args.backend.resolve(), env=environment, check=False).returncode)
