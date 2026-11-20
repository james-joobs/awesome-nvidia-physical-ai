#!/usr/bin/env bash
# Start an isolated Isaac Sim 6.2 container. ACCEPT_EULA must be supplied by the user.
set -euo pipefail
: "${ACCEPT_EULA:?Set ACCEPT_EULA=Y only after accepting the NVIDIA Omniverse agreement.}"
[[ "$ACCEPT_EULA" == Y ]] || { echo "ACCEPT_EULA must be Y after your own acceptance." >&2; exit 1; }
worldgen_lab_root="$(cd "$(dirname "$0")" && pwd)"
worldgen_data_root="${WORLDGEN_DATA_ROOT:-$worldgen_lab_root}"
mkdir -p "$worldgen_data_root/cache"
worldgen_scenario="${1:-gate}"
shift || true
worldgen_xauth="${XAUTHORITY:-/run/user/$(id -u)/gdm/Xauthority}"
worldgen_display="${DISPLAY:-:1}"
worldgen_desktop_args=()
worldgen_headless=false
for worldgen_arg in "$@"; do
 [[ "$worldgen_arg" == --headless ]] && worldgen_headless=true
done
if ! "$worldgen_headless"; then
 [[ -f "$worldgen_xauth" ]] || { echo "Set XAUTHORITY to your X11 desktop authority file for GUI use." >&2; exit 1; }
 worldgen_desktop_args=(-e "DISPLAY=$worldgen_display" -e XAUTHORITY=/tmp/isaac-xauthority
  -v "$worldgen_xauth:/tmp/isaac-xauthority:ro" -v /tmp/.X11-unix:/tmp/.X11-unix:rw)
fi
exec docker run --rm --user 0:0 --gpus all --shm-size=2g \
 -e ACCEPT_EULA="$ACCEPT_EULA" -e PRIVACY_CONSENT=N -e NVIDIA_DRIVER_CAPABILITIES=all \
 "${worldgen_desktop_args[@]}" \
 -v "$worldgen_data_root/cache:/root/.cache:rw" \
 -v "$worldgen_lab_root:/lab:ro" -v "$worldgen_data_root:/work:rw" \
 --entrypoint /isaac-sim/python.sh nvcr.io/nvidia/isaac-sim:6.2.0 \
 /lab/run.py --assets /work/assets --output "/work/$worldgen_scenario" --scenario "$worldgen_scenario" \
 --allow-root --/omni/client/omniverse/use_omnihub=false --/renderer/multiGpu/enabled=false --/rtx/hydra/supportMultiTickRate=false "$@"
