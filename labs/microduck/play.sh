#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 2 ]]; then
  printf 'Usage: bash %s ISAAC_LAB_CHECKOUT CHECKPOINT_PT\n' "$0" >&2
  exit 2
fi
checkpoint="$(cd "$(dirname "$2")" && pwd -P)/$(basename "$2")"
test -s "$checkpoint"
cd "$1"
uv run --no-sync isaaclab play --rl_library rsl_rl \
  --task IsaacContrib-Velocity-Flat-MicroDuck --checkpoint "$checkpoint" --num_envs 4 \
  --viz newton_gl presets=backlash 'env.viewer.eye=[2.1,-2.3,1.35]' 'env.viewer.lookat=[0,0,0.24]'
