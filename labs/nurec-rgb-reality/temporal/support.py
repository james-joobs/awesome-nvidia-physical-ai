"""Inspect Gaussian centers against RGB-predicted depth; no measured-depth claim.

Counts distinct named cameras, not repeated frames as independent cameras.
The false-color export retains geometry/opacity and removes directional color.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
import numpy as np

COLORS=np.array([[.95,.24,.12],[1.,.67,.12],[.08,.77,.65]],np.float32)

def visible_depth_agreement(points,camera_to_world,K,distance,relative=.10,absolute=.10):
    """Gaussian-center projection with predicted ray-distance consistency."""
    points=np.asarray(points);C=np.asarray(camera_to_world);K=np.asarray(K)
    if not np.isfinite(C).all() or not np.isfinite(K).all():raise ValueError('Nonfinite estimated camera')
    q=(points-C[:3,3])@C[:3,:3];finite=np.isfinite(q).all(axis=1);front=finite&(q[:,2]>1e-4)
    projected=q@K.T;uv=np.zeros((len(q),2),np.int64)
    uv[front]=np.rint(projected[front,:2]/projected[front,2:]).astype(np.int64)
    h,w=distance.shape;inside=front&(uv[:,0]>=0)&(uv[:,0]<w)&(uv[:,1]>=0)&(uv[:,1]<h)
    ids=np.flatnonzero(inside);result=np.zeros(len(q),bool)
    predicted=distance[uv[ids,1],uv[ids,0]];ray=np.linalg.norm(q[ids],axis=1)
    result[ids]=np.isfinite(predicted)&(predicted>0)&(np.abs(ray-predicted)<=absolute+relative*predicted)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--relative-tolerance',type=float,default=.10);p.add_argument('--absolute-tolerance',type=float,default=.10);a=p.parse_args()
    from plyfile import PlyData
    r=a.root;out=a.out
    if out.exists() and any(out.iterdir()):raise ValueError('Choose a fresh support-output folder')
    out.mkdir(parents=True,exist_ok=True);model=r/'gaussians/background/model.ply';ply=PlyData.read(model);v=ply['vertex'];xyz=np.stack([v[x] for x in ['x','y','z']],axis=1)
    rows=json.loads((r/'rgb-cameras.json').read_text())['frames'];names=sorted({x['camera'] for x in rows})
    if len(names)>16:raise ValueError('This export supports at most16 named cameras')
    bits=np.zeros(len(xyz),np.uint16);observations=np.zeros(len(xyz),np.uint16);inputs=[]
    for i,row in enumerate(rows):
        prior=r/'priors-base'/row['camera']/f"{row['timestamp_us']}.npz"
        with np.load(prior,allow_pickle=False) as data:distance=data['distance']
        for start in range(0,len(xyz),200000):
            end=min(start+200000,len(xyz));yes=visible_depth_agreement(xyz[start:end],row['camera_to_world'],row['K'],distance,a.relative_tolerance,a.absolute_tolerance)
            bits[start:end]|=yes.astype(np.uint16)<<names.index(row['camera']);observations[start:end]+=yes
        inputs.append({'image':row['image'],'depth_sha256':hashlib.sha256(prior.read_bytes()).hexdigest()})
        if i%24==0:print('SUPPORT_FRAME',i+1,len(rows),flush=True)
    counts=np.zeros(len(xyz),np.uint8)
    for bit in range(len(names)):counts+=((bits>>bit)&1).astype(np.uint8)
    colors=COLORS[np.minimum(counts,2)]
    for axis in range(3):v[f'f_dc_{axis}']=(colors[:,axis]-.5)/.28209479177387814
    for name in v.data.dtype.names:
        if name.startswith('f_rest_'):v[name]=0
    target=out/'support.ply';ply.write(target);np.savez_compressed(out/'support-counts.npz',named_camera_count=counts,frame_count=observations)
    subprocess.run(['npm','exec','--yes','--package=@playcanvas/splat-transform@3.12.0','--','splat-transform','-w',str(target),'--filter-harmonics','0',str(out/'support.spz'),'--spz-version','3'],check=True)
    report={'schema':1,'gaussians':len(xyz),'source_images':len(rows),'camera_names':names,'relative_tolerance':a.relative_tolerance,'absolute_tolerance_relative_units':a.absolute_tolerance,'histogram':{str(n):int((counts==n).sum()) for n in range(len(names)+1)},'legend':{'0':'No depth-consistent estimated RGB observation','1':'One named camera','2+':'At least two named cameras'},'scope':'Gaussian-center consistency with RGB-predicted depth and RGB-estimated poses. Not measured visibility, ground truth, per-pixel provenance, or a hallucination detector. Occlusion is approximated by predicted depth.','geometry_opacity_unchanged':True,'source_model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'support_spz_sha256':hashlib.sha256((out/'support.spz').read_bytes()).hexdigest(),'inputs':inputs}
    (out/'support.json').write_text(json.dumps(report,indent=2)+'\n');print('SUPPORT_COMPLETE',report['histogram'],flush=True)
if __name__=='__main__':main()
