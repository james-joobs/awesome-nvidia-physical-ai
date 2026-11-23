#!/usr/bin/env bash
set -euo pipefail
model_root="${ALPAMAYO_ROOT:?Choose a separate folder for model code, environment and weights}"
task_root="${REALITY_VIEW_ROOT:?Choose the task output folder}"
uv_bin="${UV_BIN:-uv}"
mkdir -p "$model_root" "$task_root/checkpoints/Harmonizer"
source_root="$model_root/alpamayo2-edge"
if [[ ! -d "$source_root/.git" ]]; then
  git clone https://github.com/NVlabs/alpamayo2-edge.git "$source_root"
fi
if [[ -n "$(git -C "$source_root" status --porcelain)" ]]; then
  printf '%s\n' 'The Alpamayo checkout has local changes. Use a clean model folder.' >&2
  exit 1
fi
git -C "$source_root" fetch origin 02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e
git -C "$source_root" checkout --detach 02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e
(cd "$source_root" && "$uv_bin" sync --locked --extra dataset --no-default-groups)
"$source_root/.venv/bin/hf" download nvidia/Alpamayo2-Edge \
  --revision b92b6aa326bd3e2235db28f248ad5a30b5890e64 --local-dir "$model_root/checkpoints/Alpamayo2-Edge"
"$source_root/.venv/bin/hf" download nvidia/Harmonizer harmonizer_nontemporal.pt \
  --revision 20ca33d4612b1e98e0526b3a7ee604af5b289f58 --local-dir "$task_root/checkpoints/Harmonizer"
