"""CPU-only checks of our recorded CARLA trajectories and published sensor videos."""
import hashlib
import json
import math
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[2]
    data=json.loads((root/"labs/carla-ego/recorded.json").read_text())
    assert data["server_version"]=="0.9.16" and len(data["cases"])==4
    for case in data["cases"]:
        rows=case["trajectory"]
        assert len(rows)==case["frames"]==320 and case["fps"]==20
        assert all(b["frame"]-a["frame"]==1 and math.isclose(b["simulation_seconds"]-a["simulation_seconds"],.05,abs_tol=1e-6) for a,b in zip(rows,rows[1:]))
        assert all(all(math.isfinite(n) for n in row["position_m"]) and 0<=row["speed_mps"]<50 for row in rows)
        distance=sum(math.dist(a["position_m"],b["position_m"]) for a,b in zip(rows,rows[1:]))
        assert math.isclose(distance,case["distance_m"],abs_tol=.001) and distance>5
        video=root/"site/public/showcase"/case["published"]["file"]
        assert hashlib.sha256(video.read_bytes()).hexdigest()==case["published"]["sha256"]
        print(f'{case["id"]}: {len(rows)} frames, {distance:.1f}m, video hash OK')
    grid=data["grid"]
    assert hashlib.sha256((root/"site/public/showcase"/grid["file"]).read_bytes()).hexdigest()==grid["sha256"]
    print("Four CARLA sensor runs verified. This is not a learned-policy safety evaluation.")


if __name__=="__main__":
    main()
