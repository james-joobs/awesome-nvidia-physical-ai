"""NuRec novel camera paths from the RGB-derived rig; retain exact source geometry."""
import argparse,copy,json,math
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root;rig=json.loads((root/'training-rig.json').read_text());sensor=next(k for k in rig['camera_calibrations'] if k.startswith('front_camera@'));template=rig['rig_trajectories'][0];source_times=template['cameras_frame_timestamps_us'][sensor];source_poses=template['cameras_frame_T_rig_worlds'][sensor];pairs=sorted(zip(source_times,source_poses),key=lambda row:row[0][0]);times=[p[0] for p in pairs];poses=[p[1] for p in pairs]
def cv_camera(eye,target):
 eye=np.array(eye,float);forward=np.array(target,float)-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(forward,right);C=np.eye(4);C[:3,:3]=np.column_stack([right,down,forward]);C[:3,3]=eye;return C
views=[]
for name in ['front','quarter','orbit']:
 d=copy.deepcopy(rig);t=copy.deepcopy(template);cal=copy.deepcopy(rig['camera_calibrations'][sensor]);F=np.array(cal['T_sensor_rig']);used_times=times;used_poses=poses
 if name=='quarter':cal['T_sensor_rig']=cv_camera([-3.4,-2.6,2.8],[.4,0,.5]).tolist()
 if name=='orbit':
  n=48;anchor=np.array(poses[len(poses)//2][0]);used_times=[[1000000+i*100000,1000000+i*100000] for i in range(n)];used_poses=[]
  for i in range(n):
   angle=2*math.pi*i/n;eye=[-4.0*math.cos(angle),-4.0*math.sin(angle),2.6];C=cv_camera(eye,[.3,0,.5]);M=anchor@C@np.linalg.inv(F);used_poses.append([M.tolist(),M.tolist()])
 if name!='front':
  pars=cal['camera_model']['parameters'];pars['focal_length']=[512,512];pars['principal_point']=[512,288];pars['resolution']=[1024,576];pars['external_distortion_parameters']=None
 t['cameras_frame_timestamps_us']={sensor:used_times};t['lidars_frame_timestamps_us']={};t['cameras_frame_T_rig_worlds']={sensor:used_poses};t['cameras_linear_start_frame_indices']={sensor:0};t['lidars_linear_start_frame_indices']={};t['T_rig_worlds']=[p[0] for p in used_poses];t['T_rig_world_timestamps_us']=[ts[0] for ts in used_times];d['rig_trajectories']=[t];d['camera_calibrations']={sensor:cal};d['lidar_calibrations']={};(root/f'rig-{name}.json').write_text(json.dumps(d,indent=2)+'\n');views.append({'view':name,'frames':len(used_times),'camera_to_rig':cal['T_sensor_rig'],'intrinsics':cal['camera_model']['parameters']})
(root/'view-paths.json').write_text(json.dumps({'sensor_id':sensor,'units':'relative camera-height units','views':views},indent=2)+'\n');print('NUREC_NOVEL_PATHS',[(v['view'],v['frames']) for v in views],flush=True)
