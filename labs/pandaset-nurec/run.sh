#!/usr/bin/env bash
set -euo pipefail
lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$lab_dir/../.." && pwd)"
root="${PANDASET_ROOT:?Set PANDASET_ROOT to a fresh output folder}"
mkdir -p "$root/runtime-home";root="$(cd -- "$root" && pwd)"
image="nvcr.io/nvidia/nre/nre-ga:26.04@sha256:97f43e7130c5636ce3e80ea3184d97f56a87fdd989b05cce42230881dbdea284"
base=(docker run --rm --gpus all --network none --shm-size=8g --user "$(id -u):$(id -g)"
 -v "$root:/work" -v "$lab_dir:/lab:ro" -e PANDASET_ROOT=/work -e HOME=/work/runtime-home)
lock="${GPU_LOCK:-/tmp/physical-ai-four-domains.gpu.lock}"
case "${1:-help}" in
 download)
  python3 "$lab_dir/index_zip.py" --output "$root/pandaset-index.json"
  python3 "$lab_dir/download.py" --index "$root/pandaset-index.json" --scene 001 --output "$root/data"
  ;;
 prepare) flock "$lock" "${base[@]}" "$image" run-script /lab/prepare.py ;;
 train)
  flock "$lock" "${base[@]}" -v "$lab_dir/scene.yaml:/app/run.runfiles/_main/configs/pandaset-scene.yaml:ro" \
   "$image" main --config-name pandaset-scene.yaml 2>&1 | tee "$root/nurec-train.log"
  python3 "$lab_dir/collect_training.py"
  ;;
 render)
  flock "$lock" "${base[@]}" "$image" run-script /lab/make_views.py
  artifact="$(python3 -c 'import json,os; print(json.load(open(os.path.join(os.environ["PANDASET_ROOT"],"artifact.json")))["artifact"])')"
  for view in front ego-elevated ego-quarter; do
   flock "$lock" "${base[@]}" "$image" render --artifact-path "/work/$artifact" --output-dir "/work/renders/$view" \
    --camera-id front_camera --height 576 --renderer gsplat --custom-rig-trajectory "/work/rig-$view.json" \
    --no-replicate-training-views --calib-source training-rig-poses --save-workers 2
  done
  ;;
 enhance)
  # The standalone official non-temporal checkpoint; mount separately if shared.
  weights="${HARMONIZER_WEIGHTS:?Set HARMONIZER_WEIGHTS to the folder containing harmonizer_nontemporal.pt}"
  if [[ ! -e "$root/novel" ]]; then ln -s renders/ego-quarter "$root/novel"; fi
  flock "$lock" "${base[@]}" -v "$repo_dir/labs/reality-view:/enhancer:ro" \
   -v "$weights:/work/checkpoints/Harmonizer:ro" -e REALITY_VIEW_ROOT=/work "$image" run-script /enhancer/enhance.py
  ;;
 *) printf '%s\n' 'Choose download, prepare, train, render, or enhance. See the bilingual guide.'; exit 2 ;;
esac
