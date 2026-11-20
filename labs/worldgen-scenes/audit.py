"""Validate newly generated PLY/distance files on CPU, and save concrete samples."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image
from plyfile import PlyData


def audit(folder):
    record=json.loads((folder/'result.json').read_text())
    depth=np.load(folder/'distance.npy');h,w=depth.shape
    vertices=PlyData.read(folder/'scene.ply')['vertex'].data
    assert len(vertices)==h*w==record['gaussians']['gaussians']
    assert np.isfinite(depth).all() and (depth>0).all()
    assert all(np.isfinite(vertices[k]).all() for k in vertices.dtype.names)
    rgb=np.array(Image.open(folder/'panorama.png'))
    samples=[]
    for y,x in [(h//2,w//2),(3*h//8,5*w//16),(5*h//8,11*w//16),(h//8,w//8)]:
        v=vertices[y*w+x];phi=((x+.5)/w)*2*math.pi-math.pi;theta=((y+.5)/h)*math.pi-math.pi/2
        ray=np.array([math.cos(theta)*math.sin(phi),math.sin(theta),math.cos(theta)*math.cos(phi)])
        xyz=np.array([float(v[k]) for k in ['x','y','z']]);distance=float(depth[y,x])
        assert np.max(np.abs(xyz-ray*distance))<1e-4
        samples.append({'pixel':[x,y],'rgb':list(map(int,rgb[y,x])),'ray':ray.tolist(),'distance':distance,'xyz':xyz.tolist()})
    norms=np.linalg.norm(np.stack([vertices[f'rot_{i}'] for i in range(4)],-1),axis=1)
    assert np.allclose(norms,1,atol=1e-3)
    result={'samples':samples,'distance_finite':True,'distance_positive':True,'finite_ply_fields':True,
        'opacity_min':float((1/(1+np.exp(-vertices['opacity']))).min()),
        'quaternion_norm_range':[float(norms.min()),float(norms.max())]}
    if record['mode']=='i2s':
        mask=np.array(Image.open(folder/'generation-mask.png'))
        conditioning=np.array(Image.open(folder/'conditioning.png'))
        assert np.any(mask==0) and np.any(mask==255)
        assert np.array_equal(conditioning[mask==0],rgb[mask==0])
        assert record['conditioning']['max_preserved_rgb_error']==0
    (folder/'geometry-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'{folder.name}: finite geometry, unit rotations, ray×distance positions and conditioning verified.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    audit(p.parse_args().folder)
