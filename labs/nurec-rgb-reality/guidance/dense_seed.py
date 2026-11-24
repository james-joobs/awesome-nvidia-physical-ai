"""Fuse cross-checked RGB-predicted geometry into an optional denser seed.

This is a separate intervention from adding losses: compare it separately.
Only training RGB and its predicted priors are used; no held-out RGB or LiDAR.
"""
import argparse,functools,json
from pathlib import Path
import numpy as np
from PIL import Image


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--priors',default='priors-base');p.add_argument('--stride',type=int,default=8);p.add_argument('--max-points',type=int,default=250000);a=p.parse_args();root=a.root
    rows=json.loads((root/'rgb-cameras.json').read_text())['frames'];groups={c:sorted([r for r in rows if r['camera']==c],key=lambda r:r['timestamp_us']) for c in {r['camera'] for r in rows}}
    @functools.lru_cache(maxsize=16)
    def load(camera,stamp):
        with np.load(root/a.priors/camera/f'{stamp}.npz') as z:return z['distance'],z['normals']
    candidates=[];counts=[]
    for camera,group in sorted(groups.items()):
        for i,r in enumerate(group):
            D,N=load(camera,r['timestamp_us']);K=np.array(r['K']);C=np.array(r['camera_to_world']);h,w=D.shape
            yy,xx=np.mgrid[4:h-4:a.stride,4:w-4:a.stride];x,y=xx.ravel(),yy.ravel();distance=D[y,x];normal=N[y,x]
            ray=np.stack([(x-K[0,2])/K[0,0],(y-K[1,2])/K[1,1],np.ones(len(x))],axis=-1);ray/=np.linalg.norm(ray,axis=1,keepdims=True);world_ray=ray@C[:3,:3].T
            valid=(distance>0)&(np.linalg.norm(normal,axis=1)>.5)&(np.abs((world_ray*normal).sum(axis=1))>.15)
            x,y,distance,normal,world_ray=x[valid],y[valid],distance[valid],normal[valid],world_ray[valid]
            P=C[:3,3]+world_ray*distance[:,None];rgb=np.asarray(Image.open(root/'rgb'/r['image']).convert('RGB'))[y,x].astype(float)/255
            agreements=np.zeros(len(P),np.int8)
            for j in [i-1,i+1]:
                if not 0<=j<len(group):continue
                other=group[j];B=np.array(other['camera_to_world']);Q=(P-B[:3,3])@B[:3,:3];q=Q@np.array(other['K']).T
                uv=np.rint(q[:,:2]/np.maximum(q[:,2:3],1e-5)).astype(int);ND,NN=load(camera,other['timestamp_us'])
                inside=(q[:,2]>.1)&(uv[:,0]>=0)&(uv[:,0]<ND.shape[1])&(uv[:,1]>=0)&(uv[:,1]<ND.shape[0]);ix=np.flatnonzero(inside);u,v=uv[ix,0],uv[ix,1]
                predicted=ND[v,u];expected=np.linalg.norm(Q[ix],axis=1)
                color=np.asarray(Image.open(root/'rgb'/other['image']).convert('RGB'))[v,u].astype(float)/255
                good=(predicted>0)&(np.abs(predicted-expected)<.08*np.maximum(expected,.5))&(np.abs((normal[ix]*NN[v,u]).sum(axis=1))>.8)&(np.abs(rgb[ix]-color).mean(axis=1)<.12)
                agreements[ix[good]]+=1
            good=agreements>=1
            candidates.append(np.concatenate([P[good],rgb[good],normal[good]],axis=1));counts.append(int(good.sum()))
        print('DENSE_SEED_CAMERA',camera,flush=True)
    points=np.concatenate(candidates).astype(np.float32);voxels=np.floor(points[:,:3]/.035).astype(np.int64);_,indices=np.unique(voxels,axis=0,return_index=True);points=points[indices]
    if len(points)>a.max_points:points=points[np.random.default_rng(42).choice(len(points),a.max_points,replace=False)]
    sparse=np.load(root/'sfm-points.npz');n=len(sparse['xyz']);s=np.zeros((n,9),np.float32);s[:,:3]=sparse['xyz'];s[:,3:6]=sparse['rgb']/255;s[:,8]=1
    points=np.concatenate([s,points]);normals=points[:,6:9];normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-8)
    q=np.stack([1+normals[:,2],-normals[:,1],normals[:,0],np.zeros(len(normals))],axis=1);opposite=np.linalg.norm(q,axis=1)<1e-5;q[opposite]=[0,1,0,0];q/=np.linalg.norm(q,axis=1,keepdims=True)
    names=['x','y','z','nx','ny','nz','f_dc_0','f_dc_1','f_dc_2','opacity','scale_0','scale_1','scale_2','rot_0','rot_1','rot_2','rot_3'];values=np.zeros(len(points),dtype=[(k,'f4') for k in names])
    for i,k in enumerate(['x','y','z']):values[k]=points[:,i]
    for i in range(3):values[f'f_dc_{i}']=(points[:,3+i]-.5)/.28209479177387814;values[f'scale_{i}']=np.log(.006 if i==2 else .04)
    for i in range(4):values[f'rot_{i}']=q[:,i]
    for i in range(3):values[f'scale_{i}'][:n]=np.log(.035)
    values['opacity']=1
    header='ply\nformat binary_little_endian 1.0\nelement vertex '+str(len(values))+'\n'+'\n'.join('property float '+k for k in names)+'\nend_header\n'
    with (root/'seed-dense.ply').open('wb') as f:f.write(header.encode());f.write(values.tobytes())
    report={'sparse_points':n,'cross_checked_candidates':sum(counts),'voxel_representatives':len(indices),'final_seed_points':len(values),'stride_pixels':a.stride,'voxel_size_relative_units':.035,'normal_and_photometric_checks':True,'uses_held_out_rgb':False,'uses_lidar':False,'scope':'Predicted geometry cross-checked against another training RGB/prior view. Consistency is not independent depth accuracy.'}
    (root/'dense-seed.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
