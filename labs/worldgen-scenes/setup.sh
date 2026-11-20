#!/usr/bin/env bash
# Linux x86_64 / RTX 5090 recipe, isolated from Isaac Sim and the fVDB renderer.
set -euo pipefail
if command -v uv >/dev/null 2>&1; then
  worldgen_uv="$(command -v uv)"
elif [[ -x "$HOME/.local/bin/uv" ]]; then
  worldgen_uv="$HOME/.local/bin/uv"
else
  echo 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/' >&2
  exit 1
fi
worldgen_root="${1:-runs/worldgen-runtime}"
mkdir -p "$worldgen_root"
worldgen_root="$(cd "$worldgen_root" && pwd)"
if [[ ! -x "$worldgen_root/.venv/bin/python" ]]; then "$worldgen_uv" venv --python 3.11 "$worldgen_root/.venv"; fi
worldgen_python="$worldgen_root/.venv/bin/python"
"$worldgen_uv" pip install --python "$worldgen_python" torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
"$worldgen_uv" pip install --python "$worldgen_python" xformers==0.0.30 \
  'https://github.com/nunchux-ai/nunchaku/releases/download/v0.2.0/nunchaku-0.2.0%2Btorch2.7-cp311-cp311-linux_x86_64.whl'
"$worldgen_uv" pip install --python "$worldgen_python" diffusers==0.33.1 transformers==4.51.3 peft==0.15.2 \
  accelerate==1.7.0 huggingface-hub==0.35.3 timm==1.0.15 opencv-python==4.12.0.88 open3d==0.19.0 \
  py360convert einops pillow scikit-image sentencepiece trimesh plyfile imageio imageio-ffmpeg \
  matplotlib omegaconf ninja scipy tqdm tensorboard tabulate fvcore iopath viser==1.1.1 setuptools wheel
if [[ ! -d "$worldgen_root/source/.git" ]]; then git clone https://github.com/ZiYang-xie/WorldGen.git "$worldgen_root/source"; fi
git -C "$worldgen_root/source" checkout 7ce7b2767fdf31e2727b69a2e61e2e950e3a017f
if [[ ! -d "$worldgen_root/da2/.git" ]]; then git clone https://github.com/EnVision-Research/DA-2.git "$worldgen_root/da2"; fi
git -C "$worldgen_root/da2" checkout d659838585f2bc9967c7e9367af573795271dbbb
if [[ ! -d "$worldgen_root/pytorch3d/.git" ]]; then git clone https://github.com/facebookresearch/pytorch3d.git "$worldgen_root/pytorch3d"; fi
git -C "$worldgen_root/pytorch3d" checkout ddfc55127fed1a74514cd24db08a7c2e62e76b08
PYTORCH3D_NO_EXTENSION=1 "$worldgen_uv" pip install --python "$worldgen_python" --no-build-isolation --no-deps "$worldgen_root/pytorch3d"
"$worldgen_uv" pip install --python "$worldgen_python" --no-deps \
  'git+https://github.com/EasternJournalist/utils3d.git@3913c65d81e05e47b9f367250cf8c0f7462a0900' \
  -e "$worldgen_root/source" -e "$worldgen_root/da2/src"
"$worldgen_python" -c 'import torch; from worldgen import WorldGen; from nunchaku.utils import get_precision; print(torch.__version__, torch.cuda.get_device_name(0), get_precision())'
