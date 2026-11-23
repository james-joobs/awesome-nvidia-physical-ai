"""RGB-only camera adapter and explicitly assumed metric history for Alpamayo.

Four real RGB streams supply six virtual slots. Rear subviews and front tele are
rotation/crop resamples of recorded pixels, never generated scene content.
This is a documented camera-layout/domain adaptation, not the native AV profile.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.spatial.transform import Rotation,Slerp
from scipy.signal import savgol_filter
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--assumed-camera-height-m',type=float,required=True);p.add_argument('--times',type=float,nargs='+',default=[2.1,3.9,5.7,7.8]);a=p.parse_args();root=a.root
if not .5<a.assumed_camera_height_m<4:raise ValueError('Use an explicit plausible camera-height assumption in meters; this is not measured by RGB')
meta=json.loads((root/'rgb-cameras.json').read_text());front=sorted((r for r in meta['frames'] if r['camera']=='front_camera'),key=lambda r:r['timestamp_us']);times=np.array([(r['timestamp_us']-1000000)/1e6 for r in front]);C=np.array([r['camera_to_world'] for r in front]);F=np.array([[0,0,1,0],[-1,0,0,0],[0,-1,0,1],[0,0,0,1]],float);rig=C@np.linalg.inv(F)
ground=np.array([f['ground_position'] for f in meta['front_poses']]);yaw=savgol_filter(np.unwrap([f['yaw_radians'] for f in meta['front_poses']]),7,2);positions=savgol_filter(ground,7,2,axis=0);positions[:,2]=0;rotations=Slerp(times,Rotation.from_euler('z',yaw.reshape(-1,1)));by_cam={c:sorted((r for r in meta['frames'] if r['camera']==c),key=lambda r:r['timestamp_us']) for c in ['front_camera','left_camera','right_camera','back_camera']}
slots={0:('left_camera',0,1),1:('front_camera',0,1),2:('right_camera',0,1),3:('back_camera',15,2.4),5:('back_camera',-15,2.4),6:('front_camera',0,2)}
def resample(row,yaw,zoom):
 im=np.array(Image.open(root/'rgb'/row['image']).convert('RGB'));H,W=im.shape[:2];K=np.array(row['K'])
 if zoom==1 and yaw==0:return Image.fromarray(im).resize((1024,576),Image.Resampling.LANCZOS)
 target=K.copy();target[0,0]*=zoom;target[1,1]*=zoom;target[0,2]=W/2;target[1,2]=H/2;yy,xx=np.mgrid[:H,:W];rays=np.stack([xx,yy,np.ones_like(xx)],axis=-1)@np.linalg.inv(target).T;Q=Rotation.from_euler('y',yaw,degrees=True).as_matrix();rays=rays@Q.T;uv=rays@K.T;u=uv[...,0]/uv[...,2];v=uv[...,1]/uv[...,2]
 if np.min(u)<0 or np.max(u)>W-1 or np.min(v)<0 or np.max(v)>H-1:raise ValueError('Virtual subview reaches outside observed RGB; reduce yaw or increase zoom')
 rgb=np.stack([map_coordinates(im[...,c],[v,u],order=1,mode='nearest') for c in range(3)],axis=-1).astype('uint8');return Image.fromarray(rgb).resize((1024,576),Image.Resampling.LANCZOS)
receipts=[]
for t0 in a.times:
 if t0<times[0]+2 or t0>times[-1]+1e-6:raise ValueError('Policy keyframe lacks two seconds of past RGB')
 dest=root/'policy'/f'{round(t0*10):03d}';dest.mkdir(parents=True,exist_ok=True);shots=[]
 hist= t0+np.arange(-19,1)/10;pos=np.stack([np.interp(hist,times,positions[:,j]) for j in range(3)],axis=1);rot=rotations(hist).as_matrix();P0=np.array([np.interp(t0,times,positions[:,j]) for j in range(3)]);R0=rotations(t0).as_matrix();xyz=(pos-P0)@R0*a.assumed_camera_height_m;history_rot=np.einsum('ji,njk->nik',R0,rot)
 for slot,(camera,yaw,zoom) in slots.items():
  offsets=[-2,-1,-.5,-.1,0] if slot in {1,6} else [-1,-.1,0]
  for si,offset in enumerate(offsets):
   request=1000000+round((t0+offset)*1e6);available=[r for r in by_cam[camera] if r['timestamp_us']<=request];row=available[-1];file=f'camera-{slot}-{si}.jpg';resample(row,yaw,zoom).save(dest/file,quality=95);shots.append({'image':file,'camera_id':slot,'timestamp_us':row['timestamp_us']-1000000,'source_image':row['image'],'requested_time_seconds':t0+offset,'virtual_camera_yaw_deg':yaw,'virtual_camera_zoom':zoom})
 record={'schema':1,'t0_seconds':t0,'shots':shots,'history_xyz_m':xyz.tolist(),'history_rot':history_rot.tolist(),'world_anchor_position_relative_units':P0.tolist(),'world_anchor_rotation':R0.tolist(),'assumed_camera_height_m':a.assumed_camera_height_m,'scale_status':'assumed, not measured; RGB SfM has no absolute scale','history_source':'RGB-derived ground-projected positions and yaw-only body orientation; planar-road assumption; Savitzky-Golay smoothing and 10 Hz interpolation; no future labels','camera_profile':'4 physical RGB streams -> 6 virtual slots: actual left/front/right; two rear crops from back RGB; tele crop from front. Narrower FOV than the native training profile; no claim of native calibration or driving accuracy','time_source':'nominal source frame number / 10; causal previous-frame selection, not supplied sensor timestamps','navigation':'Continue straight on the road and yield to pedestrians.'};(dest/'input.json').write_text(json.dumps(record,indent=2)+'\n');receipts.append({'keyframe':dest.name,'t0_seconds':t0,'images':len(shots)})
(root/'policy-inputs.json').write_text(json.dumps({'assumed_camera_height_m':a.assumed_camera_height_m,'keyframes':receipts,'uses_lidar':False,'uses_source_ego_poses':False,'uses_future_labels':False},indent=2)+'\n');print('POLICY_RGB_INPUTS',receipts,flush=True)
