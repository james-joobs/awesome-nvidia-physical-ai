"""Cull unsupported 4D floaters, preserving the unfiltered checkpoint.

Use generous distance to the independently fitted SOMA surface and principal
Gaussian size, not source-camera-only crop clipping. Thresholds are in
model-estimated meters; they are not measured physical accuracy claims.
"""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

def rotation4(left,right):
 left=left/np.linalg.norm(left,axis=1,keepdims=True);right=right/np.linalg.norm(right,axis=1,keepdims=True);a,b,c,d=left.T;p,q,r,s=right.T
 L=np.stack([a,-b,-c,-d,b,a,-d,c,c,d,a,-b,d,-c,b,a],-1).reshape(-1,4,4);R=np.stack([p,q,r,s,-q,p,-s,r,-r,s,p,-q,-s,-r,q,p],-1).reshape(-1,4,4);return L@R
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=a.root
z=np.load(a.model,allow_pickle=False);meta=json.loads(z['metadata'].tobytes());N=len(z['xyz']);rot=rotation4(z['left'].astype(np.float64),z['right'].astype(np.float64));scales=np.exp(np.c_[z['scale'],z['time_scale']].astype(np.float64));C=(rot*scales[:,None,:]**2)@rot.transpose(0,2,1);variance=np.maximum(C[:,3,3],1e-12);velocity=C[:,:3,3]/variance[:,None];spatial=C[:,:3,:3]-C[:,:3,3,None]*C[:,None,3,:3]/variance[:,None,None];unit=float(meta['config']['space_scale']);sigma=np.sqrt(np.maximum(np.linalg.eigvalsh(spatial)[:,-1],0))*unit
time=z['time'][:,0].astype(np.float64);last=float(meta['times'][-1]);dt_limit=np.sqrt(-2*np.log(meta['config']['marginal_threshold'])*variance);samples=np.stack([np.clip(time,0,last),np.clip(time-dt_limit,0,last),np.clip(time+dt_limit,0,last)],1)
g=np.load(r/'rig/geometry.npz');conditioning=np.load(r/'multiview-prior/pilot/soma-conditioning.npz');origin=conditioning['world_origin'];S=conditioning['cv_to_world'];source_ids=conditioning['frame_ids'];vertices=g['vertices'][source_ids];trees={};distances=np.zeros((N,3),np.float32)
for sidx in range(3):
 ts=samples[:,sidx];frames=np.rint(ts*30).astype(int);positions=(z['xyz'].astype(np.float64)+velocity*(ts-time)[:,None])*unit
 for t in np.unique(frames):
  ids=np.flatnonzero(frames==t)
  if int(t) not in trees:trees[int(t)]=cKDTree((vertices[t]-origin)@S)
  distances[ids,sidx]=trees[int(t)].query(positions[ids],workers=4)[0]
 print('SUPPORT_SAMPLE',sidx,flush=True)
bad_size=sigma>.12;bad_peak=distances[:,0]>.28;bad_end=distances[:,1:].max(1)>.40;keep=~(bad_size|bad_peak|bad_end)
report={'original_gaussians':N,'retained_gaussians':int(keep.sum()),'removed_gaussians':int((~keep).sum()),'removed_fraction':float((~keep).mean()),'large_principal_sigma':int(bad_size.sum()),'unsupported_peak_position':int(bad_peak.sum()),'unsupported_active_endpoint':int(bad_end.sum()),'thresholds':{'principal_sigma_model_m':.12,'peak_distance_to_SOMA_model_m':.28,'active_endpoint_distance_model_m':.40},'scope':'Generous inferred-body support culling, not unseen-view ground truth. Does not alter the original trained checkpoint. Gaussian lifetime endpoints use the native marginal threshold.','peak_distance_quantiles':np.quantile(distances[:,0],[.5,.9,.95,.99,1]).tolist(),'principal_sigma_quantiles':np.quantile(sigma,[.5,.9,.95,.99,1]).tolist()}
assert keep.sum()>1000 and report['removed_fraction']<.35,report
arrays={name:z[name][keep] for name in z.files if name!='metadata'};arrays['metadata']=z['metadata'];a.out.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(a.out,**arrays);a.out.with_suffix('.cleanup.json').write_text(json.dumps(report,indent=2)+'\n');print('CLEAN_4D_MODEL',json.dumps(report),flush=True)
