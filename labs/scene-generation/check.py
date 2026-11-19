"""Verify the published procedural house tour without Blender or a GPU."""
import hashlib
import json
import math
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[2]
    data=json.loads((root/"labs/scene-generation/recorded.json").read_text())
    assert data["mode"]=="procedural geometry generation; not neural world-model inference"
    assert data["seed"]==0 and data["room_count"]==3 and data["frames"]==48
    assert data["render"]["device"]=="CPU" and data["render"]["denoiser"]=="OpenImageDenoise"
    assert data["camera"]["unique_poses"]==48
    assert all(math.isfinite(n) for point in data["camera"]["centers_m"] for n in point)
    centers=data["camera"]["centers_m"]
    distance=sum(math.dist(a,b) for a,b in zip(centers,centers[1:]))
    assert distance>.1 and math.isclose(distance,data["camera"]["path_length_m"],abs_tol=1e-5)
    movie=root/"site/public/showcase/scene-generation.mp4"
    assert hashlib.sha256(movie.read_bytes()).hexdigest()==data["video_sha256"]
    assert data["playback_fps"]==8 and data["frames"]/data["playback_fps"]==6
    print(f'{data["frames"]} rendered views, {distance:.2f}m camera path, 6-second slowed preview, video hash OK')


if __name__=="__main__":
    main()
