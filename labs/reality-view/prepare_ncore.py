"""Convert calibrated, self-authored RGB/depth into NCore V4 and a Gaussian seed.

Run through NuRec 26.04 `run-script` with REALITY_VIEW_ROOT set to the task folder.
Depth is synthetic ground truth, not an estimated sensor measurement. This lab
therefore studies reconstruction/rendering, not monocular geometry recovery.
"""
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image
from upath import UPath
from ncore.data import OpenCVPinholeCameraModelParameters, ShutterType
from ncore.data.v4 import (SequenceComponentGroupsWriter, SequenceComponentGroupsReader,
                          PosesComponent, IntrinsicsComponent, MasksComponent,
                          CameraSensorComponent, CuboidsComponent)
from ncore.impl.common.transformations import HalfClosedInterval

root = Path(os.environ['REALITY_VIEW_ROOT'])
capture = root/'capture'
meta = json.loads((capture/'capture.json').read_text())
rows = meta['train']
times = np.array([r['timestamp_us'] for r in rows], dtype=np.uint64)
output = root/'ncore'
output.mkdir(exist_ok=True)
writer = SequenceComponentGroupsWriter(UPath(output), 'own-road', 'own-road',
    HalfClosedInterval.from_start_end(int(times[0]), int(times[-1])),
    {'source': 'self-authored Isaac Sim road; synthetic depth and calibration'}, store_type='directory')

def register(cls, name='default'):
    return writer.register_component_writer(cls.Writer, component_instance_name=name, group_name='default')

poses = register(PosesComponent)
camera_to_rig = np.array([[0,0,1,0],[-1,0,0,0],[0,-1,0,1.6],[0,0,0,1]], dtype=np.float64)
c2w = np.array([r['camera_to_world'] for r in rows], dtype=np.float64)
rigs = c2w @ np.linalg.inv(camera_to_rig)
poses.store_dynamic_pose('rig', 'world', rigs.astype(np.float32), times)
poses.store_static_pose('camera_front_wide_120fov', 'rig', camera_to_rig.astype(np.float32))
poses.store_static_pose('world', 'world_global', np.eye(4, dtype=np.float64))
K = np.array(rows[0]['K'])
intrinsics = register(IntrinsicsComponent)
intrinsics.store_camera_intrinsics('camera_front_wide_120fov', OpenCVPinholeCameraModelParameters(
    resolution=np.array([meta['width'], meta['height']], dtype=np.uint64),
    shutter_type=ShutterType.GLOBAL, principal_point=K[:2,2].astype(np.float32),
    focal_length=np.array([K[0,0],K[1,1]],dtype=np.float32), radial_coeffs=np.zeros(6,dtype=np.float32),
    tangential_coeffs=np.zeros(2,dtype=np.float32), thin_prism_coeffs=np.zeros(4,dtype=np.float32)))
# This name follows AlpaSim/NuRec conventions; actual intrinsics here are 90° pinhole, not 120°.
register(MasksComponent).store_camera_masks('camera_front_wide_120fov', {})
register(CuboidsComponent).store_observations([])
frames = register(CameraSensorComponent, 'camera_front_wide_120fov')
for row in rows:
    t = row['timestamp_us']
    frames.store_frame(image_binary_data=(capture/row['image']).read_bytes(), image_format='png',
                       frame_timestamps_us=np.array([t,t],dtype=np.uint64), generic_data={}, generic_meta_data={})
paths = writer.finalize()
reader = SequenceComponentGroupsReader(paths)
(output/'own-road.json').write_text(json.dumps(reader.get_sequence_meta().to_dict(),indent=2)+'\n')
# Back-project rendered z-depth using pixel centers and known OpenCV camera transforms.
points, colors = [], []
for row in rows[::3]:
    path = capture/row['image']
    z = np.load(path.with_suffix('.depth.npy'))
    rgb = np.array(Image.open(path).convert('RGB'))
    yy, xx = np.mgrid[0:meta['height']:8, 0:meta['width']:8]
    depth = z[yy,xx]
    valid = np.isfinite(depth) & (depth>.2) & (depth<100)
    p = np.stack([(xx+.5-K[0,2])/K[0,0]*depth, (yy+.5-K[1,2])/K[1,1]*depth, depth],axis=-1)[valid]
    c = np.array(row['camera_to_world'])
    points.append(p@c[:3,:3].T+c[:3,3]); colors.append(rgb[yy,xx][valid]/255.)
p = np.concatenate(points); c = np.concatenate(colors)
_, keep = np.unique(np.floor(p/.10).astype(np.int64), axis=0, return_index=True)
p,c = p[keep],c[keep]
fields = [(n,'f4') for n in ['x','y','z','nx','ny','nz','f_dc_0','f_dc_1','f_dc_2','opacity','scale_0','scale_1','scale_2','rot_0','rot_1','rot_2','rot_3']]
v = np.zeros(len(p), dtype=fields)
for i,n in enumerate(['x','y','z']):v[n]=p[:,i]
for i in range(3):v[f'f_dc_{i}']=(c[:,i]-.5)/.28209479177387814; v[f'scale_{i}']=np.log(.075)
v['opacity']=1.;v['rot_0']=1.
header = 'ply\nformat binary_little_endian 1.0\nelement vertex '+str(len(v))+'\n'+'\n'.join('property float '+n for n in v.dtype.names)+'\nend_header\n'
with (root/'seed.ply').open('wb') as stream:
    stream.write(header.encode('ascii')); stream.write(v.tobytes())
report={'train_views':len(rows),'held_out_views':len(meta['held_out']),'seed_gaussians':len(p),
        'seed_source':'back-projected synthetic z-depth; 0.10 m voxel subset',
        'intrinsics':K.tolist(),'camera_to_rig':camera_to_rig.tolist(),
        'camera_fov_degrees':90,'ncore_camera_id':'camera_front_wide_120fov',
        'camera_id_note':'schema-compatible identifier; the actual calibration is 90-degree pinhole'}
(root/'prepared.json').write_text(json.dumps(report,indent=2)+'\n')
print('PREPARED',json.dumps(report),flush=True)
