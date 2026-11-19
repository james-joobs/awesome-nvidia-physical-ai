#!/usr/bin/env bash
set -euo pipefail

task_root="${WORLD_DRIVING_ROOT:?Set WORLD_DRIVING_ROOT to the isolated GPU-machine folder}"
lab_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
direction="${1:-right}"
input_image="${2:-$lab_root/input/workbench.png}"
mkdir -p "$task_root/inputs" "$task_root/logs"
python3 "$lab_root/make_cosmos_input.py" --image "$input_image" \
  --output "$task_root/inputs/workbench-$direction.json" --direction "$direction"
export COSMOS_TRAINING=0
export PATH="$task_root/cosmos-framework/.venv/bin:$PATH"
cd "$task_root/cosmos-framework"
# Use the same lock for every other GPU job in this recording session.
flock /tmp/physical-ai-four-domains.gpu.lock \
  .venv/bin/python -m cosmos_framework.scripts.inference \
  -i "$task_root/inputs/workbench-$direction.json" \
  -o "$task_root/outputs/cosmos-$direction" \
  --checkpoint-path "$task_root/checkpoints/Cosmos3-Edge" \
  --parallelism-preset=latency --seed=19 \
  --no-use-torch-compile --no-guardrails
