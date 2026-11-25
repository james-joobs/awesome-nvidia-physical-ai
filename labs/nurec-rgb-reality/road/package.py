"""Package browser assets and measured run receipts, with source data kept outside Git."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baked", type=Path, required=True)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ground", type=Path, help="Earlier bake when source-view texture validation favors it")
    parser.add_argument("--surroundings", type=Path)
    parser.add_argument("--ground-comparison", type=Path)
    args = parser.parse_args()

    ground = args.ground or args.baked
    record = json.loads((ground / "road.json").read_text())
    sky = json.loads((args.baked / "sky-filter.json").read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    def export(source):
        with source.open("rb") as stream:
            sha = hashlib.file_digest(stream, "sha256").hexdigest()
        shutil.copy2(source, args.output / source.name)
        return {"file": source.name, "bytes": source.stat().st_size, "sha256": sha}

    record["atlas_asset"] = export(ground / "ground.webp")
    record["sky_filtered"] = export(args.baked / "sky-filtered.spz")
    record["sky_filtered"].update(sky)
    record["rtx_5090_runs"] = {
        key: json.loads((args.inference / f"{key}.json").read_text())
        for key in ("mask", "match", "depth")
    }
    if args.surroundings:
        context = json.loads((args.surroundings / "surroundings.json").read_text())
        for asset in [context["sky"], *context["facades"]]:
            asset.update(export(args.surroundings / asset["file"]))
        record["surroundings"] = context
        record["latest_calibration"] = json.loads((args.baked / "road.json").read_text())["calibration"]
    if args.ground_comparison:
        record["ground_comparison"] = json.loads(args.ground_comparison.read_text())
    (args.output / "road.json").write_text(json.dumps(record, separators=(",", ":"))+"\n")


if __name__ == "__main__":
    main()
