#!/usr/bin/env bash
set -euo pipefail
task_root="${WORLD_DRIVING_ROOT:?Set WORLD_DRIVING_ROOT to the isolated GPU-machine folder}"
lab_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
test -f "$task_root/inputs/synthetic-intersection/input.json"
mkdir -p "$task_root/outputs/alpamayo-synthetic"
flock /tmp/physical-ai-four-domains.gpu.lock \
  "$task_root/alpamayo2-edge/.venv/bin/python" "$lab_root/run_alpamayo_synthetic.py" \
  --input "$task_root/inputs/synthetic-intersection" \
  --model "$task_root/checkpoints/Alpamayo2-Edge" \
  --output "$task_root/outputs/alpamayo-synthetic"
