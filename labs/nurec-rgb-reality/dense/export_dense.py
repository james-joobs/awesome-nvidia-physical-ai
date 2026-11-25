"""Package static/foreground separation and actual joint-diffusion comparisons."""
import argparse,copy,gzip,hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unified'))
from export_viewer import align_to_reference

def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',type=Path,required=True);p.add_argument('--cache-input',type=Path,required=True);p.add_argument('--static',type=Path,required=True);p.add_argument('--right',type=Path,required=True);p.add_argument('--left',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('Select a fresh directory')
    a.out.mkdir(parents=True);scene=json.loads(a.scene.read_text());data=np.load(a.cache_input)
    static=a.static/'static-background.spz';shutil.copy2(static,a.out/static.name)
    masks=data['foreground'].astype('u1').tobytes();compressed=gzip.compress(masks,mtime=0);(a.out/'foreground-mask.bin.gz').write_bytes(compressed)
    record={'schema':3,'static_gaussians':{'file':static.name,'bytes':static.stat().st_size,'sha256':hashlib.sha256(static.read_bytes()).hexdigest()},'mask':{'file':'foreground-mask.bin.gz','bytes':len(compressed),'decoded_bytes':len(masks),'sha256':hashlib.sha256(masks).hexdigest(),'shape':list(data['foreground'].shape)},'decomposition':json.loads((a.static/'result.json').read_text()),'worldlatent_executed':False,'source_rgb_only':True,'models':[]}
    source=next(m for m in scene['models'] if m['id']=='aether');scale0=source['alignment']['scale'];ref0=np.array(source['camera_to_world'][0])
    for name,folder in [('generated-right',a.right),('generated-left',a.left)]:
        g=np.load(folder/'geometry.npz');requested=np.load(folder/'requested_cameras.npz')['camera_pose']
        ref=requested.copy();ref[:,:3,:3]=ref0[:3,:3][None]@requested[:,:3,:3];ref[:,:3,3]=scale0*requested[:,:3,3]@ref0[:3,:3].T+ref0[:3,3]
        C,scale,alignment=align_to_reference(g['camera_pose'],ref)
        z=g['depth'][:,::3,::3]*scale;valid=np.isfinite(z)&(z>.1)&(z<80);q=np.where(valid,np.clip(np.rint(z/80*65535),1,65535),0).astype('<u2')
        dest=a.out/name;dest.mkdir();depthfile=f'{name}.depth.bin';(a.out/depthfile).write_bytes(q.tobytes())
        rgb=(np.clip(g['decoded_rgb'],0,1)*255).round().astype('u1')
        for i,image in enumerate(rgb):Image.fromarray(image).save(dest/f'{i:02d}.jpg',quality=88,optimize=True)
        run=json.loads((folder/'run.json').read_text());latent=json.loads((folder/'latent.json').read_text())
        m=copy.deepcopy(source);m.update(id=name,label=f'AetherV1 · diffusion {name.split("-")[-1]}',rgb_kind='generated',rgb=[f'dense/{name}/{i:02d}.jpg' for i in range(17)],camera_to_world=C.tolist(),intrinsics=g['intrinsics'].tolist(),depth_file='dense/'+depthfile,depth_sha256=hashlib.sha256(q.tobytes()).hexdigest(),depth_bytes=q.nbytes,alignment=alignment,inference=run['timing'],run=run,latent=latent,display_valid_fraction=[float(x.mean()) for x in valid],geometry_sha256=hashlib.file_digest((folder/'geometry.npz').open('rb'),'sha256').hexdigest())
        record['models'].append(m)
    (a.out/'dense.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'gaussians':record['decomposition'],'mask_bytes':len(compressed),'generated':[m['id'] for m in record['models']]},indent=2))

if __name__=='__main__':main()
