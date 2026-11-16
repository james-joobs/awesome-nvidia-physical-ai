#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 3 ]]; then
  printf 'Usage: bash %s AUTODATA_CHECKOUT ANNOTATED_HDF5 OUTPUT_DIRECTORY\n' "$0" >&2
  exit 2
fi

checkout="$(cd "$1" && pwd -P)"
input="$(cd "$(dirname "$2")" && pwd -P)/$(basename "$2")"
mkdir -p "$3"
output="$(cd "$3" && pwd -P)"
test -s "$input"
cd "$checkout"

task=IsaacContrib-Stack-Cube-Franka-IK-Rel
python scripts/generate_dataset.py --viz kit --env_name "$task" --alg mimicgen \
  --generation_num_trials 3 --num_envs 3 \
  --task_descriptor autodata_examples/tasks/franka_cube_stack.yaml \
  --embodiment autodata_examples/embodiments/franka_ik_rel.yaml \
  --input_file "$input" --output_file "$output/franka-generated.hdf5" \
  --result_file "$output/run-result.json" --record_metric_inputs
python scripts/validate_dataset.py "$output/franka-generated.hdf5"
python submodules/IsaacLab-Arena/submodules/IsaacLab/scripts/tools/replay_demos.py \
  --viz kit --task "$task" --num_envs 1 \
  --dataset_file "$output/franka-generated.hdf5" --validate_success_rate
