#!/usr/bin/env bash
set -euo pipefail

task_root="${WORLD_DRIVING_ROOT:?Choose an isolated folder with at least 60 GiB free for weights, runtimes and caches}"
uv_bin="${UV_BIN:-$HOME/.local/bin/uv}"
mkdir -p "$task_root"
cd "$task_root"
clone_pin() {
  local directory="$1" url="$2" revision="$3"
  if [[ ! -d "$directory/.git" ]]; then
    git clone "$url" "$directory"
  fi
  if [[ -n "$(git -C "$directory" status --porcelain)" ]]; then
    printf 'Stop: %s has local changes. Choose an empty task folder.\n' "$directory" >&2
    return 1
  fi
  git -C "$directory" fetch origin "$revision"
  git -C "$directory" checkout --detach "$revision"
}
clone_pin cosmos-framework https://github.com/NVIDIA/cosmos-framework.git afd7d4c4087a8929c84523ff60172642fd11690b
clone_pin alpamayo2-edge https://github.com/NVlabs/alpamayo2-edge.git 02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e
(
  cd cosmos-framework
  "$uv_bin" tool run --from uv==0.11.29 uv sync --locked --group cu130 --extra guardrail --no-default-groups --python 3.13
)
(
  cd alpamayo2-edge
  "$uv_bin" sync --locked --extra dataset --no-default-groups
)
cosmos-framework/.venv/bin/hf download nvidia/Cosmos3-Edge \
  --revision 6afc1256321c3a8e623d89be3bc5117a1e90f96b \
  --local-dir checkpoints/Cosmos3-Edge
alpamayo2-edge/.venv/bin/hf download nvidia/Alpamayo2-Edge \
  --revision b92b6aa326bd3e2235db28f248ad5a30b5890e64 \
  --local-dir checkpoints/Alpamayo2-Edge
