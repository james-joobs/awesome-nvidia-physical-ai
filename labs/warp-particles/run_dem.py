import argparse
import json
import time
from pathlib import Path

import numpy as np
import warp as wp
from warp.examples.core.example_dem import Example
from warp.render import OpenGLRenderer

parser = argparse.ArgumentParser(description="Run the Warp DEM sample and measure particle motion.")
parser.add_argument("output", type=Path)
parser.add_argument("--headless", action="store_true", help="Skip creating the OpenGL window.")
args = parser.parse_args()
output = args.output
output.mkdir(parents=True, exist_ok=True)
with wp.ScopedDevice("cuda:0"):
    example = Example(stage_path=None)
    renderer = OpenGLRenderer(
        title="Warp DEM | RTX 5090",
        screen_width=1280,
        screen_height=720,
        camera_pos=(31.0, 20.0, 35.0),
        camera_front=(-0.64, -0.34, -0.69),
        camera_fov=43.0,
        far_plane=150.0,
        background_color=(0.08, 0.12, 0.16),
        draw_sky=False,
        draw_axis=False,
        show_info=False,
    ) if not args.headless else None
    first = example.points.astype(np.float32)
    selection = slice(None, None, 4)
    if renderer:
        renderer.render_ground(size=120.0)

    def render(points):
        if not renderer:
            return
        renderer.begin_frame(example.sim_time)
        renderer.render_points("particles", points[selection].copy(), 0.13, (0.41, 0.85, 0.24))
        renderer.end_frame()

    render(first)
    print(f"CUDA device: {wp.get_device().name}", flush=True)
    print(f"DEM particles: {len(first):,} (viewer renders every fourth particle)", flush=True)
    (output / "viewer-ready").touch()
    deadline = time.monotonic() + 1.4
    while renderer and time.monotonic() < deadline:
        render(first)
        time.sleep(0.02)

    times = []
    for frame in range(200):
        if renderer and not renderer.is_running():
            raise RuntimeError("Viewer closed before the simulation completed")
        start = time.perf_counter()
        example.step()
        wp.synchronize_device()
        times.append((time.perf_counter() - start) * 1000)
        current = example.x.numpy()
        render(current)
        if frame % 30 == 0:
            print(f"Frame {frame + 1:3d}/200 | sim time {example.sim_time:.2f}s | DEM step {times[-1]:.2f} ms", flush=True)
        if renderer:
            time.sleep(max(0, (1 / 24) - (time.perf_counter() - start)))

    if not np.isfinite(current).all():
        raise RuntimeError("Non-finite particle positions")
    displacement = np.linalg.norm(current - first, axis=1)
    result = {
        "warp": wp.__version__,
        "device": wp.get_device().name,
        "particles": len(current),
        "displayed_particles": len(current[selection]) if renderer else 0,
        "frames": len(times),
        "simulated_seconds": round(example.sim_time, 3),
        "median_step_ms_after_first_frame": round(float(np.median(times[1:])), 3),
        "mean_particle_displacement_m": round(float(np.mean(displacement)), 3),
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    deadline = time.monotonic() + 7
    while renderer and time.monotonic() < deadline and renderer.is_running():
        render(current)
        time.sleep(0.028)
    if renderer:
        renderer.close()
