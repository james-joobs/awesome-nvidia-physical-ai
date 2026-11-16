"""Summarize the warm-up and final training windows from the GPU workstation Microduck run."""

import argparse
import json
import re
import statistics
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
ITERATION = re.compile(r"Learning iteration\s+(\d+)/\d+")
SECTIONS = {
    "mean_reward": re.compile(r"Mean reward:\s+(-?\d+\.\d+)"),
    "mean_episode_length": re.compile(r"Mean episode length:\s+(\d+\.\d+)"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    log = ANSI.sub("", args.log.read_text())
    blocks = ITERATION.split(log)
    rows = []
    for step, block in zip(blocks[1::2], blocks[2::2], strict=True):
        entry = {"iteration": int(step)}
        for key, pattern in SECTIONS.items():
            match = pattern.search(block)
            if match is None:
                raise ValueError(f"Missing {key} for training iteration {step}")
            entry[key] = float(match.group(1))
        rows.append(entry)
    assert [row["iteration"] for row in rows] == list(range(500))
    windows = {"first_50": rows[:50], "last_50": rows[-50:]}
    aggregate = {name: {key: statistics.mean(row[key] for row in selected) for key in SECTIONS} for name, selected in windows.items()}
    print(f"Microduck | {len(rows)} iterations | {aggregate}", flush=True)
    (args.output / "result.json").write_text(json.dumps({
        "scope": "training statistics logged by RSL-RL for one run",
        "environments": 512, "iteration_count": len(rows), "windows": aggregate, "iterations": rows,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
