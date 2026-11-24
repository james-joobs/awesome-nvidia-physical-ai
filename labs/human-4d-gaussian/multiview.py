"""SOMA motion -> public 4DAnyone video conditioning (no SMPL assets).

This is an original adapter, NOT GVHMR/SMPL-X inference. Source RGB is observed;
every target-view RGB produced by the video model is synthetic supervision.
The released 4DAnyone base model/renderer/conditioning API is left unchanged.
"""
import argparse, json, logging, sys, time, hashlib
from dataclasses import asdict
from pathlib import Path
import numpy as np
from PIL import Image

p=argparse.ArgumentParser()
p.add_argument('--root',type=Path,required=True)
p.add_argument('--start',type=int,default=0)
p.add_argument('--views',type=int,default=6)
p.add_argument('--name',default='pilot')
p.add_argument('--start-yaw',type=int,default=0)
p.add_argument('--seed',type=int,default=42);p.add_argument('--turbo',action='store_true');p.add_argument('--rcp',action='store_true')
p.add_argument('--prepare-only',action='store_true')
p.add_argument('--white-source',action='store_true')
a=p.parse_args();r=a.root;work=r/'multiview-prior';sys.path.insert(0,str(work/'4danyone'))
from fdanyone.skeleton.pipeline import Conditioning, SkeletonVideo
from fdanyone.skeleton.keypoints import KEYPOINT_NAMES
from fdanyone.skeleton.renderer import render_goliath40, estimate_body_height, projected_body_scales
from fdanyone.geometry.cameras import camera_grid, camera_ring, project_points, reference_intrinsics
from fdanyone.geometry.crop import Crop, crop_from_bounds, mask_bounds, transform_intrinsics
from fdanyone.video import write_video
from fdanyone.views import resolve_view_plan
from fdanyone.config import INFERENCE, BASE24, RANK64_DELTA4

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
out=work/a.name;out.mkdir(exist_ok=True,parents=True)
# A cached video belongs to an exact source, camera plan and inference profile.
# Earlier conditioning-only caches may be recalculated; unproven generated RGB
# is never silently adopted as the requested experiment.
request={'start':a.start,'views':a.views,'start_yaw':a.start_yaw,'turbo':a.turbo,'rcp':a.rcp,'white_source':a.white_source,'seed':a.seed,'input_sha256':hashlib.sha256((r/'input.json').read_bytes()).hexdigest(),'geometry_sha256':hashlib.sha256((r/'rig/geometry.npz').read_bytes()).hexdigest()}
request_file=out/'request.json'
if request_file.exists():
 if json.loads(request_file.read_text())!=request:raise ValueError('Existing multiview cache has a different input/start/camera plan/profile; use a new interval name or output root')
elif (out/'generation.json').exists() or (out/'generated').exists():raise ValueError('Generated cache has no request fingerprint; preserve it and use a new interval name')
request_file.write_text(json.dumps(request,indent=2)+'\n')
condition_root=out/'conditioning';condition_root.mkdir(exist_ok=True)
g=np.load(r/'rig/geometry.npz');names=json.loads((r/'rig/rig.json').read_text())['public_joint_names'];lookup={n:i for i,n in enumerate(names)}
if not 0 <= a.start < len(g['joints']):raise ValueError('start must identify an existing normalized frame')
valid_frames=min(121,len(g['joints'])-a.start)
# Diffusion requires 121 frames; pad only the final incomplete window.
ids=np.minimum(np.arange(a.start,a.start+121),len(g['joints'])-1)
j=g['joints'][ids].copy();v=g['vertices'][ids]
# SOMA camera axes -> upright human world, retaining the actual source motion.
# Use the same estimated coordinate frame for every interval. The seed
# definition remains unchanged; later intervals read that seed's origin.
seed_conditioning=work/'pilot/soma-conditioning.npz'
if a.start and seed_conditioning.is_file():
 origin=np.load(seed_conditioning)['world_origin'].copy()
else:
 origin=g['joints'][0,0].copy();origin[1]=float(np.quantile(g['vertices'][:min(121,len(g['vertices'])),:,[1]],.995))
S=np.diag([1.,-1.,-1.]);world=(j-origin)@S
kps=np.zeros((121,70,3),np.float32)
def at(name):return world[:,lookup[name]]
direct={'left-eye':'LeftEye','right-eye':'RightEye','left-shoulder':'LeftArm','right-shoulder':'RightArm','left-elbow':'LeftForeArm','right-elbow':'RightForeArm','left-hip':'LeftLeg','right-hip':'RightLeg','left-knee':'LeftShin','right-knee':'RightShin','left-ankle':'LeftFoot','right-ankle':'RightFoot','left-wrist':'LeftHand','right-wrist':'RightHand','neck':'Neck1'}
for i,n in enumerate(KEYPOINT_NAMES):
 if n in direct:kps[:,i]=at(direct[n])
 for side in ['left','right']:
  prefix=side.title()
  if n.startswith(side+'-') and any(t in n for t in ['thumb','index','middle','ring','pinky']):
   finger=n.split('-')[1].title();suffix=n.split('-')[2]
   digit={'tip':'End','first':'1','second':'2','third':'3'}[suffix]
   kps[:,i]=at(prefix+'Hand'+finger+digit)
  if n==side+'-big-toe-tip' or n==side+'-small-toe-tip':kps[:,i]=at(prefix+'ToeEnd')
  if n==side+'-heel':kps[:,i]=at(prefix+'Foot')+.3*(at(prefix+'Foot')-at(prefix+'ToeEnd'))
  if n==side+'-olecranon' or n==side+'-cubital-fossa':kps[:,i]=at(prefix+'ForeArm')
  if n==side+'-acromion':kps[:,i]=at(prefix+'Arm')
# Sparse face/ear hints come from the already fitted SOMA mesh, not a new face model.
head=at('Head');eyes=(at('LeftEye')+at('RightEye'))/2
side=at('LeftEye')-at('RightEye');side/=np.maximum(np.linalg.norm(side,axis=-1,keepdims=True),1e-5)
up=at('HeadEnd')-at('Head');up/=np.maximum(np.linalg.norm(up,axis=-1,keepdims=True),1e-5)
front=np.cross(side,up);front/=np.maximum(np.linalg.norm(front,axis=-1,keepdims=True),1e-5)
if front[0,2]<0:front=-front
for n,pts in [('nose',eyes-.02*up+.032*front),('left-ear',head+.068*side),('right-ear',head-.068*side)]:kps[:,KEYPOINT_NAMES.index(n)]=pts
assert np.isfinite(kps).all()
plan=resolve_view_plan(views_per_layer=a.views,layer_pitches=[0],start_yaw=a.start_yaw,yaw_span=360,enable_rcp=a.rcp,enable_tcr=True)
H,W=1280,704;K=reference_intrinsics(H,W)
body_height=estimate_body_height(kps,KEYPOINT_NAMES)
center=np.array([0.,body_height*.52,0.]);radius=max(2.7,body_height*1.85)
cameras=camera_grid(center=center,front_direction=np.array([0.,0.,-1.]),K=K,image_height=H,image_width=W,views_per_layer=a.views,layer_pitches=(0,),start_yaw=a.start_yaw,yaw_span=360,radius=radius,target_height=center[1])
crop=Crop(0,0,H,W,H,W,H,W)
target_skeletons=[];camera_rows=[]
for camera in cameras:
 path=condition_root/f'skeleton-{camera.camera_id:02d}.mp4'
 xy,depth=[],[]
 for frame in kps:
  pt,z,_=project_points(frame,camera);xy.append(pt);depth.append(z)
 scales=projected_body_scales(np.asarray(depth),KEYPOINT_NAMES,body_height,float(K[0,0]))
 if not path.exists():
  def frames():
   for t in range(121):yield render_goliath40(xy[t],depth[t],np.ones(70),canvas_height=H,canvas_width=W,output_height=H,output_width=W,body_scale_px=float(scales[t]))
  write_video(frames(),path,30,crf=17,preset='fast')
 target_skeletons.append(SkeletonVideo(path,crop));camera_rows.append(camera.to_dict())
 print('SOMA_CONDITIONING_VIEW',camera.camera_id,flush=True)
rcp_skeletons=[]
ring=camera_ring(center=center,front_direction=np.array([0.,0.,-1.]),K=K,image_height=H,image_width=W,radius=radius,target_height=center[1],layer_index=-1)
for cid in plan.rcp_camera_ids:
 camera=ring[cid];path=condition_root/f'rcp-{cid:02d}.mp4'
 xy,depth=[],[]
 for frame in kps:
  pt,z,_=project_points(frame,camera);xy.append(pt);depth.append(z)
 scales=projected_body_scales(np.asarray(depth),KEYPOINT_NAMES,body_height,float(K[0,0]))
 if not path.exists():
  def frames():
   for t in range(121):yield render_goliath40(xy[t],depth[t],np.ones(70),canvas_height=H,canvas_width=W,output_height=H,output_width=W,body_scale_px=float(scales[t]))
  write_video(frames(),path,30,crf=17,preset='fast')
 rcp_skeletons.append(SkeletonVideo(path,crop));print('RCP_READY',cid,flush=True)

masks=np.stack([np.asarray(Image.open(r/f'masks/{i+1:06d}.png')) for i in ids])
source_crop=crop_from_bounds(bounds=mask_bounds(masks,.5),image_height=960,image_width=540,output_height=H,output_width=W,margins=(.04,.08,.04,.08),allow_upscale=True)
source_path=condition_root/'source.mp4'
if not source_path.exists():
 def source_frames():
  for t,i in enumerate(ids):
   rgb=np.asarray(Image.open(r/f'frames/{i+1:06d}.jpg').convert('RGB'))
   if a.white_source:rgb=np.where((masks[t]>0)[...,None],rgb,240).astype(np.uint8)
   yield rgb
 write_video(source_frames(),source_path,30,crf=16,preset='fast')
np.savez_compressed(out/'soma-conditioning.npz',keypoints_world=kps,world_origin=origin,cv_to_world=S,frame_ids=ids)
payload={'adapter':'GEM-X/SOMA -> Goliath40 hints; no GVHMR/SMPL-X assets','source_frames':ids.tolist(),'valid_frames':valid_frames,'common_world_origin':True,'source_rgb':'observed; optional white background', 'target_rgb':'generated, not observed or ground truth','front_direction_from_initial_pose':True,'body_height_model_m':body_height,'cameras':camera_rows,'source_crop':asdict(source_crop),'source_K':g['K'][a.start].tolist(),'source_input_size':[json.loads((r/'input.json').read_text())['width'],json.loads((r/'input.json').read_text())['height']],'view_plan':plan.to_dict(),'face_hints':'approximate existing SOMA eye/head joints; no face recognition','white_source':a.white_source}
(out/'adapter.json').write_text(json.dumps(payload,indent=2)+'\n')
conditioning=Conditioning(root=condition_root,source_video=source_path,source_crop=source_crop,target_skeletons=tuple(target_skeletons),rcp_skeletons=tuple(rcp_skeletons),view_plan=plan,fps_num=30,fps_den=1,num_frames=121)
if a.prepare_only:raise SystemExit(0)
from fdanyone.assets import BaseAssets, resolve_turbo_lora
from fdanyone.model.inference import generate_views
import torch
torch.set_num_threads(8)
model_dir=work/'models/4danyone';started=time.time()
generated=generate_views(conditioning=conditioning,checkpoint_path=model_dir/'model.safetensors',turbo_lora_path=resolve_turbo_lora(model_dir=work/'models') if a.turbo else None,denoising_profile=RANK64_DELTA4 if a.turbo else BASE24,attention_backend='sdpa',assets=BaseAssets(model_dir/'Wan2.2_VAE.pth',model_dir/'prompt_context.safetensors'),output_dir=out/'generated',devices=('cuda:0',),seed=a.seed)
result={**asdict(generated),'total_wall_seconds':time.time()-started}
(out/'generation.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
print('SYNTHETIC_VIEWS_READY',json.dumps(result,default=str),flush=True)
