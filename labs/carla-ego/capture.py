"""Record real CARLA RGB sensors; Traffic Manager is a rule-based driver, not an AI policy.

Run against a dedicated CARLA 0.9.16 server. Only actors created here are destroyed.
"""
import argparse
import hashlib
import json
import math
import queue
from pathlib import Path

import carla
import imageio.v2 as imageio
import numpy as np
from PIL import Image

CASES = [
    ("city-clear", "Town10HD_Opt", "ClearNoon", 1),
    ("junction-rain", "Town03", "HardRainNoon", 8),
    ("suburb-sunset", "Town02", "WetSunset", 0),
    ("highway-fog", "Town04_Opt", "CloudyNoon", 20),
]


def image_for_frame(q, frame):
    while True:
        image = q.get(timeout=30)
        if image.frame == frame:
            return np.frombuffer(image.raw_data, dtype=np.uint8).reshape(image.height, image.width, 4)[:, :, :3][:, :, ::-1].copy()
        if image.frame > frame:
            raise RuntimeError(f"Missed sensor frame {frame}; received {image.frame}")


def record(client, case, output, fps, seconds, width, height):
    name, map_name, weather_name, spawn_index = case
    print(f"Loading {name}: {map_name}, {weather_name}", flush=True)
    world = client.load_world(map_name)
    previous = world.get_settings()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 1 / fps
    world.apply_settings(settings)
    weather = getattr(carla.WeatherParameters, weather_name)
    if name == "highway-fog":
        weather.fog_density = 55
        weather.fog_distance = 8
        weather.fog_falloff = 1.0
    world.set_weather(weather)
    tm = client.get_trafficmanager(24005)
    tm.set_synchronous_mode(True)
    tm.set_random_device_seed(42)
    tm.global_percentage_speed_difference(20)
    actors = []
    writers = []
    try:
        blueprints = world.get_blueprint_library()
        points = world.get_map().get_spawn_points()
        bp = blueprints.find("vehicle.tesla.model3")
        bp.set_attribute("role_name", "hero")
        ego = world.spawn_actor(bp, points[spawn_index])
        actors.append(ego)
        for index in range(3, min(len(points), 75), 4):
            other = world.try_spawn_actor(bp, points[index])
            if other:
                actors.append(other)
                other.set_autopilot(True, 24005)
        ego.set_autopilot(True, 24005)
        tm.ignore_lights_percentage(ego, 0)
        tm.distance_to_leading_vehicle(ego, 3)
        streams = []
        folder = output / name
        folder.mkdir(parents=True, exist_ok=True)
        for view, transform in [
            ("ego", carla.Transform(carla.Location(x=0.3, z=1.45))),
            ("chase", carla.Transform(carla.Location(x=-6, z=3), carla.Rotation(pitch=-12))),
        ]:
            camera_bp = blueprints.find("sensor.camera.rgb")
            for key, value in {"image_size_x": width, "image_size_y": height, "fov": 90, "sensor_tick": 0}.items():
                camera_bp.set_attribute(key, str(value))
            camera_bp.set_attribute("motion_blur_intensity", "0")
            camera = world.spawn_actor(camera_bp, transform, attach_to=ego)
            actors.append(camera)
            q = queue.Queue()
            camera.listen(q.put)
            path = folder / f"{view}.mp4"
            writer = imageio.get_writer(path, fps=fps, codec="libx264", quality=None,
                pixelformat="yuv420p", macro_block_size=None,
                output_params=["-crf", "23", "-preset", "fast", "-movflags", "+faststart"])
            writers.append(writer)
            streams.append((view, q, writer, path))
        samples = []
        for i in range(round((seconds + 2) * fps)):
            frame = world.tick()
            images = [(view, image_for_frame(q, frame), writer, path) for view, q, writer, path in streams]
            if i < 2 * fps:
                continue
            for view, rgb, writer, path in images:
                writer.append_data(rgb)
                if i == 5 * fps:
                    Image.fromarray(rgb).save(folder / f"{view}.jpg", quality=92)
            transform, velocity = ego.get_transform(), ego.get_velocity()
            samples.append({"frame": frame, "simulation_seconds": round((i - 2*fps)/fps, 3),
                "position_m": [transform.location.x, transform.location.y, transform.location.z],
                "rotation_deg": [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll],
                "speed_mps": math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)})
        for writer in writers:
            writer.close()
        writers.clear()
        displacement = math.dist(samples[0]["position_m"], samples[-1]["position_m"])
        distance = sum(math.dist(a["position_m"], b["position_m"]) for a,b in zip(samples, samples[1:]))
        report = {"id": name, "map": world.get_map().name, "weather": weather_name,
            "fog_density": weather.fog_density, "controller": "CARLA Traffic Manager (rule-based)",
            "npc_vehicles": len(actors)-3, "fps": fps, "frames": len(samples), "resolution": [width, height],
            "displacement_m": round(displacement, 3), "distance_m": round(distance, 3), "trajectory": samples,
            "videos": [{"view": view, "file": str(path.relative_to(output)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for view,_,_,path in streams]}
        (folder / "result.json").write_text(json.dumps(report, indent=2)+"\n")
        print(f"{name}: {len(samples)} synchronized frames, {distance:.1f}m travelled", flush=True)
        if distance < 5:
            raise RuntimeError(f"{name}: ego did not travel enough; review the spawn and traffic")
        return report
    finally:
        for writer in writers:
            writer.close()
        for actor in reversed(actors):
            if actor.is_alive:
                if actor.type_id.startswith("sensor."):
                    actor.stop()
                actor.destroy()
        tm.set_synchronous_mode(False)
        world.apply_settings(previous)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=24000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=[c[0] for c in CASES], action="append")
    parser.add_argument("--seconds", type=float, default=16)
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    args = parser.parse_args()
    client = carla.Client(args.host, args.port)
    client.set_timeout(90)
    assert client.get_server_version() == "0.9.16", "Use the pinned CARLA server and client"
    cases = [c for c in CASES if not args.case or c[0] in args.case]
    results = [record(client, c, args.output, args.fps, args.seconds, args.width, args.height) for c in cases]
    (args.output / "result.json").write_text(json.dumps({"server_version": client.get_server_version(),
        "client_version": client.get_client_version(), "seed": 42, "cases": results}, indent=2)+"\n")


if __name__ == "__main__":
    main()
