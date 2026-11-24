"""Export native conditional 4D Gaussians for local GPU browser playback."""
import argparse,gzip,hashlib,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True)
z=np.load(a.model,allow_pickle=False);meta=json.loads(z['metadata'].tobytes());names=['xyz','time','scale','time_scale','left','right','opacity','dc','sh'];d={k:z[k].astype(np.float32) for k in names};N=len(d['xyz'])
def rotation4(left,right):
 left=left/np.linalg.norm(left,axis=1,keepdims=True);right=right/np.linalg.norm(right,axis=1,keepdims=True);aa,b,c,dd=left.T;pp,q,r,s=right.T
 L=np.stack([aa,-b,-c,-dd,b,aa,-dd,c,c,dd,aa,-b,dd,-c,b,aa],-1).reshape(-1,4,4)
 R=np.stack([pp,q,r,s,-q,pp,-s,r,-r,s,pp,-q,-s,-r,q,pp],-1).reshape(-1,4,4)
 return L@R
rot=rotation4(d['left'].astype(np.float64),d['right'].astype(np.float64));scales=np.exp(np.concatenate([d['scale'],d['time_scale']],-1).astype(np.float64));C=(rot*scales[:,None,:]**2)@rot.transpose(0,2,1);var=np.maximum(C[:,3,3],1e-12);velocity=C[:,:3,3]/var[:,None];spatial=C[:,:3,:3]-C[:,:3,3,None]*C[:,None,3,:3]/var[:,None,None]
unit=float(meta['config']['space_scale']);evals,evectors=np.linalg.eigh(spatial.astype(np.float64)*unit**2);evectors[:,:,0]*=np.linalg.det(evectors)[:,None];quat=Rotation.from_matrix(evectors).as_quat();std=np.sqrt(np.maximum(evals,1e-12));opacity=1/(1+np.exp(-np.clip(d['opacity'][:,0],-60,60)))
fields=np.c_[d['xyz']*unit,std,quat,opacity,np.full((N,3),.5)].astype(np.float32)
motion=np.c_[velocity*unit,d['time'][:,0]].astype(np.float32);variance=np.c_[1/var,np.zeros((N,3))].astype(np.float32)
sh=np.concatenate([d['dc'],d['sh']],axis=1).astype(np.float16);assert sh.shape[1:]==(16,3)
assert all(np.isfinite(x).all() for x in [fields,motion,variance,sh])
files={}
def save(name,array):
 raw=np.ascontiguousarray(array).tobytes();target=out/name
 with target.open('wb') as handle:
  with gzip.GzipFile(filename='',mode='wb',fileobj=handle,mtime=0) as packed:packed.write(raw)
 files[name]={'bytes':target.stat().st_size,'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest()}
save('gaussians.f32.gz',fields);save('motion.f32.gz',motion);save('variance.f32.gz',variance);save('sh.f16.gz',sh)
# Export independent samples of the exact conditional distribution for JS parity.
rng=np.random.default_rng(42);samples=[]
for i,t in zip(rng.integers(0,N,40),rng.uniform(0,float(meta['times'][-1]),40)):
 dt=t-float(d['time'][i,0]);samples.append({'index':int(i),'time':float(t),'position':((d['xyz'][i]+velocity[i]*dt)*unit).tolist(),'opacity':float(opacity[i]*np.exp(-.5*dt*dt/var[i]))})
camera_keys=[json.dumps([c['K'],c['w2c']],sort_keys=True) for c in meta['cameras']];unique_cameras=len(set(camera_keys));observed_weight=camera_keys.count(camera_keys[0])
payload={'schema':1,'gaussians':N,'fps':float(meta['fps']),'frames':len(meta['times']),'duration':len(meta['times'])/float(meta['fps']),'degree':meta['degree'],'marginal_threshold':meta['config']['marginal_threshold'],'units':'model-estimated meters','native_model_format':meta['format'],'training_step':meta['step'],'training_resolution':[int(meta['cameras'][0]['width']*meta['config']['image_scale']),int(meta['cameras'][0]['height']*meta['config']['image_scale'])],'method':'Native conditional 4D Gaussian with per-Gaussian temporal marginal, velocity and conditional covariance','unique_camera_directions':unique_cameras,'synthetic_views':unique_cameras-1,'observed_cameras':1,'observed_sampling_weight':observed_weight,'source_observed':True,'back_and_sides':'generated priors; not observed ground truth','files':files,'parity_samples':samples}
(out/'meta.json').write_text(json.dumps(payload,indent=2)+'\n');print('BROWSER_4D_EXPORT',N,sum(f['bytes'] for f in files.values()),flush=True)
