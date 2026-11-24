"""Infer training-only RGB depth, align it to SfM, and derive normal priors.

Priors are predictions, not measured depth or new sensor observations. Both
supported checkpoints declare Apache-2.0; larger DA3 any-view checkpoints have
different terms and are deliberately not selected by this runner.
"""
import argparse, hashlib, json, time
from collections import defaultdict
from pathlib import Path
import cv2
import numpy as np
import torch
from huggingface_hub import snapshot_download, model_info
from depth_anything_3.api import DepthAnything3
from geometry import align_depth, normals_from_z

MODELS={
    'base':('depth-anything/DA3-BASE','f4a6c9b3c95e41c82048423d3493a81ec3fa810e'),
    'mono':('depth-anything/DA3MONO-LARGE','f465978e618db8cc79c83b8bbf24964857db1875'),
}


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--model',choices=MODELS,default='base');p.add_argument('--perception',type=Path);p.add_argument('--resolution',type=int,default=756);a=p.parse_args()
    root=a.root;rows=json.loads((root/'rgb-cameras.json').read_text())['frames'];split=json.loads((root/'split.json').read_text())
    assert all(r['timestamp_us'] not in split['held_out_timestamp_us'] for r in rows)
    repo,revision=MODELS[a.model];info=model_info(repo,revision=revision,files_metadata=True)
    assert info.card_data.license=='apache-2.0'
    path=Path(snapshot_download(repo,revision=revision,allow_patterns=['config.json','model.safetensors','README.md']))
    checksum=hashlib.file_digest((path/'model.safetensors').open('rb'),'sha256').hexdigest()
    expected=next(f.lfs.sha256 for f in info.siblings if f.rfilename=='model.safetensors')
    assert checksum==expected,'Depth checkpoint checksum mismatch'
    model=DepthAnything3.from_pretrained(path).to('cuda').eval();torch.cuda.reset_peak_memory_stats()
    points=np.load(root/'sfm-points.npz')['xyz'];tracks=defaultdict(list)
    for image,uv,idx in json.loads((root/'training-tracks.json').read_text()):tracks[image].append((uv,idx))
    exclusions={}
    if a.perception:
        detections=json.loads(a.perception.read_text())
        for frame in detections['frames']:
            for camera,view in frame['views'].items():exclusions[(camera,str(Path(view['image']).stem))]=view['detections']
    output=root/('priors-'+a.model);output.mkdir(exist_ok=True);receipts=[];start=time.perf_counter()
    for camera in sorted({r['camera'] for r in rows}):
        group=sorted([r for r in rows if r['camera']==camera],key=lambda r:r['timestamp_us'])
        paths=[str(root/'rgb'/r['image']) for r in group]
        kwargs={'process_res':a.resolution,'process_res_method':'upper_bound_resize'}
        if a.model=='base':
            kwargs.update(extrinsics=np.array([np.linalg.inv(r['camera_to_world']) for r in group],np.float32),intrinsics=np.array([r['K'] for r in group],np.float32),align_to_input_ext_scale=True)
        with torch.inference_mode():prediction=model.inference(paths,**kwargs)
        for index,r in enumerate(group):
            h,w=r['height'],r['width'];K=np.array(r['K']);C=np.array(r['camera_to_world']);raw=cv2.resize(prediction.depth[index],(w,h),interpolation=cv2.INTER_LINEAR)
            valid=np.isfinite(raw)&(raw>0)
            if prediction.conf is not None:
                conf=cv2.resize(prediction.conf[index],(w,h),interpolation=cv2.INTER_LINEAR)
                valid &= conf>=np.percentile(conf[np.isfinite(conf)],20)
            excluded=np.zeros((h,w),bool)
            for d in exclusions.get((camera,Path(r['image']).stem),[]):
                x0,y0,x1,y1=d['bbox'];x0=max(0,int(x0)-4);x1=min(w,int(np.ceil(x1))+4);y0=max(0,int(y0)-4);y1=min(h,int(np.ceil(y1))+4);excluded[y0:y1,x0:x1]=True
            valid &= ~excluded
            items=tracks[r['image']];uv=np.array([q[0] for q in items]);ids=np.array([q[1] for q in items]);xy=np.rint(uv).astype(int)
            inbounds=(xy[:,0]>=0)&(xy[:,0]<w)&(xy[:,1]>=0)&(xy[:,1]<h);xy,ids=xy[inbounds],ids[inbounds]
            keep=valid[xy[:,1],xy[:,0]];xy,ids=xy[keep],ids[keep]
            z=((points[ids]-C[:3,3])@C[:3,:3])[:,2]
            scale,shift,fit=align_depth(raw[xy[:,1],xy[:,0]],z)
            depth=(raw*scale+shift).astype(np.float32)
            max_depth=min(200.,float(np.percentile(z[z>0],97))*1.5)
            valid &= (depth>.15)&(depth<max_depth)
            smooth=cv2.GaussianBlur(depth,(5,5),.8)
            normals,rays=normals_from_z(smooth,K,valid)
            world_normals=normals@C[:3,:3].T
            distance=depth*np.linalg.norm(rays,axis=-1);distance[~valid]=0
            destination=output/camera/f"{r['timestamp_us']}.npz";destination.parent.mkdir(exist_ok=True)
            np.savez_compressed(destination,distance=distance.astype(np.float32),normals=world_normals.astype(np.float32))
            receipts.append({'image':r['image'],'timestamp_us':r['timestamp_us'],'scale':scale,'shift':shift,**fit,'valid_depth_fraction':float(valid.mean()),'valid_normal_fraction':float((np.linalg.norm(normals,axis=-1)>.5).mean()),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()})
        print('PRIORS_CAMERA',a.model,camera,len(group),flush=True)
    torch.cuda.synchronize()
    report={'schema':1,'model':repo,'revision':revision,'weights_sha256':checksum,'model_license':'Apache-2.0','source_revision':'3d835ec1a5802d64a8b8b15f817a1ab54809bfe4','images':len(receipts),'held_out_images_used':0,'uses_lidar':False,'depth_source':'Predicted from training RGB only; robust scale/shift aligned to RGB-triangulated training observations','normals_source':'Finite differences of smoothed predicted z-depth, camera-facing, transformed to the existing world frame','scope':'Priors and confidences are estimates, not ground truth. Camera poses were estimated offline from all RGB views.','resolution_long_side':a.resolution,'seconds':time.perf_counter()-start,'torch_peak_allocated_gib':torch.cuda.max_memory_allocated()/2**30,'frames':receipts}
    (root/f'priors-{a.model}.json').write_text(json.dumps(report,indent=2)+'\n');print('PRIORS_COMPLETE',a.model,len(receipts),flush=True)


if __name__=='__main__':main()
