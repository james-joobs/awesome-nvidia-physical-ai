import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from curobo.examples.getting_started.motion_planning import _prepare_interpolated_trajectory
from curobo.motion_planner import MotionPlanner, MotionPlannerCfg
from curobo.scene import Cuboid, Scene
from curobo.types import JointState

def main():
    parser = argparse.ArgumentParser(description="Compare Franka motion plans before and after adding a cuboid.")
    parser.add_argument("output", type=Path)
    out = parser.parse_args().output
    out.mkdir(parents=True, exist_ok=True)
    table = Cuboid(name="workbench", pose=[0.0, 0.0, -0.055, 1., 0., 0., 0.], dims=[1.2, 0.75, 0.10])
    config = MotionPlannerCfg.create(
        robot="franka.yml",
        scene_model=Scene(cuboid=[table]),
        collision_cache={"cuboid": 4},
        graph_planner_algorithm="rrt",
        enable_trajopt=True,
    )
    planner = MotionPlanner(config)
    print(f"cuRobo | {torch.cuda.get_device_name(0)} | Franka Panda", flush=True)
    planner.warmup(enable_graph=True, num_warmup_iterations=2)
    start = JointState.from_position(planner.default_joint_state.position.unsqueeze(0), joint_names=planner.joint_names)
    goal_joints = start.clone()
    goal_joints.position[:, 0] += 1.60
    goal = planner.compute_kinematics(goal_joints).tool_poses.as_goal()

    def plan():
        planner.reset_seed()
        start_time = time.monotonic()
        result = planner.plan_pose(goal, start.clone(), max_attempts=8, enable_graph_attempt=0)
        torch.cuda.synchronize()
        ms = 1000 * (time.monotonic() - start_time)
        if result is None or not bool(result.success.any()):
            return None, ms
        return _prepare_interpolated_trajectory(result.get_interpolated_plan()), ms

    def kinematics(trajectory):
        points = planner.kinematics.get_active_js(trajectory).position[0].contiguous()
        state = planner.compute_kinematics(JointState.from_position(points, joint_names=planner.joint_names))
        tool = state.tool_poses.position.detach().cpu().numpy().reshape(len(points), -1, 3)[:, 0]
        spheres = state.robot_spheres.detach().cpu().numpy().reshape(len(points), -1, 4)
        return points.detach().cpu().numpy(), tool, spheres

    baseline, base_ms = plan()
    if baseline is None:
        raise RuntimeError("Baseline path failed dense validation")
    base_q, base_tool, base_spheres = kinematics(baseline)
    print(f"Baseline: validated | {len(base_tool)} waypoints | {base_ms:.1f} ms", flush=True)
    attempts = [
        (0.50, [0.04, 0.04, 0.08]),
        (0.57, [0.04, 0.04, 0.065]),
        (0.41, [0.035, 0.035, 0.065]),
        (0.50, [0.026, 0.026, 0.043]),
    ]
    for fraction, dims in attempts:
        center = base_tool[int((len(base_tool) - 1) * fraction)].copy()
        end_spheres = np.concatenate((base_spheres[0], base_spheres[-1]), axis=0)
        outside_box = np.maximum(np.abs(end_spheres[:, :3] - center) - np.asarray(dims) / 2, 0)
        if (np.linalg.norm(outside_box, axis=1) - end_spheres[:, 3] < 0.007).any():
            continue
        blocker = Cuboid(name="new_obstacle", pose=[*center.tolist(), 1., 0., 0., 0.], dims=dims)
        planner.update_world(Scene(cuboid=[table, blocker]))
        result, obstacle_ms = plan()
        print(f"Obstacle at {center.tolist()} | {dims} m | {'validated' if result is not None else 'no valid path'}", flush=True)
        if result is None:
            continue
        obstacle_q, obstacle_tool, obstacle_spheres = kinematics(result)
        is_inside = (np.abs(obstacle_tool - center) < np.asarray(dims) / 2).all(axis=1)
        if not is_inside.any():
            break
    else:
        raise RuntimeError("No obstacle case passed the planner and tool-center checks")
    assert np.allclose(base_q[0], obstacle_q[0], atol=1e-3)
    np.savez_compressed(
        out / "motion.npz", baseline_tool=base_tool, obstacle_tool=obstacle_tool,
        baseline_spheres=base_spheres, obstacle_spheres=obstacle_spheres, baseline_q=base_q, obstacle_q=obstacle_q,
    )
    report = {
        "planner": "cuRoboV2 Franka Panda",
        "same_start_and_goal": True,
        "baseline_waypoints": len(base_tool),
        "obstacle_waypoints": len(obstacle_tool),
        "baseline_wall_ms": round(base_ms, 2),
        "obstacle_wall_ms": round(obstacle_ms, 2),
        "obstacle_center_m": center.tolist(),
        "obstacle_dimensions_m": dims,
        "baseline_tool_enters_new_obstacle": bool((np.abs(base_tool - center) < np.asarray(dims)/2).all(axis=1).any()),
        "replanned_tool_enters_obstacle": bool(is_inside.any()),
    }
    (out / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
