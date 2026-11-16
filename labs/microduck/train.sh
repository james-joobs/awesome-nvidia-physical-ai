#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 1 ]]; then
  printf 'Usage: bash %s ISAAC_LAB_CHECKOUT\n' "$0" >&2
  exit 2
fi
cd "$1"
uv run --no-sync isaaclab train --rl_library rsl_rl \
  --task IsaacContrib-Velocity-Flat-MicroDuck --num_envs 512 --max_iterations 500 \
  --seed 17 --run_name showcase_microduck presets=backlash
