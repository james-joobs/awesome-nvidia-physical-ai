#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 3 || ! "$2" =~ ^(24|70)$ ]]; then
  printf 'Usage: bash %s ARENA_CHECKOUT 24|70 OUTPUT_DIRECTORY [ARENA_OVERRIDES...]\n' "$0" >&2
  exit 2
fi
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
config="$here/droid-${2}s.yaml"
mkdir -p "$3"
export GR00T_GUI_OUTPUT="$(cd "$3" && pwd -P)"
export GR00T_GUI_FFMPEG="${GR00T_GUI_FFMPEG:-$(command -v ffmpeg)}"
if [[ ! -x "$GR00T_GUI_FFMPEG" ]]; then
  printf 'Set GR00T_GUI_FFMPEG to an executable ffmpeg binary.\n' >&2
  exit 2
fi
command -v xwininfo >/dev/null
: "${DISPLAY:?Run this from a Linux desktop session with DISPLAY set.}"
cd "$1"
shift 3
# Start the official loopback GR00T server separately before running this script.
"${GR00T_ARENA_PYTHON:-python}" -u "$here/record_gui.py" --viz kit --record_camera_video \
  --experiment_config "$config" --experiment_output_directory "$GR00T_GUI_OUTPUT/evaluation" "$@"
if [[ -e "$GR00T_GUI_OUTPUT/capture-failed" || ! -s "$GR00T_GUI_OUTPUT/capture.json" ]]; then
  printf 'The GUI run did not finish cleanly; keep the logs and inspect the failure.\n' >&2
  exit 1
fi
