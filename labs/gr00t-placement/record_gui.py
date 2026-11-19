"""Record the native Isaac Sim window during a real GR00T/Arena rollout.

Use run_recorded.sh after starting the official GR00T policy server. The USD
snapshot preserves the scene setup; the MP4 records the live policy rollout,
not an animation authored from a known successful trajectory.
"""

from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from isaaclab_arena.evaluation import experiment_runner


output = Path(os.environ["GR00T_GUI_OUTPUT"]).resolve()
output.mkdir(parents=True, exist_ok=True)
original_enter = experiment_runner.SimulationAppContext.__enter__


def window_id():
    listing = subprocess.check_output(["xwininfo", "-root", "-tree"], text=True)
    for line in listing.splitlines():
        if '"Isaac Lab ' in line and "mutter-x11-frames" not in line:
            return str(int(line.split()[0], 16))
    raise RuntimeError("The native Isaac Sim GUI window was not found")


class ObservedEnvironment:
    def __init__(self, original):
        self.original = original
        self.camera = None
        self.started = None
        self.frame_number = 0
        self.window = None
        self.wall_log = (output / "viewport-timing.jsonl").open("w", buffering=1)
        self.ffmpeg_log = (output / "viewport-ffmpeg.log").open("w")

    def __getattr__(self, name):
        return getattr(self.original, name)

    def reset(self, *args, **kwargs):
        observation = self.original.reset(*args, **kwargs)
        if self.camera is not None:
            return observation
        from omni.usd import get_context

        stage = get_context().get_stage()
        assert stage and stage.GetRootLayer().Export(str(output / "gr00t-arena.usda"))
        self.window = window_id()
        self.camera = subprocess.Popen([
            os.environ["GR00T_GUI_FFMPEG"], "-hide_banner", "-loglevel", "warning", "-y",
            "-f", "x11grab", "-framerate", "30", "-draw_mouse", "0",
            "-window_id", self.window, "-i", f"{os.environ['DISPLAY']}.0", "-an",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output / "gr00t-gui.mp4"),
        ], stdin=subprocess.DEVNULL, stdout=self.ffmpeg_log, stderr=subprocess.STDOUT)
        self.started = time.monotonic()
        self.started_utc = datetime.now(timezone.utc).isoformat()
        print("GR00T_GUI_START: scene exported; recording the live policy rollout", flush=True)
        self.sample()
        return observation

    def sample(self):
        env = self.original.unwrapped
        self.wall_log.write(json.dumps({
            "wall_s": time.monotonic() - self.started,
            "global_step": self.frame_number,
            "episodes_completed": int(env.completed_episode_count),
            "positions_m": {name: asset.data.root_pos_w[0].tolist()
                            for name, asset in env.scene.rigid_objects.items()},
        }) + "\n")

    def step(self, actions):
        result = self.original.step(actions)
        self.frame_number += 1
        if self.frame_number % 5 == 0:
            self.sample()
        return result

    def finish(self):
        try:
            if self.camera is not None:
                self.sample()
                if self.camera.poll() is None:
                    self.camera.send_signal(signal.SIGINT)
                self.camera.wait(timeout=20)
                video = output / "gr00t-gui.mp4"
                if not video.exists() or video.stat().st_size < 50_000:
                    raise RuntimeError("The GUI recording is missing or unexpectedly small")
                (output / "capture.json").write_text(json.dumps({
                    "application": "Isaac Sim GUI launched through Isaac Lab-Arena",
                    "isaacsim_version": version("isaacsim"),
                    "recording_mode": "live_policy_native_x11_window",
                    "video": video.name,
                    "scene": "gr00t-arena.usda",
                    "window_id": self.window,
                    "started_utc": self.started_utc,
                    "ended_utc": datetime.now(timezone.utc).isoformat(),
                    "wall_seconds": round(time.monotonic() - self.started, 3),
                    "control_steps": self.frame_number,
                    "ffmpeg_exit_code": self.camera.returncode,
                    "bytes": video.stat().st_size,
                }, indent=2) + "\n")
        finally:
            self.ffmpeg_log.close()
            self.wall_log.close()


def enter(context):
    value = original_enter(context)
    from isaaclab_arena.evaluation import run_execution

    rollout = run_execution.rollout_policy

    def observed_rollout(env, policy, *args, **kwargs):
        instrumented = ObservedEnvironment(env)
        try:
            return rollout(instrumented, policy, *args, **kwargs)
        finally:
            instrumented.finish()

    run_execution.rollout_policy = observed_rollout
    return value


if __name__ == "__main__":
    experiment_runner.SimulationAppContext.__enter__ = enter
    try:
        experiment_runner.main()
    except BaseException:
        # Some Kit shutdown paths mask a Python failure with exit code zero.
        (output / "capture-failed").touch()
        raise
