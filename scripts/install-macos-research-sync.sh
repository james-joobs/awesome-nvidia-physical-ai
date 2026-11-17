#!/bin/bash
# Keep a separate local copy of the GitHub Actions research reports.
set -euo pipefail

label='io.github.james-joobs.physical-ai-research-sync'
branch='research-reports'
remote='https://github.com/james-joobs/awesome-nvidia-physical-ai.git'
mirror="${1:-$HOME/work/awesome-nvidia-physical-ai-reports}"
agents="$HOME/Library/LaunchAgents"
logs="$HOME/Library/Logs/physical-ai-research-sync.log"
plist="$agents/$label.plist"
domain="gui/$(id -u)"

if [[ "$(uname -s)" != Darwin || "$mirror" != /* ]]; then
  echo "Run this on macOS with an absolute destination path." >&2
  exit 2
fi
launchctl print "$domain" >/dev/null
mkdir -p "$agents" "$HOME/Library/Logs" "$(dirname "$mirror")"
export GIT_TERMINAL_PROMPT=0

if [[ ! -e "$mirror" ]]; then
  /usr/bin/git -c credential.helper= clone --single-branch --branch "$branch" "$remote" "$mirror"
elif [[ "$(/usr/bin/git -C "$mirror" remote get-url origin)" != "$remote" ||
        "$(/usr/bin/git -C "$mirror" branch --show-current)" != "$branch" ]]; then
  echo "The destination is not the dedicated research-reports checkout." >&2
  exit 2
fi

pending=$(mktemp "$agents/$label.XXXXXX")
trap 'rm -f "$pending"' EXIT
python3 - "$pending" "$label" "$mirror" "$logs" <<'PY'
import plistlib
import sys

path, label, mirror, log_path = sys.argv[1:]
job = {
    "Label": label,
    "ProgramArguments": [
        "/usr/bin/git", "-c", "credential.helper=", "-c", "http.lowSpeedLimit=1000",
        "-c", "http.lowSpeedTime=30", "-C", mirror, "pull", "--ff-only", "--no-rebase",
        "origin", "research-reports",
    ],
    "EnvironmentVariables": {"GIT_TERMINAL_PROMPT": "0"},
    "RunAtLoad": True,
    "StartCalendarInterval": [{"Minute": 7}, {"Minute": 37}],
    "StandardOutPath": "/dev/null",
    "StandardErrorPath": log_path,
}
with open(path, "wb") as stream:
    plistlib.dump(job, stream)
PY
plutil -lint "$pending"
if launchctl print "$domain/$label" >/dev/null 2>&1; then
  launchctl bootout "$domain/$label"
fi
mv "$pending" "$plist"
launchctl bootstrap "$domain" "$plist"
echo "Local research reports: $mirror/latest.md"
