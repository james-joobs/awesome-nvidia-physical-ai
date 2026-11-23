#!/usr/bin/env bash
set -euo pipefail
lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$lab_dir/../.." && pwd)"
task_root="${REALITY_VIEW_ROOT:?Set REALITY_VIEW_ROOT to an isolated output folder}"
mkdir -p "$task_root/runtime-home"
task_root="$(cd -- "$task_root" && pwd)"
image="nvcr.io/nvidia/nre/nre-ga:26.04@sha256:97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284"
base=(docker run --rm --gpus all --shm-size=8g --user "$(id -u):$(id -g)"
  -v "$task_root:/work" -v "$lab_dir:/lab:ro" -e REALITY_VIEW_ROOT=/work -e HOME=/work/runtime-home)
lock="${GPU_LOCK:-/tmp/physical-ai-four-domains.gpu.lock}"
case "${1:-help}" in
  capture)
    HEADLESS=1 flock "$lock" "${ISAAC_PYTHON:?Set ISAAC_PYTHON to your Isaac Lab Python executable}" \
      "$lab_dir/capture_road.py" --scene "$repo_dir/labs/world-driving/evidence/synthetic-intersection/synthetic-intersection.usda" \
      --output "$task_root/capture" --positions 40 --visualizer kit
    ;;
  prepare)
    "${base[@]}" "$image" run-script /lab/prepare_ncore.py
    ;;
  train)
    flock "$lock" "${base[@]}" -v "$lab_dir/road.yaml:/app/run.runfiles/_main/configs/reality-view.yaml:ro" \
      "$image" main --config-name reality-view.yaml 2>&1 | tee "$task_root/nurec-train.log"
    python3 "$lab_dir/collect_training.py"
    ;;
  render)
    python3 "$lab_dir/make_trajectory.py"
    artifact="$(python3 -c 'import json,os; print(json.load(open(os.path.join(os.environ["REALITY_VIEW_ROOT"],"artifact.json")))["artifact"])')"
    flock "$lock" "${base[@]}" "$image" render --artifact-path "/work/$artifact" --output-dir /work/novel \
      --camera-id camera_front_wide_120fov --height 576 --renderer gsplat --custom-rig-trajectory /work/novel-rig.json \
      --no-replicate-training-views --calib-source training-rig-poses --save-workers 2
    ;;
  enhance)
    flock "$lock" "${base[@]}" "$image" run-script /lab/enhance.py
    ;;
  policy)
    model_root="${ALPAMAYO_ROOT:?Set ALPAMAYO_ROOT to the folder prepared by setup_models.sh}"
    flock "$lock" "$model_root/alpamayo2-edge/.venv/bin/python" "$repo_dir/labs/world-driving/run_alpamayo_synthetic.py" \
      --input "$task_root/capture/policy" --model "$model_root/checkpoints/Alpamayo2-Edge" --output "$task_root/alpamayo"
    ;;
  *) printf '%s\n' 'Choose capture, prepare, train, render, enhance, or policy. See the bilingual lab guide.'; exit 2 ;;
esac
