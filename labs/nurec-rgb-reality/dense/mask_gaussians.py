"""Remove repeatedly foreground-supported Gaussians from a learned RGB scene.

Preserves every property of retained Gaussians. Uses detector masks + estimated
RGB depth/cameras; never treats generated traffic as observation.
"""
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ply',type=Path,required=True);p.add_argument('--cache-input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('Choose fresh output')
    a.out.mkdir(parents=True);start=time.perf_counter();header=[];names=[]
    with a.ply.open('rb') as stream:
        while True:
            line=stream.readline().decode('ascii').strip();header.append(line)
            if line.startswith('element vertex '):count=int(line.split()[-1])
            if line.startswith('property '):
                _,kind,name=line.split()
                if kind!='float':raise ValueError('Expected native all-float Gaussian PLY')
                names.append(name)
            if line=='end_header':break
        data=np.fromfile(stream,dtype=[(n,'<f4') for n in names],count=count)
    if len(data)!=count:raise ValueError('Truncated Gaussian PLY')
    xyz=np.column_stack([data[k] for k in ['x','y','z']]);source=np.load(a.cache_input);votes=np.zeros(count,np.uint8)
    H,W=source['depth'].shape[1:]
    for i in range(102):
        C=source['poses'][i];K=source['intrinsics'][i].astype(float);K[:2]/=3
        q=(xyz-C[:3,3])@C[:3,:3];z=q[:,2];safe=np.maximum(z,1e-6)
        u=np.rint(q[:,0]/safe*K[0,0]+K[0,2]).astype(int);v=np.rint(q[:,1]/safe*K[1,1]+K[1,2]).astype(int)
        inside=(z>.25)&(u>=0)&(u<W)&(v>=0)&(v<H);ids=np.flatnonzero(inside);u=u[ids];v=v[ids]
        d=source['depth'][i,v,u];fg=source['foreground'][i,v,u]
        support=fg&(np.abs(d-z[ids])<np.maximum(.3,.04*d))
        votes[ids[support]]+=1
    keep=votes<2;out=a.out/'static-background.ply';header=[f'element vertex {int(keep.sum())}' if l.startswith('element vertex ') else l for l in header]
    with out.open('wb') as stream:stream.write(('\n'.join(header)+'\n').encode());stream.write(data[keep].tobytes())
    report={'schema':1,'method':'source RGB mask + DA3 z-depth support in at least 2 source views','input_gaussians':count,'retained_gaussians':int(keep.sum()),'removed_gaussians':int((~keep).sum()),'input_sha256':hashlib.file_digest(a.ply.open('rb'),'sha256').hexdigest(),'output_sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'elapsed_seconds':time.perf_counter()-start,'source':'previous trained NuRec RGB scene; no retraining; retained Gaussian parameters unchanged','generated_pixels_used':False,'uses_lidar':False,'limitations':'Estimated depth and detector masks may miss objects or remove some background. This is an experimental static/foreground decomposition.'}
    (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
