"""Create viewer alignment and an ego path from RGB-derived COLMAP geometry.

No original sensor poses or depth are read. Metric scale is not observable from
uncalibrated RGB alone. We normalize the estimated camera-to-road distance to
one viewer unit; the car's relative size is a display convention, not metrology.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import pycolmap as c
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--front-folder',default='front_camera');p.add_argument('--capture-fps',type=float,default=10);a=p.parse_args();r=a.root;out=a.output;out.mkdir(parents=True,exist_ok=True)
model=c.Reconstruction(str(r/'undistorted/sparse/0'));front=sorted([im for im in model.images.values() if im.name.split('/')[0]==a.front_folder],key=lambda im:im.name)
if len(front)<3:raise ValueError('Choose a front-facing image folder with at least three registered frames')
def pose(im):
 m=np.eye(4);m[:3]=im.cam_from_world().matrix();return np.linalg.inv(m)
C=np.array([pose(im) for im in front]);up=np.median(-C[:,:3,1],axis=0);up/=np.linalg.norm(up);forward=np.median(C[:,:3,2],axis=0);forward-=up*forward.dot(up);forward/=np.linalg.norm(forward);left=np.cross(up,forward);left/=np.linalg.norm(left)
# Candidate road correspondences are actual triangulated points observed in the
# central lower part of the front RGB images; no provided road plane is loaded.
ids=set()
for im in front:
 cam=model.cameras[im.camera_id]
 for pt in im.points2D:
  x,y=pt.xy
  if .15*cam.width<x<.85*cam.width and .60*cam.height<y<.95*cam.height and pt.point3D_id in model.points3D:
   point=model.points3D[pt.point3D_id]
   if point.error<2 and point.track.length()>=3:ids.add(pt.point3D_id)
if len(ids)<30:raise ValueError('Not enough RGB-derived road features to align a ground plane; capture textured road or choose another clip')
P=np.array([model.points3D[i].xyz for i in ids]);center=np.median(C[:,:3,3],axis=0);depth=np.median(np.linalg.norm(P-center,axis=1));threshold=max(depth*.004,1e-5);rng=np.random.default_rng(17);best=None
for _ in range(1600):
 q=P[rng.choice(len(P),3,replace=False)];n=np.cross(q[1]-q[0],q[2]-q[0]);length=np.linalg.norm(n)
 if length<1e-10:continue
 n/=length
 if abs(n.dot(up))<math.cos(math.radians(18)):continue
 if n.dot(up)<0:n=-n
 d=-n.dot(q[0]);inside=np.abs(P@n+d)<threshold;score=int(inside.sum())
 if best is None or score>best[0]:best=(score,n,d,inside)
if best is None or best[0]<25:raise ValueError('Could not fit a defensible road plane from RGB features')
Q=P[best[3]];mean=Q.mean(axis=0);_,_,vh=np.linalg.svd(Q-mean,full_matrices=False);n=vh[-1]
if n.dot(up)<0:n=-n
d=-n.dot(mean);heights=C[:,:3,3]@n+d;height=float(np.median(heights))
if height<=0:raise ValueError('Estimated road plane lies above the camera')
forward-=n*forward.dot(n);forward/=np.linalg.norm(forward);left=np.cross(n,forward);left/=np.linalg.norm(left);R=np.stack([forward,left,n]);origin=C[len(C)//2,:3,3]-n*heights[len(C)//2];scale=1/height
T=np.eye(4);T[:3,:3]=R*scale;T[:3,3]=-R@origin*scale
rows=[]
for im,M,h in zip(front,C,heights):
 position=(R@(M[:3,3]-origin))*scale;ground=position.copy();ground[2]-=h*scale;direction=R@M[:3,2];yaw=math.atan2(direction[1],direction[0]);rot=R@M[:3,:3];cam=model.cameras[im.camera_id];K=cam.calibration_matrix()
 try:seconds=int(Path(im.name).stem)/a.capture_fps
 except ValueError:seconds=len(rows)/a.capture_fps
 rows.append({'image':im.name,'time_seconds':seconds,'camera_position':position.tolist(),'camera_rotation_opencv':rot.tolist(),'ground_position':ground.tolist(),'yaw_radians':yaw,'K':K.tolist(),'image_size':[cam.width,cam.height]})
geometry={'schema':1,'world_to_viewer':T.tolist(),'up_axis':'Z','units':'normalized camera-height units; not measured meters','scale_assumption':'RGB/SfM scale is ambiguous. Median estimated camera-to-road distance is normalized to 1. Vehicle scale 1/1.8 is a display proportion, not a measurement.','road_plane_source':'RANSAC + least-squares on triangulated RGB feature tracks in lower front-camera image regions','road_plane_candidates':len(P),'road_plane_inliers':len(Q),'road_plane_rms_viewer_units':float(np.sqrt(np.mean((Q@n+d)**2))*scale),'source_camera':'COLMAP estimated intrinsics and camera poses; no source dataset calibration or poses','frames':rows,'vehicle':{'file':'volvo-s90.glb','scale':1/1.8,'model_axis':'glTF Y-up, nose +X; rotate +90 degrees around X into viewer Z-up','role':'added ego-position reference; not the original capture vehicle or an OEM dynamics model'},'default_frame':len(rows)//2}
(out/'cameras.json').write_text(json.dumps(geometry,indent=2)+'\n');print('VIEWER_GEOMETRY',len(rows),'front poses; plane',len(Q),'inliers; RMS',geometry['road_plane_rms_viewer_units'],flush=True)
