"""Check that each lab ships its code, both guides and consistent recorded evidence."""

import json
import hashlib
from math import isclose
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent


def report(lab):
    return json.loads((ROOT / lab / "recorded.json").read_text())


def verify_files():
    manifest = json.loads((ROOT / "index.json").read_text())
    labs = manifest["labs"]
    ids = {lab["id"] for lab in labs}
    assert len(ids) == len(labs) and len(labs) >= 8
    assert len(manifest["scenes"]) == 16 and all(lab in ids and tags for lab, tags in manifest["scenes"])
    for lab in labs:
        key = lab["id"]
        for path in (*lab["code"], lab["evidence"]):
            file = ROOT / key / path
            assert file.is_file() and file.stat().st_size, file
            if file.suffix == ".py":
                compile(file.read_text(), str(file), "exec")
        for language in ("en", "ko"):
            guide = ROOT.parent / "docs" / language / "labs" / f"{key}.md"
            assert guide.is_file() and sum(s.startswith("## ") for s in guide.read_text().splitlines()) == 3, guide


def verify_evidence():
    for key in ("carla-ego", "spatial-reconstruction", "scene-generation", "worldgen-scenes", "worldgen-isaac", "worldgen-navigation", "worldgen-dynamic-navigation"):
        runpy.run_path(str(ROOT / key / "check.py"))["main"]()
    world = report("world-driving")
    assert len(world["cosmos"]) == 3
    for case in world["cosmos"]:
        video = ROOT / "world-driving" / case["video"]
        assert case["generation_status"] == "success"
        assert hashlib.sha256(video.read_bytes()).hexdigest() == case["preview_mp4_sha256"]
    assert world["alpamayo"]["result"]["finite"]
    assert world["alpamayo"]["result"]["pred_xyz_shape"] == [1, 1, 1, 64, 3]
    inputs = ROOT / "world-driving" / "evidence" / "synthetic-intersection"
    shots = json.loads((inputs / "input.json").read_text())["shots"]
    assert len(shots) == 22 and len({row["camera_id"] for row in shots}) == 6
    assert all(hashlib.sha256((inputs / row["image"]).read_bytes()).hexdigest() == row["sha256"] for row in shots)

    newton = report("newton-materials")
    assert len(newton["cases"]) == 3 and all(row["official_tests_passed"] for row in newton["cases"])
    assert newton["recording_mode"] == "solver-usd-replay"
    assert len(newton["gui"]["takes"]) == 3

    physics = report("physics")
    live = physics["live"]
    assert isclose(live["simready-live"]["height_difference_m"], .14, abs_tol=.002)
    assert all(isclose(live["collider-live"][name], height, abs_tol=.02)
               for name, height in (("aligned", .80), ("raised", .92), ("disabled", 0)))
    friction = live["friction-live"]["distances_m"]
    bounce = live["bounce-live"]["peak_center_z_m_after_initial_contact"]
    assert friction[0] > friction[1] > friction[2] > 0 and bounce[0] < bounce[1] < bounce[2]
    assert physics["comparison"]["same_initial_poses"] and physics["comparison"]["integration_steps"] == 240

    motion = report("robot-motion")
    assert motion["curobo"]["same_start_and_goal"] and motion["curobo"]["baseline_tool_enters_new_obstacle"]
    assert not motion["curobo"]["replanned_tool_enters_obstacle"]
    assert motion["autodata"]["num_success"] == len(motion["audit"]) == 3
    assert all(row["first_success_frame"] is not None for row in motion["audit"])

    cad = report("scene-to-data")
    assert cad["cad_capture"]["rest_within_2cm"]
    points = cad["point_cloud"]["frames"]
    assert len(points) == 4 and max(row["absolute_displacement_error_mm"] for row in points) < 6

    everyday = report("everyday-robots")
    assert everyday["alarm_controller"][1]["fall_s"] is not None
    assert everyday["alarm_controller"][2]["fall_s"] is None
    assert everyday["drawer_final_m"][0] > .28 and max(everyday["drawer_final_m"][1:]) < .012
    assert [case["fits_demo_cart"] for case in everyday["cart"]] == [False, False, True]
    assert everyday["cleanup"]["SortTrashOnly"]["objects"]["snack"]["in_bin"]
    assert everyday["cleanup"]["SortTrashOnly"]["remaining_on_desk"] == 2

    gr00t = ROOT / "gr00t-placement"
    parse = runpy.run_path(str(gr00t / "check_result.py"))["read_episodes"]
    before = parse(gr00t / "recorded-24s.jsonl")
    after = parse(gr00t / "recorded-70s.jsonl")
    assert len(before) == 3 and all(row["placement_step"] is None for row in before)
    assert [row["placement_step"] for row in after] == [521, 574]

    replicator = report("replicator-outputs")
    rows = replicator["frames"]
    assert replicator["resolution_px"] == [960, 540]
    assert len(rows) == len({row["rgb_sha256"] for row in rows}) == 12
    assert [row["frame"] for row in rows if row["candidate_occluded"]] == [3, 7, 11]

    policy = json.loads((ROOT / "microduck/policy-publication.json").read_text())
    policy_bytes = (ROOT / "microduck/policy.onnx").read_bytes()
    assert len(policy_bytes) == policy["bytes"]
    assert hashlib.sha256(policy_bytes).hexdigest() == policy["sha256"]
    assert policy["comparison"]["outputs_bitwise_equal"]
    microduck = report("microduck")
    assert microduck["environments"] == 512 and microduck["iteration_count"] == len(microduck["iterations"]) == 500
    assert microduck["windows"]["last_50"]["mean_reward"] > microduck["windows"]["first_50"]["mean_reward"]
    warp = report("warp-particles")
    assert warp["particles"] == 65_536 and warp["frames"] == 200
    assert warp["displayed_particles"] * 4 == warp["particles"]
    assert warp["mean_particle_displacement_m"] > 0


if __name__ == "__main__":
    verify_files()
    verify_evidence()
    print("Verified code, bilingual guides and recorded results for all registered video labs.")
