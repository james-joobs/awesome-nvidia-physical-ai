"""Run the mobile-alarm and color-badge drawer simulations and render their traces."""

import argparse
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np

FPS = 30
DARK = (21, 23, 25)
TEXT = (237, 241, 240)
GREEN = (114, 221, 158)
AMBER = (108, 185, 247)


def label(frame, message, x, y, size=.55, color=TEXT):
    cv2.putText(frame, message, (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, color, 1, cv2.LINE_AA)


def encode(frames, destination, width, height, ffmpeg):
    with subprocess.Popen([
        str(ffmpeg), "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
        "-pix_fmt", "bgr24", "-s", f"{width}x{height}", "-r", str(FPS), "-i", "pipe:0",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(destination),
    ], stdin=subprocess.PIPE) as encoder:
        assert encoder.stdin is not None
        for frame in frames:
            assert frame.shape == (height, width, 3)
            encoder.stdin.write(frame.tobytes())
        encoder.stdin.close()
        assert encoder.wait() == 0


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def alarm_trace(mode):
    wheel_radius, base = .03, .1125
    x, y, yaw, z = .53, .30, math.pi, .0
    waypoints = [(.93, .30), (.93, .47), (.70, .47)]
    index = 0
    triggered = False
    fall_at = press_at = None
    min_clear = math.inf
    trace = []
    for frame in range(180):
        t = frame / FPS
        hand = (.10 + min(t * .30, .97), .30)
        separation = math.hypot(x - hand[0], y - hand[1])
        if fall_at is None and press_at is None and separation <= .075:
            press_at = t
        triggered = triggered or separation <= .25
        v = turn = 0.0
        if fall_at is None and press_at is None and triggered:
            if mode == "reverse_only":
                v = -.40
            elif mode == "edge_aware" and index < len(waypoints):
                tx, ty = waypoints[index]
                if math.hypot(tx - x, ty - y) < .015:
                    index += 1
                else:
                    err = wrap(math.atan2(ty - y, tx - x) + math.pi - yaw)
                    turn = float(np.clip(5 * err, -3.5, 3.5))
                    if abs(err) < .10:
                        v = -min(.4, 5 * math.hypot(tx - x, ty - y))
        left, right = (v - turn * base / 2) / wheel_radius, (v + turn * base / 2) / wheel_radius
        if fall_at is None:
            speed, omega = wheel_radius * (left + right) / 2, wheel_radius * (right - left) / base
            x += speed * math.cos(yaw + omega / (2 * FPS)) / FPS
            y += speed * math.sin(yaw + omega / (2 * FPS)) / FPS
            yaw = wrap(yaw + omega / FPS)
            min_clear = min(min_clear, x - .075, 1.20 - x - .075, y - .075, .60 - y - .075)
            if not (0 <= x <= 1.20 and 0 <= y <= .60):
                fall_at = t
        else:
            z = -min(.8, 9.81 * (t - fall_at) ** 2 / 2)
        trace.append({"t": t, "pose": [x, y, yaw, z], "hand": hand, "wheel_rad_s": [left, right]})
    return {"mode": mode, "fall_s": fall_at, "pressed_s": press_at, "minimum_footprint_clearance_m": min_clear, "trace": trace}


def alarm_frames(rows):
    names = {"stationary": "STATIONARY", "reverse_only": "REVERSE ONLY", "edge_aware": "EDGE-AWARE ROUTE"}
    for frame_idx in range(len(rows[0]["trace"])):
        frame = np.full((414, 1440, 3), DARK, dtype=np.uint8)
        label(frame, "RUNAWAY ALARM  /  SAME HAND TRAJECTORY", 20, 32, .72)
        for panel, row in enumerate(rows):
            x0, y0, scale = 38 + panel * 480, 124, 324
            cv2.rectangle(frame, (x0, y0), (x0 + 389, y0 + 194), (100, 113, 128), -1)
            cv2.rectangle(frame, (x0+24, y0+24), (x0+365, y0+170), (135, 149, 164), 1)
            label(frame, names[row["mode"]], x0, 89, .67)
            now = row["trace"][frame_idx]
            t = now["t"]
            x, y, yaw, z = now["pose"]
            xy = (int(x0 + x * scale), int(y0 + (.6 - y) * scale))
            line = [(int(x0 + p["pose"][0] * scale), int(y0 + (.6-p["pose"][1]) * scale)) for p in row["trace"][:frame_idx+1]]
            if len(line) > 1:
                cv2.polylines(frame, [np.array(line, np.int32)], False, GREEN, 2)
            hx, hy = now["hand"]
            cv2.circle(frame, (round(x0 + hx*scale), round(y0 + (.60-hy)*scale)), 13, (201, 202, 215), -1, cv2.LINE_AA)
            if z > -.7:
                cv2.circle(frame, xy, max(9, round(22 - abs(z)*10)), (52, 74, 76), -1, cv2.LINE_AA)
                direction = (round(xy[0] + math.cos(yaw)*27), round(xy[1] - math.sin(yaw)*27))
                cv2.arrowedLine(frame, xy, direction, AMBER, 4, cv2.LINE_AA)
            pressed = row["pressed_s"] is not None and t >= row["pressed_s"]
            fell = row["fall_s"] is not None and t >= row["fall_s"]
            state = "OVER EDGE" if fell else "BUTTON PRESSED" if pressed else "RUNNING"
            label(frame, state, x0, 358, .58, AMBER if fell else GREEN)
            label(frame, f"{t:.2f} s  |  wheel {now['wheel_rad_s'][0]:+.1f} / {now['wheel_rad_s'][1]:+.1f} rad/s", x0, 386, .48)
        yield frame


def camera_frame(t, badge, obstruction):
    image = np.full((244, 324, 3), (42, 46, 48), np.uint8)
    cv2.rectangle(image, (92, 53), (232, 205), (87, 101, 113), -1)
    cv2.rectangle(image, (115, 71), (210, 134), (29, 31, 35), -1)
    hand_y = max(88, int(235 - t * 92))
    cv2.circle(image, (163, hand_y), 22, (30, 108, 219), -1, cv2.LINE_AA)
    if badge:
        cv2.rectangle(image, (139, hand_y+15), (166, hand_y+41), (45, 195, 73), -1)
    if obstruction:
        cv2.rectangle(image, (168, 90), (193, 116), (219, 99, 28), -1)
    return image


def drawer_control(name, badge, obstruction):
    close, active = 0.0, False
    any_block_time = any_grant_time = None
    frames = []
    for index in range(108):
        t = index / FPS
        camera = camera_frame(t, badge, obstruction)
        zone = camera[78:156, 104:218]
        hand = int(cv2.countNonZero(cv2.inRange(zone, (10, 75, 180), (70, 145, 245)))) > 120
        # Card and slot are camera regions. Actuation does not read the scenario's input flags.
        card_roi = camera[80:205, 110:209]
        access = int(cv2.countNonZero(cv2.inRange(card_roi, (25, 155, 45), (65, 235, 115)))) > 160
        slot = camera[74:132, 115:208]
        occupied = int(cv2.countNonZero(cv2.inRange(slot, (170, 65, 5), (245, 136, 65)))) > 120
        active = active or hand
        if active:
            if access and any_grant_time is None:
                any_grant_time = t
            if not access and occupied and any_block_time is None:
                any_block_time = t
            goal = 0.0 if access or occupied else 1.0
            close += float(np.clip(goal - close, -.034, .034))
        frames.append({"t": t, "hand_present": hand, "badge_seen": access, "slot_occupied": occupied, "drawer_closed_fraction": close})
    return {"scenario": name, "input_badge": badge, "input_obstruction": obstruction,
            "grant_s": any_grant_time, "obstruction_interlock_s": any_block_time,
            "max_closed_fraction": max(item["drawer_closed_fraction"] for item in frames),
            "final_closed_fraction": frames[-1]["drawer_closed_fraction"], "trace": frames}


def guard_frames(rows):
    for i in range(len(rows[0]["trace"])):
        frame = np.full((370, 1440, 3), DARK, np.uint8)
        label(frame, "SNACK GUARD  /  WHAT THE RGB CAMERA SEES", 20, 32, .72)
        for col, row in enumerate(rows):
            x = 18 + 360*col
            item = row["trace"][i]
            image = camera_frame(item["t"], row["input_badge"], row["input_obstruction"])
            cv2.rectangle(image, (104, 78), (218, 156), (178, 183, 188), 1)
            frame[75:319, x:x+324] = image
            label(frame, row["scenario"], x, 63, .51)
            fraction = item["drawer_closed_fraction"]
            cv2.rectangle(frame, (x, 326), (x + round(fraction*310), 336), AMBER, -1)
            label(frame, f"DRAWER CLOSED {fraction:.0%}", x, 356, .49, AMBER if fraction > .5 else GREEN)
        yield frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("ffmpeg", type=Path)
    args = parser.parse_args()
    alarms = [alarm_trace(name) for name in ("stationary", "reverse_only", "edge_aware")]
    assert alarms[0]["pressed_s"] is not None and alarms[1]["fall_s"] is not None
    assert alarms[2]["pressed_s"] is None and alarms[2]["fall_s"] is None and alarms[2]["minimum_footprint_clearance_m"] > 0
    guards = [drawer_control("OWNER / NO CARD", False, False), drawer_control("OWNER / GREEN CARD", True, False),
              drawer_control("GUEST / SAME GREEN CARD", True, False), drawer_control("OBJECT IN SLOT", False, True)]
    assert guards[0]["final_closed_fraction"] == 1
    assert guards[1]["grant_s"] is not None and guards[2]["grant_s"] is not None
    assert guards[3]["obstruction_interlock_s"] is not None and guards[3]["max_closed_fraction"] == 0
    for name, rows, media, dimensions in (("27-runaway-alarm", alarms, alarm_frames, (1440, 414)),
                                           ("28-snack-guard", guards, guard_frames, (1440, 370))):
        folder = args.root / name / "result"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "result.json").write_text(json.dumps({"fps": FPS, "cases": rows}, indent=2) + "\n")
        encode(media(rows), folder / "comparison.mp4", *dimensions, args.ffmpeg)
        for row in rows:
            print(name, {key: value for key, value in row.items() if key != "trace"}, flush=True)


if __name__ == "__main__":
    main()
