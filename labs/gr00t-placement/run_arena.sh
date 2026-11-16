#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 3 || ! "$2" =~ ^(24|70)$ ]]; then
  printf 'Usage: bash %s ARENA_CHECKOUT 24|70 OUTPUT_DIRECTORY [ARENA_OVERRIDES...]\n' "$0" >&2
  exit 2
fi
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
config="$here/droid-${2}s.yaml"
mkdir -p "$3"
output="$(cd "$3" && pwd -P)"
cd "$1"
shift 3
# Start the official loopback GR00T server before running this script.
python -m isaaclab_arena.evaluation.experiment_runner --viz kit --record_camera_video \
  --experiment_config "$config" --experiment_output_directory "$output" "$@"
