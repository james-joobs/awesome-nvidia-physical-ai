"""Write NuRec NCore input from RGB-only estimated cameras, preserving poses.

NuRec requires dynamic rig motion and static camera-to-rig transforms. Fit the
fixed transforms from RGB-derived poses and retain residuals explicitly.
All timestamps are nominal, not source sensor metadata.
"""
import hashlib,io,json,os
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
from upath import UPath
from ncore.data import OpenCVPinholeCameraModelParameters,ShutterType
from ncore.data.v4 import SequenceComponentGroupsWriter,SequenceComponentGroupsReader,PosesComponent,IntrinsicsComponent,MasksComponent,CameraSensorComponent,CuboidsComponent
from ncore.impl.common.transformations import HalfClosedInterval
root=Path(os.environ.get('NUREC_RGB_ROOT','/work'));meta=json.loads((root/'rgb-cameras.json').read_text());rows=meta['frames'];out=root/'ncore';out.mkdir(exist_ok=True)
writer=SequenceComponentGroupsWriter(UPath(out),'rgb-only-road','rgb-only-road',HalfClosedInterval.from_start_end(min(r['timestamp_us'] for r in rows),max(r['timestamp_us'] for r in rows)),{'source':'RGB-only COLMAP estimates; no source sensor data; relative units; nominal frame times'},store_type='directory')
def reg(cls,name='default'):return writer.register_component_writer(cls.Writer,component_instance_name=name,group_name='default')
pw=reg(PosesComponent);front=sorted((r for r in rows if r['camera']=='front_camera'),key=lambda r:r['timestamp_us']);F=np.array([[0,0,1,0],[-1,0,0,0],[0,-1,0,1],[0,0,0,1]],float);rigs={r['timestamp_us']:np.array(r['camera_to_world'])@np.linalg.inv(F) for r in front};nominal_times=np.array(sorted(rigs),np.uint64);pw.store_dynamic_pose('rig','world',np.array([rigs[t] for t in nominal_times],np.float32),nominal_times);pw.store_static_pose('world','world_global',np.eye(4));iw=reg(IntrinsicsComponent);mw=reg(MasksComponent);reg(CuboidsComponent).store_observations([]);residuals={}
for camera in sorted({r['camera'] for r in rows}):
 group=sorted((r for r in rows if r['camera']==camera),key=lambda r:r['timestamp_us']);relative=np.array([np.linalg.inv(rigs[r['timestamp_us']])@np.array(r['camera_to_world']) for r in group]);fixed=np.eye(4);fixed[:3,:3]=Rotation.from_matrix(relative[:,:3,:3]).mean().as_matrix();fixed[:3,3]=np.median(relative[:,:3,3],axis=0);error=np.linalg.inv(fixed)@relative;residuals[camera]={'translation_max_relative_units':float(np.linalg.norm(error[:,:3,3],axis=1).max()),'translation_mean_relative_units':float(np.linalg.norm(error[:,:3,3],axis=1).mean()),'rotation_max_degrees':float(np.rad2deg(Rotation.from_matrix(error[:,:3,:3]).magnitude()).max())};pw.store_static_pose(camera,'rig',fixed.astype(np.float32));r=group[0];K=np.array(r['K']);assert all(np.allclose(np.array(g['K']),K) for g in group)
 iw.store_camera_intrinsics(camera,OpenCVPinholeCameraModelParameters(resolution=np.array([r['width'],r['height']],np.uint64),shutter_type=ShutterType.GLOBAL,principal_point=K[:2,2].astype(np.float32),focal_length=np.array([K[0,0],K[1,1]],np.float32),radial_coeffs=np.zeros(6,np.float32),tangential_coeffs=np.zeros(2,np.float32),thin_prism_coeffs=np.zeros(4,np.float32)));mw.store_camera_masks(camera,{});cw=reg(CameraSensorComponent,camera)
 for r in group:
  path=root/'rgb'/r['image'];data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==r['sha256'];ts=r['timestamp_us'];cw.store_frame(image_binary_data=data,image_format='jpeg',frame_timestamps_us=np.array([ts,ts],np.uint64),generic_data={},generic_meta_data={})
 print('NCORE_RGB_CAMERA',camera,len(group),flush=True)
paths=writer.finalize();reader=SequenceComponentGroupsReader(paths);(out/'rgb-only-road.json').write_text(json.dumps(reader.get_sequence_meta().to_dict(),indent=2)+'\n')
z=np.load(root/'sfm-points.npz');P=z['xyz'];C=z['rgb']/255.;names=['x','y','z','nx','ny','nz','f_dc_0','f_dc_1','f_dc_2','opacity','scale_0','scale_1','scale_2','rot_0','rot_1','rot_2','rot_3'];a=np.zeros(len(P),dtype=[(n,'f4') for n in names])
for i,k in enumerate(['x','y','z']):a[k]=P[:,i]
for i in range(3):a[f'f_dc_{i}']=(C[:,i]-.5)/.28209479177387814;a[f'scale_{i}']=np.log(.035)
a['opacity']=1;a['rot_0']=1
header='ply\nformat binary_little_endian 1.0\nelement vertex '+str(len(a))+'\n'+'\n'.join('property float '+n for n in names)+'\nend_header\n'
with (root/'seed.ply').open('wb') as f:f.write(header.encode());f.write(a.tobytes())
(root/'prepared.json').write_text(json.dumps({'image_count':len(rows),'camera_count':6,'seed_gaussians':len(P),'seed_source':'RGB-triangulated COLMAP sparse points only','camera_pose_handling':'RGB-estimated front trajectory + fitted static camera-to-rig transforms; approximation residuals retained','rig_fit_residuals':residuals,'units':meta['units']},indent=2)+'\n');print('NCORE_RGB_READY',flush=True)
