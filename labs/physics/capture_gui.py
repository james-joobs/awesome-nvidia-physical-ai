"""Play the USD takes in the Isaac Sim GUI and capture its actual window."""

import argparse
import json
import os
from importlib.metadata import version
from pathlib import Path
import subprocess
import time
import traceback

from isaaclab.app import AppLauncher

TAKES = [
    ("01-alarm-wide", "runaway-alarm", "FilmCamera", 0.0, 1.0, 9.0),
    ("02-alarm-fall", "runaway-alarm", "FallCamera", 1.90, .78, 5.5),
    ("03-drawer-wide", "snack-guard", "FilmCamera", 0.0, 1.0, 7.0),
    ("04-drawer-close", "snack-guard", "DrawerCamera", .65, .8, 5.0),
    ("05-desk-cleanup", "desk-cleanup", "FilmCamera", 0.0, .90, 7.0),
    ("06-collider-offset", "collider-offset", "FilmCamera", 0.0, 1.0, 7.0),
    ("07-physx-newton", "physics-solvers", "FilmCamera", 0.0, 1.0, 7.0),
    ("08-collider-live", "collider-live", "FilmCamera", 0.0, 1.0, 7.0),
]


def window_id():
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        tree = subprocess.check_output(["xwininfo", "-root", "-tree"], text=True)
        for row in tree.splitlines():
            if '"Isaac Lab ' in row and 'mutter-x11-frames' not in row:
                return str(int(row.split()[0], 16))
        app.update()
    raise RuntimeError("Could not find Isaac Sim's native Kit window")


def pump(seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.update()


def summarize_live(stage_name, samples):
    if stage_name == "simready-live":
        positions = [xyz[2] for xyz in samples[-1]["positions_m"]]
        assert abs(positions[0] - .844) < .016 and abs(positions[1] - .984) < .016, positions
        return {"probe_center_z_m": positions, "height_difference_m": positions[1] - positions[0]}
    if stage_name == "friction-live":
        initials = [-.80] * 3
        travel = [samples[-1]["positions_m"][i][0] - initials[i] for i in range(3)]
        assert travel[0] > travel[1] + .10 > travel[2] + .17 and travel[2] > .035, travel
        return {"coefficients": [.16, .35, .75], "distances_m": travel}
    peak = []
    for index in range(3):
        heights = [sample["positions_m"][index][2] for sample in samples]
        first = next(i for i, z in enumerate(heights) if z < .945)
        peak.append(max(heights[first + 2:]))
    assert peak[1] > peak[0] + .09 and peak[2] > peak[1] + .18, peak
    return {"coefficient_of_restitution": [0, .55, .85], "peak_center_z_m_after_initial_contact": peak}


def capture(name, stage_name, camera, begin, speed, duration, window, context, timeline, args):
    from omni.kit.viewport.utility import get_active_viewport

    desired = str(args.scenes.resolve() / f"{stage_name}.usda")
    stage = context.get_stage()
    if stage and stage.GetRootLayer().realPath == desired and stage_name.endswith("-live"):
        timeline.stop()
        timeline.commit()
        context.close_stage()
        app.update()
        stage = None
    if not stage or stage.GetRootLayer().realPath != desired:
        assert context.open_stage(desired), desired
    camera_path = f"/World/{camera}"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        app.update()
        stage = context.get_stage()
        if stage and stage.GetRootLayer().realPath == desired and stage.GetPrimAtPath(camera_path):
            break
    else:
        raise RuntimeError(f"Camera {camera_path} never loaded from {desired}")
    get_active_viewport().camera_path = camera_path
    timeline.pause()
    timeline.set_current_time(begin)
    timeline.commit()
    pump(1.30)
    last = stage.GetEndTimeCode() / stage.GetTimeCodesPerSecond()
    live = stage_name.endswith("-live")
    started_physics = False
    live_samples = []
    inspector = None
    if live:
        from omni.physx import get_physx_interface
        inspector = get_physx_interface()
    print(f"TAKE_START {name} camera={camera_path} duration={duration:.2f}s", flush=True)
    output = args.output / f"{name}.mp4"
    with (args.output / f"{name}.capture.log").open("w") as log:
        recorder = subprocess.Popen([
            str(args.ffmpeg), "-nostdin", "-hide_banner", "-loglevel", "warning", "-y",
            "-f", "x11grab", "-draw_mouse", "0", "-framerate", "30",
            "-window_id", window, "-i", f"{os.environ['DISPLAY']}.0", "-t", str(duration),
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
        ], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        started = time.monotonic()
        updates = 0
        while recorder.poll() is None:
            wall = time.monotonic() - started
            if wall > duration + 12:
                recorder.terminate()
                recorder.wait(timeout=8)
                raise RuntimeError(f"Screen recorder timed out during {name}")
            if live:
                if not started_physics and wall >= .72:
                    timeline.set_looping(False)
                    timeline.play()
                    timeline.commit()
                    started_physics = True
            else:
                offset = max(0, wall - .48)
                timeline.set_current_time(min(last, begin + offset * speed))
                timeline.commit()
            app.update()
            updates += 1
            if inspector and started_physics and stage_name != "collider-live" and updates % 2 == 0:
                count = 2 if stage_name == "simready-live" else 3
                positions = [inspector.get_rigidbody_transformation(f"/World/Trial_{i}/Body") for i in range(count)]
                if all(value["ret_val"] for value in positions):
                    live_samples.append({"time_s": timeline.get_current_time(),
                                         "positions_m": [list(value["position"]) for value in positions]})
        assert recorder.returncode == 0 and output.stat().st_size > 50_000, name
    actual = timeline.get_current_time()
    live_results = None
    if stage_name == "collider-live":
        live_results = {}
        for case, expected in (("aligned", .80), ("raised", .92), ("disabled", 0)):
            pose = inspector.get_rigidbody_transformation(f"/World/ColliderCase_{case}/Part")
            assert pose["ret_val"], case
            bottom = float(pose["position"][2]) - .06
            assert abs(bottom - expected) < .02, (case, bottom, expected)
            live_results[case] = bottom
    elif live:
        assert len(live_samples) > 30
        live_results = summarize_live(stage_name, live_samples)
        (args.output / f"{name}.physics.json").write_text(json.dumps({
            "scene": stage_name, "summary": live_results, "samples": live_samples,
        }, indent=2) + "\n")
    if live:
        timeline.pause()
        timeline.commit()
        print(f"LIVE_PHYSX {live_results}", flush=True)
    print(f"TAKE_DONE {name} timeline_end={actual:.3f} updates={updates}", flush=True)
    return {"file": output.name, "scene": stage_name, "camera": camera_path,
            "playback_speed": speed, "playback_start_s": begin, "playback_end_s": actual, "app_updates": updates,
            "live_physx_final_bottom_m": live_results if stage_name == "collider-live" else None,
            "live_physx": live_results if stage_name != "collider-live" else None}


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("scenes", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("ffmpeg", type=Path)
parser.add_argument("--takes", nargs="+")
parser.add_argument("--plan", type=Path, help="JSON take list for a different set of scenes")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.enable_cameras = True
args.output.mkdir(parents=True, exist_ok=True)
launcher = AppLauncher(args)
app = launcher.app
failed = False
try:
    import carb
    import omni.timeline
    import omni.usd

    settings = carb.settings.get_settings()
    settings.set_bool("/rtx/hydra/readTransformsFromFabricInRenderDelegate", False)
    settings.set_bool("/persistent/app/viewport/Viewport/Viewport0/scene/cameras/visible", False)
    context = omni.usd.get_context()
    timeline = omni.timeline.get_timeline_interface()
    window = window_id()
    plan = json.loads(args.plan.read_text()) if args.plan else TAKES
    selected = [take for take in plan if not args.takes or take[0] in args.takes]
    assert selected and (not args.takes or len(selected) == len(set(args.takes)))
    metadata = []
    for take in selected:
        metadata.append(capture(*take, window, context, timeline, args))
    (args.output / "capture.json").write_text(json.dumps({
        "application": "Isaac Sim GUI (launched by Isaac Lab)", "isaacsim_version": version("isaacsim"),
        "recording": "X11 capture of the native application window", "takes": metadata,
    }, indent=2) + "\n")
except Exception:
    failed = True
    traceback.print_exc()
finally:
    if failed:
        # SimulationApp's fast shutdown can otherwise hide an exception's exit code.
        (args.output / "capture-failed").touch()
    app.close()
