"""Persistent RGB-only background plus time-local foreground surfels.

Geometry comes from DA3, not a learned WorldVAE. RGB detector masks keep
foreground out of static history. These oriented samples are not trained 3DGS.
"""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

CAMERAS=['back_camera','front_camera','front_left_camera','front_right_camera','left_camera','right_camera']

def decode_mask(mask, size):
    bits=np.zeros(int(np.prod(mask['size'])),np.uint8);offset=0
    for i,count in enumerate(mask['counts']):
        bits[offset:offset+count]=i%2;offset+=count
    if offset!=len(bits):raise ValueError('RLE length mismatch')
    w,h=mask['size'];part=Image.fromarray(bits.reshape(h,w)*255).resize(tuple(mask['extent']),Image.Resampling.NEAREST)
    full=Image.new('L',size);full.paste(part,tuple(mask['origin']))
    return full

def foreground(view, size):
    mask=Image.new('L',tuple(view['image_size']))
    for detection in view['detections']:
        if detection['score']>=.7 and detection.get('mask'):
            part=decode_mask(detection['mask'],tuple(view['image_size']))
            mask=Image.fromarray(np.maximum(np.asarray(mask),np.asarray(part)))
    return np.asarray(mask.resize(size,Image.Resampling.NEAREST).filter(ImageFilter.MaxFilter(5)))>0

def unproject(depth,K,C,stride=1):
    y,x=np.mgrid[0:depth.shape[0]:stride,0:depth.shape[1]:stride];z=depth[::stride,::stride]
    rays=np.stack([(x-K[0,2])/K[0,0],(y-K[1,2])/K[1,1],np.ones_like(x)],-1)
    return (rays*z[...,None])@C[:3,:3].T+C[:3,3]

def fuse_voxels(points, colors, tangents, scores, voxel):
    key=np.floor(points/voxel).astype(np.int32)
    _,inverse=np.unique(key,axis=0,return_inverse=True);n=int(inverse.max())+1
    total=np.bincount(inverse,weights=scores,minlength=n)
    p=np.stack([np.bincount(inverse,weights=points[:,i]*scores,minlength=n)/total for i in range(3)],-1)
    c=np.stack([np.bincount(inverse,weights=colors[:,i]*scores,minlength=n)/total for i in range(3)],-1)
    order=np.lexsort((-scores,inverse));_,first=np.unique(inverse[order],return_index=True)
    return p.astype('f4'),np.rint(c).clip(0,255).astype('u1'),tangents[order[first]].astype('f4')

def write_cloud(path,points,colors,tangents):
    # Oriented footprint, not a camera-facing disk: xyz f32 + 2×xyz f16 + RGBA.
    record=np.zeros(len(points),dtype=[('position','<f4',(3,)),('tangents','<f2',(2,3)),('color','u1',(4,))])
    record['position']=points;record['tangents']=tangents;record['color'][:,:3]=colors;record['color'][:,3]=255
    path.write_bytes(record.tobytes())
    return {'file':path.name,'count':len(points),'stride_bytes':28,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--geometry',type=Path,required=True);p.add_argument('--scene',type=Path,required=True);p.add_argument('--perception',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--stride',type=int,default=3);p.add_argument('--voxel',type=float,default=.09);a=p.parse_args()
    if a.out.exists():raise ValueError('Preserve earlier experiments; select a fresh output directory')
    a.out.mkdir(parents=True);start=time.perf_counter()
    data=np.load(a.geometry);scene=json.loads(a.scene.read_text());detector=json.loads(a.perception.read_text())
    model=next(m for m in scene['models'] if m['id']=='calibrated')
    depth=data['depth']*model['alignment']['scale'];rgb=data['observed_rgb'];conf=data['confidence']
    if rgb.max()<=1:rgb=np.rint(rgb*255).astype('u1')
    poses=np.array(model['camera_to_world']);K=np.array(model['intrinsics']);N,H,W=depth.shape
    if N!=102:raise ValueError('This reproducible case expects 6 cameras × 17 times')
    masks=np.stack([foreground(detector['frames'][i//6]['views'][CAMERAS[i%6]],(W,H)) for i in range(N)])
    all_points=[];all_colors=[];all_radii=[];all_scores=[];actors=[];counts=[]
    for t in range(17):
        ap=[];ac=[];ar=[]
        for j in range(6):
            i=t*6+j;z=depth[i,::a.stride,::a.stride];c=conf[i,::a.stride,::a.stride]
            xyz=unproject(depth[i],K[i],poses[i],a.stride)
            valid=np.isfinite(z)&(z>.25)&(z<70)&(c>=np.percentile(conf[i],15))
            # Reject steep depth edges; widening splats must not bridge cars and background.
            edge=np.maximum(np.abs(np.gradient(z,axis=0)),np.abs(np.gradient(z,axis=1)))
            valid &= edge<np.maximum(.35,z*.07)
            fg=masks[i,::a.stride,::a.stride];color=rgb[i,::a.stride,::a.stride]
            # Estimate surface footprint, not only the fronto-parallel pixel
            # cone: oblique road samples span much more world space vertically.
            tangent=np.stack([np.gradient(xyz,axis=1),np.gradient(xyz,axis=0)],axis=-2)*.65
            lengths=np.linalg.norm(tangent,axis=-1,keepdims=True)
            tangent*=np.minimum(1.,.8/np.maximum(lengths,1e-8))
            dynamic=valid&fg;ap.append(xyz[dynamic]);ac.append(color[dynamic]);ar.append(tangent[dynamic])
            static=valid&~fg
            # A second real RGB frame must agree in camera z. No generated pixels
            # are permitted to validate or recolor this observed background.
            other=(t+1 if t<16 else t-1)*6+j
            q=(xyz-poses[other,:3,3])@poses[other,:3,:3]
            safe=np.maximum(q[...,2],1e-6);u=np.rint(q[...,0]/safe*K[other,0,0]+K[other,0,2]).astype(int);v=np.rint(q[...,1]/safe*K[other,1,1]+K[other,1,2]).astype(int)
            inside=(u>=0)&(u<W)&(v>=0)&(v<H)&(q[...,2]>.25)
            u=np.clip(u,0,W-1);v=np.clip(v,0,H-1);target=depth[other,v,u]
            consistent=inside&~masks[other,v,u]&(np.abs(target-q[...,2])<np.maximum(.35,q[...,2]*.065))
            static &= consistent
            all_points.append(xyz[static]);all_colors.append(color[static]);all_radii.append(tangent[static]);all_scores.append(np.clip(c[static],.01,None))
        actors.append(write_cloud(a.out/f'foreground-{t:02d}.bin',np.concatenate(ap),np.concatenate(ac),np.concatenate(ar)))
        counts.append(sum(len(x) for x in ap))
    points=np.concatenate(all_points);colors=np.concatenate(all_colors);radii=np.concatenate(all_radii);scores=np.concatenate(all_scores)
    before=len(points);points,colors,radii=fuse_voxels(points,colors,radii,scores,a.voxel)
    background=write_cloud(a.out/'background.bin',points,colors,radii)
    # The cache benchmark uses the exact same filtered geometry and masks.
    np.savez_compressed(a.out/'cache-input.npz',rgb=rgb[:,::3,::3],depth=depth[:,::3,::3],foreground=masks[:,::3,::3],confidence=conf[:,::3,::3],intrinsics=K,poses=poses)
    result={'schema':2,'kind':'persistent RGB-depth surfels + frame-local foreground','not_worldlatent':True,'learned_fused_worldvae':False,'background':background,'foreground':actors,'frames':17,'cameras':6,'source_views':102,'static_samples_before_fusion':before,'voxel_relative_units':a.voxel,'foreground_mask':'source RGB Mask R-CNN, score ≥ 0.7, 5px dilation at DA3 resolution; all detected foreground is time-local, including parked cars','consistency':'static samples agree with same camera at next/previous time within max(0.35, 6.5% Z); 15th confidence percentile excluded','geometry_sha256':hashlib.file_digest(a.geometry.open('rb'),'sha256').hexdigest(),'elapsed_seconds':time.perf_counter()-start,'units':'RGB/SfM relative display units, not measured meters','format':'28-byte little-endian records: xyz float32, U and V surface tangents float16 × 3 each, RGB uint8 + padding uint8','view_frame':'same display coordinates as calibrated scene.json'}
    (a.out/'dense.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in {'foreground'}},indent=2))

if __name__=='__main__':main()
