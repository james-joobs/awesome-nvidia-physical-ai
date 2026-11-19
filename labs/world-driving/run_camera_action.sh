#!/usr/bin/env bash
set -euo pipefail
task_root="${WORLD_DRIVING_ROOT:?Set WORLD_DRIVING_ROOT to the isolated GPU-machine folder}"
lab_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$lab_root/make_camera_action_input.py" --image "$lab_root/input/workbench.png" \
  --output "$task_root/inputs/workbench-camera-actions.json"
export COSMOS_TRAINING=0
export PATH="$task_root/cosmos-framework/.venv/bin:$PATH"
cd "$task_root/cosmos-framework"
flock /tmp/physical-ai-four-domains.gpu.lock \
  .venv/bin/python -m cosmos_framework.scripts.inference \
  -i "$task_root/inputs/workbench-camera-actions.json" \
  -o "$task_root/outputs/cosmos-camera-actions" \
  --checkpoint-path "$task_root/checkpoints/Cosmos3-Edge" \
  --parallelism-preset=latency --seed=19 \
  --no-use-torch-compile --no-guardrails
