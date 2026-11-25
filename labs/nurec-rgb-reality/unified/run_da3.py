"""RGB-only joint camera/depth inference with the Apache-2.0 DA3-BASE.

Unlike the earlier geometry-loss experiment, no SfM intrinsics/extrinsics are
provided to this forward pass. Checkpoint terms differ across DA3 variants.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from huggingface_hub import snapshot_download
from depth_anything_3.api import DepthAnything3

REPO='depth-anything/DA3-BASE'
REVISION='f4a6c9b3c95e41c82048423d3493a81ec3fa810e'


def main():
    p=argparse.ArgumentParser();p.add_argument('--images',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--frames',type=int,default=17);p.add_argument('--resolution',type=int,default=756);p.add_argument('--ray-pose',action='store_true');p.add_argument('--camera-priors',type=Path,help='Optional prior lab RGB/SfM estimates, never source sensor calibration');a=p.parse_args()
    if a.out.exists():raise ValueError('Choose a fresh output directory')
    a.out.mkdir(parents=True)
    paths=sorted(x for x in a.images.iterdir() if x.suffix.lower() in {'.jpg','.png','.jpeg'})[:a.frames]
    if len(paths)!=a.frames:raise ValueError('Insufficient distinct frames')
    checkpoint=Path(snapshot_download(REPO,revision=REVISION,allow_patterns=['config.json','model.safetensors','README.md']))
    model=DepthAnything3.from_pretrained(checkpoint).to('cuda').eval()
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();start=time.perf_counter()
    kwargs={}
    if a.camera_priors:
        calibration=json.loads(a.camera_priors.read_text())
        if calibration.get('uses_lidar') or calibration.get('uses_supplied_calibration') or calibration.get('uses_supplied_poses'):raise ValueError('RGB-only camera priors required')
        by_name={r['image']:r for r in calibration['frames']};poses=[];intrinsics=[]
        for path in paths:
            timestamp,camera=path.stem.split('-',1);row=by_name[f'{camera}/{timestamp}.jpg'];w,h=Image.open(path).size
            intrinsics.append(np.diag([w/row['width'],h/row['height'],1.])@row['K']);poses.append(row['camera_to_world'])
        kwargs={'extrinsics':np.linalg.inv(np.array(poses,dtype=np.float32)),'intrinsics':np.array(intrinsics,dtype=np.float32),'align_to_input_ext_scale':True}
    with torch.inference_mode():
        pred=model.inference([str(x) for x in paths],process_res=a.resolution,process_res_method='upper_bound_resize',use_ray_pose=a.ray_pose,**kwargs)
    torch.cuda.synchronize();seconds=time.perf_counter()-start
    C=np.linalg.inv(np.concatenate([pred.extrinsics,np.broadcast_to([0,0,0,1],(a.frames,1,4))],axis=1))
    rgb=pred.processed_images
    t,h,w=pred.depth.shape;y,x=np.mgrid[:h,:w]
    pixels=np.stack([x,y,np.ones_like(x)],axis=-1)
    rays=np.einsum('hwj,tkj->thwk',pixels,np.linalg.inv(pred.intrinsics))
    camera_points=rays*pred.depth[...,None]
    points=np.einsum('thwj,tkj->thwk',camera_points,C[:,:3,:3])+C[:,None,None,:3,3]
    arrays={'observed_rgb':rgb,'depth':pred.depth,'confidence':pred.conf,'intrinsics':pred.intrinsics,'camera_pose':C,'pointmap':points}
    for k,v in arrays.items():
        if not np.isfinite(v).all():raise RuntimeError(f'Nonfinite {k}')
    np.savez_compressed(a.out/'geometry.npz',**arrays)
    receipt={'schema':1,'model':REPO,'revision':REVISION,'weights_sha256':hashlib.file_digest((checkpoint/'model.safetensors').open('rb'),'sha256').hexdigest(),'license':'Apache-2.0','input':'RGB + optional camera priors estimated from RGB/SfM; no sensor calibration, LiDAR or supplied depth' if a.camera_priors else 'RGB only; no camera, depth, LiDAR or SfM priors','rgb_camera_priors_sha256':hashlib.file_digest(a.camera_priors.open('rb'),'sha256').hexdigest() if a.camera_priors else None,'depth_units':'relative, not measured meters','use_ray_pose':a.ray_pose,'resolution':a.resolution,'frames':a.frames,'timing':{'inference_seconds':seconds,'frames_per_second_offline':a.frames/seconds,'peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'peak_reserved_gib':torch.cuda.max_memory_reserved()/2**30},'device':torch.cuda.get_device_name(),'torch':torch.__version__,'source_records':[{'name':x.name,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in paths],'output_shapes':{k:list(v.shape) for k,v in arrays.items()}}
    (a.out/'run.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt['timing']),flush=True)


if __name__=='__main__':main()
