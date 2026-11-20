#!/usr/bin/env bash
# Current publication artifacts only; full Git history is scanned separately.
set -euo pipefail
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
python3 -m venv "$scratch/venv"
"$scratch/venv/bin/python" -m pip install --quiet --disable-pip-version-check -r scripts/requirements-publication.txt
"$scratch/venv/bin/python" -m unittest discover -s scripts -p test_public_artifacts.py
"$scratch/venv/bin/python" scripts/check-public-artifacts.py

if [[ -z "${GITLEAKS_BIN:-}" ]]; then
  if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo 'Set GITLEAKS_BIN to an installed Gitleaks v8.30.1 executable on this platform.' >&2
    exit 2
  fi
  curl --fail --silent --show-error --location \
    https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz \
    --output "$scratch/gitleaks.tar.gz"
  "$scratch/venv/bin/python" - "$scratch/gitleaks.tar.gz" <<'PY'
import hashlib, sys
from pathlib import Path
expected = '551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb'
if hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() != expected:
    raise SystemExit('Gitleaks checksum mismatch')
PY
  tar -xzf "$scratch/gitleaks.tar.gz" -C "$scratch" gitleaks
  GITLEAKS_BIN="$scratch/gitleaks"
fi
# Copy from the index listing, without applying export-ignore or including local
# logs, scanner binaries, virtual environments, or build output.
"$scratch/venv/bin/python" - "$scratch/source" <<'PY'
from pathlib import Path
import shutil, subprocess, sys
root = Path(sys.argv[1])
for name in subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0'):
    if not name:
        continue
    source = Path(name)
    if source.is_file():
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
PY
"$GITLEAKS_BIN" dir "$scratch/source" --redact=100 --no-banner --no-color --max-archive-depth 3 --ignore-gitleaks-allow
