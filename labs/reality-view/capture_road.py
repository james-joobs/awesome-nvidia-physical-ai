"""Capture our primitive-only road as calibrated RGB/depth, held-out views and VLA inputs.

Run with Isaac Lab's Python, using the scene committed in this repository.
No downloaded driving scenes, textures, actors or NVIDIA dataset frames are used.
"""
import argparse
import hashlib
import json
import math
from importlib.metadata import version
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument('--scene', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--positions', type=int, default=40)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.enable_cameras = True
launcher = AppLauncher(args)
app = launcher.app

import numpy as np
from PIL import Image
import omni.replicator.core as rep
import omni.usd
from pxr import Gf, UsdGeom

out = args.output
out.mkdir(parents=True, exist_ok=True)
omni.usd.get_context().open_stage(str(args.scene.resolve()))
for _ in range(30):
    app.update()
stage = omni.usd.get_context().get_stage()
camera = UsdGeom.Camera.Get(stage, '/World/Camera')
op = camera.MakeMatrixXform()
w, h = 1024, 576
aperture = 20.955
camera.GetHorizontalApertureAttr().Set(aperture)
camera.CreateVerticalApertureAttr(aperture * h / w)
camera.GetClippingRangeAttr().Set(Gf.Vec2f(.1, 250))
product = rep.create.render_product(str(camera.GetPath()), (w, h))
rgb_reader = rep.AnnotatorRegistry.get_annotator('rgb')
depth_reader = rep.AnnotatorRegistry.get_annotator('distance_to_image_plane')
for reader in [rgb_reader, depth_reader]:
    reader.attach([product])


def capture(folder, name, eye, yaw=0., focal=10.4775, depth=False):
    folder.mkdir(exist_ok=True, parents=True)
    target = Gf.Vec3d(*eye) + Gf.Vec3d(30 * math.cos(yaw), 30 * math.sin(yaw), -.2)
    matrix = Gf.Matrix4d(1).SetLookAt(Gf.Vec3d(*eye), target, Gf.Vec3d(0, 0, 1)).GetInverse()
    op.Set(matrix)
    camera.GetFocalLengthAttr().Set(focal)
    for _ in range(10):
        app.update()
    rgb = np.asarray(rgb_reader.get_data())[:, :, :3].copy()
    if rgb.shape != (h, w, 3) or rgb.mean() < 3:
        raise RuntimeError('Camera returned an empty or unexpected image')
    path = folder / f'{name}.png'
    Image.fromarray(rgb).save(path)
    # USD uses row vectors, -Z forward, +Y up. NCore/OpenCV uses +Z forward, +Y down.
    c2w = np.asarray(matrix, dtype=np.float64).T @ np.diag([1., -1., -1., 1.])
    K = [[focal / aperture * w, 0, w / 2], [0, focal / aperture * w, h / 2], [0, 0, 1]]
    if depth:
        z = np.asarray(depth_reader.get_data()).reshape(h, w).copy()
        np.save(folder / f'{name}.depth.npy', z)
    return {'image': str(path.relative_to(out)), 'camera_to_world': c2w.tolist(), 'K': K,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


train = []
for track, y in enumerate([-2.6, -1.8, -1.0]):
    for i, x in enumerate(np.linspace(-14, 12, args.positions)):
        row = capture(out/'train', f'{len(train):05d}', (float(x), y, 1.6), depth=True)
        row['timestamp_us'] = 1_000_000 + len(train) * 100_000
        train.append(row)
    print(f'CAPTURE training track {track + 1}/3 completed', flush=True)
novel = []
for i, x in enumerate(np.linspace(-12, 10, args.positions)):
    row = capture(out/'held-out', f'{i:05d}', (float(x), -1.4, 2.6))
    row['timestamp_us'] = 1_000_000 + i * 100_000
    novel.append(row)
print('CAPTURE held-out elevated camera completed', flush=True)
# Same six camera IDs/time history as the existing, pinned Alpamayo 2 Edge wrapper.
profiles = {0: (55, [-1, -.1, 0], 12), 1: (0, [-2, -1, -.5, -.1, 0], 14),
            2: (-55, [-1, -.1, 0], 12), 3: (145, [-1, -.1, 0], 12),
            5: (-145, [-1, -.1, 0], 12), 6: (0, [-2, -1, -.5, -.1, 0], 30)}
shots = []
policy = out/'policy'
for camera_id, (degrees, times, focal) in profiles.items():
    for offset in times:
        name = f'camera-{camera_id}-t{round((offset + 2)*1e6):07d}'
        row = capture(policy, name, (offset * 5, -1.8, 1.6), math.radians(degrees), focal)
        # Match the pre-existing smoke test resolution, without changing the scene aspect ratio.
        p = out/row['image']
        Image.open(p).resize((640, 360), Image.Resampling.LANCZOS).save(p)
        shots.append({'camera_id': camera_id, 'timestamp_us': round((offset + 2)*1e6),
                      'relative_time_s': offset, 'image': p.name,
                      'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
manifest = {'schema': 1, 'runtime': {'isaac_sim': version('isaacsim'), 'isaac_lab': version('isaaclab')}, 'source': 'self-authored primitive-only Isaac Sim road',
            'width': w, 'height': h, 'units': 'meters', 'camera_convention': 'OpenCV: x right, y down, z forward',
            'world_convention': 'x road forward, y left, z up', 'train': train, 'held_out': novel,
            'held_out_offset': 'elevated by 1.0 m; y=-1.4 m between capture tracks',
            'scene_sha256': hashlib.sha256(args.scene.read_bytes()).hexdigest()}
(out/'capture.json').write_text(json.dumps(manifest, indent=2)+'\n')
(policy/'input.json').write_text(json.dumps({'kind': 'self-authored road; model interface experiment',
    'width': 640, 'height': 360, 'ego_speed_m_s': 5, 'shots': shots,
    'history_times_s': [round(-1.9+.1*i, 3) for i in range(20)],
    'history_xyz_m': [[round((-1.9+.1*i)*5, 3), 0, 0] for i in range(20)]}, indent=2)+'\n')
stage.GetRootLayer().Export(str(out/'road.usda'))
for reader in [rgb_reader, depth_reader]:
    reader.detach([product])
print(f'CAPTURE complete: {len(train)} training, {len(novel)} held-out, {len(shots)} policy frames', flush=True)
app.close()
