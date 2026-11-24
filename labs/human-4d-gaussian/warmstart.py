"""Pose-conditioned initialization of a native conditional-4D Gaussian model.

Original adapter. Quaternion convention matches Ant Research 4DAnyone; all
geometry remains RGB-estimated, not measured. No input media is distributed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree


def qmul(a,b):
 return np.concatenate((a[...,:1]*b[...,:1]-(a[...,1:]*b[...,1:]).sum(-1,keepdims=True),a[...,:1]*b[...,1:]+b[...,:1]*a[...,1:]+np.cross(a[...,1:],b[...,1:])),axis=-1)


def rotation4(left,right):
 left=left/np.linalg.norm(left,axis=-1,keepdims=True);right=right/np.linalg.norm(right,axis=-1,keepdims=True);conj=right*np.array([1,-1,-1,-1]);basis=np.eye(4)
 return qmul(left[:,None],qmul(basis[None],conj[:,None])).transpose(0,2,1)


def rotation_pair(matrix):
 """Recover SO(4)'s two unit quaternions through a rank-one association."""
 basis=np.eye(4);q=np.stack([rotation4(basis[i:i+1],basis[j:j+1])[0] for i in range(4) for j in range(4)])
 assoc=(matrix.reshape(-1,16)@q.reshape(16,16).T/4).reshape(-1,4,4);columns=(assoc**2).sum(1).argmax(1);left=assoc[np.arange(len(assoc)),:,columns];left/=np.maximum(np.linalg.norm(left,axis=1,keepdims=True),1e-15);right=np.einsum('nij,ni->nj',assoc,left);right/=np.maximum(np.linalg.norm(right,axis=1,keepdims=True),1e-15)
 error=float(np.abs(rotation4(left,right)-matrix).max());assert error<1e-6,error
 return left,right,error


def blend(D,t,ids,weights):
 out=np.zeros((len(t),4,4),np.float64)
 for k in range(ids.shape[1]):out+=D[t,ids[:,k]].astype(np.float64)*weights[:,k,None,None]
 return out


def conditional(arrays):
 R=rotation4(arrays['left'],arrays['right']);std=np.exp(np.concatenate([arrays['scale'],arrays['time_scale']],-1));F=R*std[:,None];C=F@F.transpose(0,2,1);var=np.maximum(C[:,3,3],1e-14);velocity=C[:,:3,3]/var[:,None];spatial=C[:,:3,:3]-C[:,:3,3,None]*C[:,None,3,:3]/var[:,None,None]
 return spatial,velocity,var


def save(path,arrays,meta):
 encoded=np.frombuffer(json.dumps(meta,allow_nan=False).encode(),dtype=np.uint8);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.with_suffix('.tmp').open('wb') as stream:np.savez_compressed(stream,metadata=encoded,**{k:v.astype(np.float32) for k,v in arrays.items()})
 path.with_suffix('.tmp').replace(path)


def prepare(geometry,model,origin_file,start,out,frames=121,fps=30):
 z=np.load(model,allow_pickle=False);meta=json.loads(z['metadata'].tobytes());names=['xyz','time','scale','time_scale','left','right','opacity','dc','sh'];d={k:z[k].astype(np.float64) for k in names};unit=float(meta['config']['space_scale']);spatial,velocity,var=conditional(d);tau=d['time'][:,0]
 g=np.load(geometry,allow_pickle=False);V=g['vertices'][:121];D=g['deformations'];origin_data=np.load(origin_file);origin=origin_data['world_origin'];R=origin_data['cv_to_world'];ti=np.rint(tau*fps).astype(int).clip(0,120);tref=ti/fps
 world=(d['xyz']+velocity*(tref-tau)[:,None])*unit;cv=world@R+origin;indices=np.zeros((len(cv),8),np.int64);weights=np.zeros((len(cv),8),np.float64);distance=np.zeros(len(cv));bi=g['bone_indices'];bw=g['bone_weights']
 for t in np.unique(ti):
  selected=np.flatnonzero(ti==t);dist,nearest=cKDTree(V[t]).query(cv[selected]);indices[selected]=bi[nearest];weights[selected]=bw[nearest];distance[selected]=dist
 weights/=np.maximum(weights.sum(1,keepdims=True),1e-15);assert indices.max()<D.shape[1]
 old=blend(D,ti,indices,weights);Aold=old[:,:3,:3];inverse=np.linalg.pinv(Aold,rcond=1e-5);rest=np.einsum('nij,nj->ni',inverse,cv-old[:,:3,3]);nt=(ti+start).clip(0,len(D)-1);new=blend(D,nt,indices,weights);Anew=new[:,:3,:3];B=Anew@inverse
 def body_velocity(frame):
  lo=np.maximum(frame-1,0);hi=np.minimum(frame+1,len(D)-1);ml=blend(D,lo,indices,weights);mh=blend(D,hi,indices,weights);delta=np.einsum('nij,nj->ni',mh[:,:3,:3]-ml[:,:3,:3],rest)+mh[:,:3,3]-ml[:,:3,3]
  return delta/np.maximum((hi-lo)/fps,1/fps)[:,None]
 old_body=body_velocity(ti);new_body=body_velocity(nt);old_cv_velocity=velocity*unit@R;residual=np.einsum('nij,nj->ni',inverse,old_cv_velocity-old_body);norm=np.linalg.norm(residual,axis=1);residual*=np.minimum(1,1.5/np.maximum(norm,1e-9))[:,None]
 new_cv_velocity=np.einsum('nij,nj->ni',Anew,residual)+new_body;new_cv=np.einsum('nij,nj->ni',Anew,rest)+new[:,:3,3];new_world=(new_cv-origin)@R.T;vnew=new_cv_velocity@R.T/unit;mu=new_world/unit+vnew*(tau-tref)[:,None];Aw=R[None]@B@R.T[None];S=Aw@spatial@Aw.transpose(0,2,1)
 C=np.zeros((len(mu),4,4),np.float64);C[:,:3,:3]=S+var[:,None,None]*vnew[:,:,None]*vnew[:,None,:];C[:,:3,3]=var[:,None]*vnew;C[:,3,:3]=var[:,None]*vnew;C[:,3,3]=var
 values,vectors=np.linalg.eigh(C);vectors[:,:,0]*=np.linalg.det(vectors)[:,None];left,right,error=rotation_pair(vectors);logs=np.log(np.maximum(values,1e-12))*.5;result={**d,'xyz':mu,'scale':logs[:,:3],'time_scale':logs[:,3:],'left':left,'right':right}
 recovered_S,recovered_v,recovered_var=conditional(result);v_error=float(np.abs(vnew-recovered_v).max());s_error=float(np.abs(S-recovered_S).max());assert v_error<1e-3 and s_error<1e-3,(v_error,s_error)
 meta['times']=(np.arange(frames)/fps).tolist();meta['fps']=str(fps);save(out,result,meta)
 report={'start_frame':start,'frames':frames,'valid_frames':min(frames,len(D)-start),'source_model':str(model),'method':'SOMA weighted skin transform at Gaussian peak time, residual velocity transfer, exact 4D covariance refactor','new_multiview_diffusion':False,'world_origin':origin.tolist(),'pose_binding_distance_m_quantiles':np.quantile(distance,[.5,.9,.99]).tolist(),'residual_velocity_cap_mps':1.5,'quaternion_rotation_max_error':error,'conditional_velocity_max_error':v_error,'conditional_covariance_max_error':s_error,'gaussians':len(mu),'precision':'FP32 parameters, float64 covariance algebra'}
 Path(out).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


def prepare_trajectory(geometry,model,origin_file,start,out,frames=121,fps=30,seed_time=0.):
 """Track a consistent snapshot's particles through SOMA, then lift tracks to 4D.

 Free 4D particles are not persistent mesh vertices. A shared appearance
 snapshot avoids assuming that every learned temporal particle has a stable
 material correspondence throughout its original lifetime.
 """
 z=np.load(model,allow_pickle=False);meta=json.loads(z['metadata'].tobytes());names=['xyz','time','scale','time_scale','left','right','opacity','dc','sh'];d={k:z[k].astype(np.float64) for k in names};unit=float(meta['config']['space_scale']);spatial,velocity,var=conditional(d);tau=d['time'][:,0];marginal=np.exp(-.5*(seed_time-tau)**2/var);opacity=1/(1+np.exp(-np.clip(d['opacity'][:,0],-60,60)))*marginal
 g=np.load(geometry,allow_pickle=False);D=g['deformations'];seed_frame=int(round(seed_time*fps));V=g['vertices'][seed_frame];ref=np.load(origin_file);R=ref['cv_to_world'];origin=ref['world_origin'];world=(d['xyz']+velocity*(seed_time-tau)[:,None])*unit;cv=world@R+origin;distance,nearest=cKDTree(V).query(cv);largest=np.linalg.eigvalsh(spatial)[:,-1].clip(0)**.5*unit;keep=(marginal>.05)&(opacity>.015)&(distance<.20)&(largest<.12);assert keep.sum()>3000
 cv=cv[keep];S=spatial[keep];ids=g['bone_indices'][nearest[keep]].astype(int);weights=g['bone_weights'][nearest[keep]].astype(float);weights/=weights.sum(1,keepdims=True);base_D=blend(D,np.full(len(cv),seed_frame),ids,weights);inv=np.linalg.pinv(base_D[:,:3,:3],rcond=1e-5);rest=np.einsum('nij,nj->ni',inv,cv-base_D[:,:3,3]);step=3;keys=np.arange(-step,frames+step,step);seconds=keys/fps;poses=[];covs=[]
 for k in keys:
  t=int(np.clip(start+k,0,len(D)-1));M=np.zeros_like(base_D)
  for dt,w in [(-1,.25),(0,.5),(1,.25)]:M+=blend(D,np.full(len(cv),np.clip(t+dt,0,len(D)-1)),ids,weights)*w
  A=M[:,:3,:3];P=np.einsum('nij,nj->ni',A,rest)+M[:,:3,3];poses.append((P-origin)@R.T/unit);B=R[None]@A@inv@R.T[None];covs.append(B@S@B.transpose(0,2,1))
 positions=np.stack(poses);v=np.gradient(positions,seconds,axis=0);Snew=np.concatenate(covs);mu=np.concatenate(poses);v=v.reshape(-1,3);N=len(cv);T=len(keys);time=np.repeat(seconds,N)[:,None];sigma=.07;variance=sigma*sigma;C=np.zeros((len(mu),4,4));C[:,:3,:3]=Snew+variance*v[:,:,None]*v[:,None,:];C[:,:3,3]=variance*v;C[:,3,:3]=variance*v;C[:,3,3]=variance;values,vectors=np.linalg.eigh(C);vectors[:,:,0]*=np.linalg.det(vectors)[:,None];left,right,error=rotation_pair(vectors);logs=np.log(np.maximum(values,1e-12))*.5
 alpha=np.clip(opacity[keep],1e-5,1-1e-5);fraction=(step/fps)/(np.sqrt(2*np.pi)*sigma);alpha=1-(1-alpha)**fraction;logit=np.log(alpha/(1-alpha))[:,None]
 result={'xyz':mu,'time':time,'scale':logs[:,:3],'time_scale':logs[:,3:],'left':left,'right':right,'opacity':np.tile(logit,(T,1)),'dc':np.tile(d['dc'][keep],(T,1,1)),'sh':np.tile(d['sh'][keep],(T,1,1))};meta['times']=(np.arange(frames)/fps).tolist();meta['fps']=str(fps);save(out,result,meta)
 report={'method':'Canonical appearance snapshot from selected native 4D model -> coherent SOMA particle tracks -> conditional 4D initialization','start_frame':start,'frames':frames,'valid_frames':min(frames,len(D)-start),'canonical_seed_time':seed_time,'canonical_gaussians':N,'keyframes':T,'keyframe_step':step,'gaussians':len(mu),'temporal_sigma_seconds':sigma,'new_multiview_diffusion':False,'canonical_binding_distance_m_quantiles':np.quantile(distance[keep],[.5,.9,.99]).tolist(),'quaternion_rotation_max_error':error,'source_model':str(model),'precision':'FP32 parameters, float64 covariance algebra'};Path(out).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--geometry',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--origin',type=Path,required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--frames',type=int,default=121);p.add_argument('--mode',choices=['trajectory','peak'],default='trajectory');a=p.parse_args();func=prepare_trajectory if a.mode=='trajectory' else prepare;func(a.geometry,a.model,a.origin,a.start,a.out,a.frames)
if __name__=='__main__':main()
