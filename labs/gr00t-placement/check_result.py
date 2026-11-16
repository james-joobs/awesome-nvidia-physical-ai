"""Read Arena's episode JSONL and distinguish lifting from stable placement."""

import argparse
import json
from pathlib import Path


def read_episodes(path):
    episodes = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        milestones = {event["predicate_name"]: event["step"] for event in row["progress"]["events"]}
        lift = next((step for name, step in milestones.items() if "object_is_above_height" in name), None)
        placed = next((step for name, step in milestones.items() if "object_on_destination" in name), None)
        if bool(row["success"]) != (placed is not None):
            raise ValueError(f"Arena success and placement event disagree in episode {len(episodes) + 1}")
        episodes.append({"steps": row["episode_length"], "lift_step": lift, "placement_step": placed})
    if not episodes:
        raise ValueError("No episodes in the Arena report")
    return episodes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode_report", type=Path)
    parser.add_argument("--rate", type=float, default=15, help="Arena environment control steps per second")
    args = parser.parse_args()
    if args.rate <= 0:
        parser.error("--rate must be positive")
    for index, episode in enumerate(read_episodes(args.episode_report), start=1):
        lifted = episode["lift_step"]
        placed = episode["placement_step"]
        print(f"Trial {index}: {episode['steps']} steps,"
              f" lift {format(lifted / args.rate, '.2f') + ' s' if lifted is not None else 'no'},"
              f" placed {format(placed / args.rate, '.2f') + ' s' if placed is not None else 'no'}")
