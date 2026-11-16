import argparse
import json
from pathlib import Path

import newton
import numpy as np
import warp as wp

root = Path(__file__).parent
parser = argparse.ArgumentParser(description="Run the shared box-stack scene using Newton XPBD.")
parser.add_argument("output", type=Path)
output = parser.parse_args().output
output.mkdir(parents=True, exist_ok=True)
spec = json.loads((root / "scene.json").read_text())
builder = newton.ModelBuilder(gravity=(0.0, 0.0, -spec["gravity"]))
shape = newton.ModelBuilder.ShapeConfig(density=spec["box_density"], mu=spec["friction"], restitution=0.0)

def body_transform(pos):
    return wp.transform(wp.vec3(*pos), wp.quat_identity())

for part in ("table", "floor"):
    x, y, z = spec[f"{part}_half_extents"]
    builder.add_shape_box(-1, xform=body_transform(spec[f"{part}_pos"]), hx=x, hy=y, hz=z, cfg=shape)
half = spec["box_half_extent"]
for pos in spec["boxes"]:
    body = builder.add_body(xform=body_transform(pos))
    builder.add_shape_box(body, hx=half, hy=half, hz=half, cfg=shape)

model = builder.finalize(device="cuda:0")
solver = newton.solvers.SolverXPBD(model, iterations=8)
pipeline = newton.CollisionPipeline(model)
contacts = pipeline.contacts()
state = model.state()
next_state = model.state()
control = model.control()
newton.eval_fk(model, model.joint_q, model.joint_qd, state)
poses = [state.body_q.numpy().copy()]
for frame in range(spec["frames"]):
    state.clear_forces()
    pipeline.collide(state, contacts)
    solver.step(state, next_state, control, contacts, 1 / spec["step_hz"])
    state, next_state = next_state, state
    poses.append(state.body_q.numpy())
    if frame in (0, 119, 239):
        print(f"NEWTON XPBD | step {frame + 1} | top-body z = {poses[-1][-1][2]:.4f} m", flush=True)
poses = np.asarray(poses)
assert np.isfinite(poses).all()
assert np.max(np.abs(poses[0, :, :3] - np.asarray(spec["boxes"]))) < 1e-5
assert np.max(np.abs(poses[-1, :, :3] - poses[0, :, :3])) > 0.1
np.save(output / "newton-poses.npy", poses)
print(f"NEWTON_DONE {newton.__version__} | {poses.shape} | {model.device}", flush=True)
