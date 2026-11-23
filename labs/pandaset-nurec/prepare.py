"""PandaSet RGB/LiDAR -> NCore V4 + a colored Gaussian seed (NuRec 26.04).

Data terms remain separate from code. Run the pinned runtime with --network none
and only this output folder mounted. A restricted unpickler refuses all globals
except the nine pandas/numpy constructors used by the original LiDAR payload.
This first baseline is static; moving actors can leave reconstruction artifacts.
"""
import gzip,io,json,os,pickle
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation,Slerp
from upath import UPath
from ncore.data import OpenCVPinholeCameraModelParameters,ShutterType
from ncore.data.v4 import (SequenceComponentGroupsWriter,SequenceComponentGroupsReader,
 PosesComponent,IntrinsicsComponent,MasksComponent,CameraSensorComponent,CuboidsComponent)
from ncore.impl.common.transformations import HalfClosedInterval
root=Path(os.environ['PANDASET_ROOT']);scene=root/'data'/'001'
cameras=['front_camera','front_left_camera','front_right_camera','left_camera','right_camera','back_camera']
class Restricted(pickle.Unpickler):
 def find_class(self,module,name):
  allow={('pandas.core.frame','DataFrame'),('pandas.core.internals.managers','BlockManager'),('pandas.core.indexes.base','_new_Index'),('pandas.core.indexes.base','Index'),('pandas.core.indexes.range','RangeIndex'),('numpy.core.multiarray','_reconstruct'),('numpy','ndarray'),('numpy','dtype'),('builtins','slice')}
  if (module,name) not in allow:raise pickle.UnpicklingError(f'Blocked global: {module}.{name}')
  return super().find_class(module,name)
def poses(path):
 rows=json.loads(path.read_text());q=np.array([[r['heading'][k] for k in ['x','y','z','w']] for r in rows]);p=np.array([[r['position'][k] for k in ['x','y','z']] for r in rows]);out=np.tile(np.eye(4),(len(rows),1,1));out[:,:3,:3]=Rotation.from_quat(q).as_matrix();out[:,:3,3]=p;return out
L=poses(scene/'lidar/poses.json');lt=np.array(json.loads((scene/'lidar/timestamps.json').read_text()))
# Original lidar ego axes: +X right, +Y forward, +Z up. Target +X forward, +Y left.
G=np.array([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]],float);rig=L@G
rinterp=Slerp(lt,Rotation.from_matrix(rig[:,:3,:3]))
def rig_at(times):
 times=np.clip(times,lt[0],lt[-1]);out=np.tile(np.eye(4),(len(times),1,1));out[:,:3,:3]=rinterp(times).as_matrix()
 for j in range(3):out[:,j,3]=np.interp(times,lt,rig[:,j,3])
 return out
# Trim boundary poses instead of extrapolating asynchronous camera exposures.
indices=np.arange(2,78);out=root/'ncore';out.mkdir(exist_ok=True);base=lt[0]
def us(t):return np.rint((np.array(t)-base)*1e6).astype(np.uint64)+1_000_000
writer=SequenceComponentGroupsWriter(UPath(out),'pandaset-001','pandaset-001',HalfClosedInterval.from_start_end(int(us(lt)[0]),int(us(lt)[-1])),{'source':'PandaSet by Scale AI and Hesai; original LICENSE.txt retained; community mirror'},store_type='directory')
def reg(cls,name='default'):return writer.register_component_writer(cls.Writer,component_instance_name=name,group_name='default')
pw=reg(PosesComponent);pw.store_dynamic_pose('rig','world',rig.astype(np.float32),us(lt));pw.store_static_pose('world','world_global',np.eye(4));iw=reg(IntrinsicsComponent);mw=reg(MasksComponent);reg(CuboidsComponent).store_observations([])
meta={};receipt={'camera_pose_approximation':{},'source':'PandaSet scene 001','train_indices':indices.tolist(),'width':1024,'height':576,'baseline':'static 3D Gaussian scene; no actor dynamics or control','original_data_terms':'CC BY 4.0 + PandaSet Dataset Terms; see data/001/LICENSE.txt'}
for cam in cameras:
 croot=scene/'camera'/cam;C=poses(croot/'poses.json');ct=np.array(json.loads((croot/'timestamps.json').read_text()));intr=json.loads((croot/'intrinsics.json').read_text());C2R=np.linalg.inv(rig_at(ct[indices]))@C[indices]
 # Time-aligned rigid calibration estimate, with measured residuals recorded.
 fixed=np.eye(4);fixed[:3,:3]=Rotation.from_matrix(C2R[:,:3,:3]).mean().as_matrix();fixed[:3,3]=np.median(C2R[:,:3,3],axis=0)
 err=np.linalg.inv(fixed)@C2R;receipt['camera_pose_approximation'][cam]={'max_translation_m':float(np.linalg.norm(err[:,:3,3],axis=1).max()),'max_rotation_deg':float(np.rad2deg(Rotation.from_matrix(err[:,:3,:3]).magnitude()).max())}
 pw.store_static_pose(cam,'rig',fixed.astype(np.float32));scale=1024/1920;K=np.array([[intr['fx'],0,intr['cx']],[0,intr['fy'],intr['cy']],[0,0,1]],float);K[:2]*=scale
 iw.store_camera_intrinsics(cam,OpenCVPinholeCameraModelParameters(resolution=np.array([1024,576],np.uint64),shutter_type=ShutterType.GLOBAL,principal_point=K[:2,2].astype(np.float32),focal_length=np.array([K[0,0],K[1,1]],np.float32),radial_coeffs=np.zeros(6,np.float32),tangential_coeffs=np.zeros(2,np.float32),thin_prism_coeffs=np.zeros(4,np.float32)))
 mw.store_camera_masks(cam,{});cw=reg(CameraSensorComponent,cam)
 for i in indices:
  image=Image.open(croot/f'{i:02d}.jpg').convert('RGB').resize((1024,576),Image.Resampling.LANCZOS);stream=io.BytesIO();image.save(stream,format='JPEG',quality=95);ts=int(us(ct[i]));cw.store_frame(image_binary_data=stream.getvalue(),image_format='jpeg',frame_timestamps_us=np.array([ts,ts],np.uint64),generic_data={},generic_meta_data={})
 meta[cam]={'C':C,'times':ct,'K':K,'camera_to_rig':fixed.tolist()}
 print('CAMERA_WRITTEN',cam,receipt['camera_pose_approximation'][cam],flush=True)
paths=writer.finalize();reader=SequenceComponentGroupsReader(paths);(out/'pandaset-001.json').write_text(json.dumps(reader.get_sequence_meta().to_dict(),indent=2)+'\n')
# LiDAR is already in world coordinates (official devkit geometry.projection).
# Exclude validation-frame scans; project into calibrated RGB to color the seed.
points=[];colors=[];source_frames=[]
for i in indices[1::4]:
 with gzip.open(scene/'lidar'/f'{i:02d}.pkl.gz','rb') as f:df=Restricted(f).load()
 p=df[['x','y','z']].to_numpy();valid=np.isfinite(p).all(axis=1)&(np.linalg.norm(p-rig[i,:3,3],axis=1)<90);p=p[valid][::2];rgb=np.zeros((len(p),3));assigned=np.zeros(len(p),bool)
 for cam in cameras:
  m=meta[cam];C=m['C'][i];q=(p-C[:3,3])@C[:3,:3];K=m['K'];z=q[:,2];u=K[0,0]*q[:,0]/np.maximum(z,1e-6)+K[0,2];v=K[1,1]*q[:,1]/np.maximum(z,1e-6)+K[1,2];sel=(z>.5)&(u>=0)&(u<1024)&(v>=0)&(v<576)&~assigned
  im=np.array(Image.open(scene/'camera'/cam/f'{i:02d}.jpg').resize((1024,576)));rgb[sel]=im[v[sel].astype(int),u[sel].astype(int)]/255.;assigned[sel]=True
 points.append(p[assigned]);colors.append(rgb[assigned]);source_frames.append(int(i))
p=np.concatenate(points);c=np.concatenate(colors);_,keep=np.unique(np.floor(p/.18).astype(np.int64),axis=0,return_index=True);p=p[keep];c=c[keep]
if len(p)>320000:keep=np.random.default_rng(7).choice(len(p),320000,replace=False);p=p[keep];c=c[keep]
fields=[(n,'f4') for n in ['x','y','z','nx','ny','nz','f_dc_0','f_dc_1','f_dc_2','opacity','scale_0','scale_1','scale_2','rot_0','rot_1','rot_2','rot_3']];a=np.zeros(len(p),dtype=fields)
for j,k in enumerate(['x','y','z']):a[k]=p[:,j]
for j in range(3):a[f'f_dc_{j}']=(c[:,j]-.5)/.28209479177387814;a[f'scale_{j}']=np.log(.12)
a['opacity']=1;a['rot_0']=1
header='ply\nformat binary_little_endian 1.0\nelement vertex '+str(len(a))+'\n'+'\n'.join('property float '+n for n in a.dtype.names)+'\nend_header\n'
with (root/'seed.ply').open('wb') as f:f.write(header.encode());f.write(a.tobytes())
# Estimate a local road plane for the display mesh, without inventing its height.
with gzip.open(scene/'lidar/30.pkl.gz','rb') as f:road=Restricted(f).load()[['x','y','z']].to_numpy()
road=(road-rig[30,:3,3])@rig[30,:3,:3];patch=road[(road[:,0]>3)&(road[:,0]<12)&(abs(road[:,1])<1.5)]
A=np.column_stack([patch[:,:2],np.ones(len(patch))]);coef=np.linalg.lstsq(A,patch[:,2],rcond=None)[0]
for _ in range(3):
 error=abs(A@coef-patch[:,2]);ok=error<np.quantile(error,.8);coef=np.linalg.lstsq(A[ok],patch[ok,2],rcond=None)[0]
(root/'ground-plane.json').write_text(json.dumps({'forward_slope':float(coef[0]),'left_slope':float(coef[1]),'height_at_rig_m':float(coef[2]),'reference_lidar_frame':30,'plane_rms_m':float(np.sqrt(np.mean((A[ok]@coef-patch[ok,2])**2))),'scope':'static robust fit of observed road patch 3-12m ahead, not per-frame contact physics'},indent=2)+'\n')
receipt.update(seed_gaussians=len(a),seed_lidar_frames=source_frames,camera_count=6,image_count=len(indices)*6,seed_source='measured real LiDAR in world coordinates, colored by real camera RGB; 0.18m voxel subset; no synthetic depth')
(root/'prepared.json').write_text(json.dumps(receipt,indent=2)+'\n');(root/'camera-calibrations.json').write_text(json.dumps({cam:{'K':m['K'].tolist(),'camera_to_rig':m['camera_to_rig']} for cam,m in meta.items()},indent=2)+'\n');print('PREPARED',receipt,flush=True)
