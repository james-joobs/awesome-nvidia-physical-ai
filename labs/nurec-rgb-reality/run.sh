#!/usr/bin/env bash
set -euo pipefail
lab="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd -- "$lab/../.." && pwd)"
root="${NUREC_RGB_ROOT:?Set NUREC_RGB_ROOT to a fresh output folder}"
mkdir -p "$root/runtime-home"
root="$(cd -- "$root" && pwd)"
image="nvcr.io/nvidia/nre/nre-ga:26.04@sha256:97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284"
base=(docker run --rm --gpus device=0 --network none --shm-size=8g --user "$(id -u):$(id -g)" -v "$root:/work" -v "$lab:/lab:ro" -e NUREC_RGB_ROOT=/work -e HOME=/work/runtime-home)
cpu_python="${RGB_SFM_PYTHON:-python3}"
lock="${GPU_LOCK:-/tmp/rgb-reality-view.gpu.lock}"
case "${1:-help}" in
 export-rgb) "${RGB_SFM_PYTHON:?Point RGB_SFM_PYTHON to the RGB lab SfM environment Python}" "$lab/export_rgb.py" --rgb-root "${RGB_VIEW_ROOT:?Set RGB_VIEW_ROOT to the completed RGB reconstruction folder}" --output "$root" ;;
 prepare) flock "$lock" "${base[@]}" "$image" run-script /lab/prepare_ncore.py ;;
 train) flock "$lock" "${base[@]}" -v "$lab/scene.yaml:/app/run.runfiles/_main/configs/nurec-rgb.yaml:ro" "$image" main --config-name nurec-rgb.yaml 2>&1 | tee "$root/nurec-train.log" ;;
 collect) "$cpu_python" "$lab/collect_result.py" --root "$root" ;;
 render)
  "$cpu_python" "$lab/make_views.py" --root "$root"
  artifact="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["artifact"])' "$root/nurec-result.json")"
  for view in front quarter orbit; do
   flock "$lock" "${base[@]}" "$image" render --artifact-path "/work/$artifact" --output-dir "/work/renders/$view" --camera-id front_camera --height 576 --renderer gsplat --custom-rig-trajectory "/work/rig-$view.json" --no-replicate-training-views --calib-source training-rig-poses --save-workers 2
  done ;;
 export-ply) flock "$lock" "${base[@]}" -v "$root/resolved-export.yaml:/app/run.runfiles/_main/configs/resolved-nurec-rgb.yaml:ro" "$image" export-gaussian-plys --config-name resolved-nurec-rgb.yaml --checkpoint-name last.ckpt --output-dir /work/gaussians ;;
 enhance)
  weights="${HARMONIZER_WEIGHTS:?Set HARMONIZER_WEIGHTS to the official checkpoint directory}"
  flock "$lock" "${base[@]}" -v "$weights:/work/checkpoints/Harmonizer:ro" "$image" run-script /lab/enhance.py ;;
 *) printf '%s\n' 'Choose export-rgb, prepare or train. See the bilingual guide.'; exit 2 ;;
esac
