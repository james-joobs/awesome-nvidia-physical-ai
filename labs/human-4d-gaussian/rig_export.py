"""Inspect actual GEM/SOMA predictions and export one coherent animated rig."""
import argparse,json,torch,numpy as np,cv2,types
from pathlib import Path
from gem.common.soma import SomaFixedGs1BodyAdapter,SomaRuntimeConfig
import soma.geometry.lbs_warp as warp_lbs

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--prediction',default='motion.pt');p.add_argument('--lod',default='mid');a=p.parse_args();r=a.root;torch.set_num_threads(8)
 d=torch.load(r/a.prediction,map_location='cpu',weights_only=False);T=int(d['length'][0]);K=d['conditions']['K_fullimg'][0].numpy();observed=d['conditions']['kp2d_native77'][0].numpy();model=SomaFixedGs1BodyAdapter(SomaRuntimeConfig(data_root=r/'soma-assets',device='cpu',lod=a.lod,apply_correctives=False,mode='warp',enable_procedural_transforms=True,procedural_reference='runtime'))
 def params(variant):return (d['raw_predictions'] if variant=='raw' else d)['pred_soma_params_incam']
 def sample_fields(q,ids):return {k:(v[:,ids] if v.ndim>=3 else v) for k,v in q.items()}
 ids=torch.arange(0,T,max(1,T//64));quality={}
 for variant in ['raw','postprocessed']:
  q=sample_fields(params(variant),ids)
  with torch.inference_mode():out=model(**q,return_joints_only=True,apply_correctives=False,repose_to_bind_pose=True)
  J=out['joints'][0].numpy();P=np.einsum('tij,tnj->tni',K[ids],J);uv=P[...,:2]/P[...,2:3];valid=(observed[ids,:,2]>.5)&(P[...,2]>0);err=np.linalg.norm(uv-observed[ids,:,:2],axis=-1);quality[variant]={'mean_confident_reprojection_px':float(err[valid].mean()),'median_confident_reprojection_px':float(np.median(err[valid])),'observations':int(valid.sum())}
 selected=min(quality,key=lambda k:quality[k]['mean_confident_reprojection_px']);q=params(selected);print('RIG_QUALITY',json.dumps(quality),'selected',selected,flush=True)
 runtime=model.runtime;original=warp_lbs.linear_blend_skinning;captures=[]
 def capture(vertices,weights,indices,transforms):
  captures.append(tuple(x.detach().cpu().numpy().copy() for x in [vertices,weights,indices,transforms]));return original(vertices,weights,indices,transforms)
 warp_lbs.linear_blend_skinning=capture
 outdir=r/'rig';outdir.mkdir(exist_ok=True);allJ=[];allD=[];allV=[];rest=None;weights=None;indices=None;max_error=0
 try:
  for start in range(0,T,32):
   captures.clear();idx=torch.arange(start,min(T,start+32));fields=sample_fields(q,idx)
   with torch.inference_mode():out=model(**fields,apply_correctives=False,repose_to_bind_pose=True)
   V=out['vertices'][0].numpy();J=out['joints'][0].numpy();assert captures,'Expected native Warp skinning'
   bind,bw,bi,D=captures[-1];assert len(bind)==len(idx);assert D.shape[1]<=256
   if rest is None:rest=bind[0].copy();weights=bw.copy();indices=bi.copy()
   assert np.max(np.abs(bind-rest[None]))<1e-4,'Identity must remain fixed across frames'
   # Check that the captured native deformation really reproduces the mesh.
   check=np.arange(0,len(rest),max(1,len(rest)//200));trans=D[:,bi[check]];x=rest[check];pred=(trans[...,:3,:3]@x[None,:,None,:,None])[...,0]+trans[...,:3,3]
   pred=(pred*bw[check][None,:,:,None]).sum(2);error=float(np.max(np.linalg.norm(pred-V[:,check],axis=-1)));max_error=max(max_error,error);assert error<1e-4,(error,'Skinning export must match native SOMA')
   allJ.append(J);allD.append(D);allV.append(V);print('RIG_FRAMES',start+len(idx),T,flush=True)
 finally:warp_lbs.linear_blend_skinning=original
 J=np.concatenate(allJ);D=np.concatenate(allD);V=np.concatenate(allV);faces=runtime.faces.cpu().numpy();np.savez_compressed(outdir/'geometry.npz',vertices=V,joints=J,deformations=D,rest_vertices=rest,bone_weights=weights,bone_indices=indices,faces=faces,K=K,times=d['frame_times'][0].numpy(),observations=observed)
 names=list(runtime.public_joint_names)[1:];parents=runtime.public_joint_parent_ids.cpu().numpy()[1:]-1
 lengths=np.array([np.linalg.norm(J[:,i]-J[:,p],axis=-1) for i,p in enumerate(parents) if p>=0]);bone_variation=float(np.max(np.std(lengths,axis=1)))
 report={'schema':1,'frames':T,'fps':30,'selected_camera_parameters':selected,'reprojection':quality,'public_joint_names':names,'public_joint_parents':parents.tolist(),'skinning_bones':D.shape[1],'vertices':V.shape[1],'triangles':len(faces),'native_skinning_reconstruction_max_error_m':max_error,'max_public_bone_length_std_m':bone_variation,'uses_supplied_depth':False,'uses_lidar':False,'scale':'Model-estimated meters, not physically measured from the video','source':'NVIDIA GEM-X temporal estimation + SOMA 0.3.3 native Warp skinning; estimates, not motion-capture ground truth'}
 (outdir/'rig.json').write_text(json.dumps(report,indent=2)+'\n')
 cap=cv2.VideoCapture(str(r/'input.mp4'));frames=[]
 for t in np.linspace(0,T-1,8).astype(int):
  cap.set(cv2.CAP_PROP_POS_MSEC,float(t)/30*1000);ok,image=cap.read();assert ok;P=K[t]@J[t].T;uv=(P[:2]/P[2:]).T
  for i,parent in enumerate(parents):
   if parent<0 or any(s in names[i].lower() for s in ['thumb','index','middle','ring','pinky']):continue
   a,b=uv[i],uv[parent]
   if not np.isfinite([a,b]).all():continue
   color=(80,210,250) if 'left' in names[i].lower() else (250,170,60) if 'right' in names[i].lower() else (80,240,80)
   cv2.line(image,tuple(np.rint(a).astype(int)),tuple(np.rint(b).astype(int)),color,5,cv2.LINE_AA);cv2.circle(image,tuple(np.rint(a).astype(int)),7,color,-1,cv2.LINE_AA)
  frames.append(cv2.resize(image,(270,480)))
 cap.release();cv2.imwrite(str(outdir/'rig-contact.jpg'),np.concatenate(frames,axis=1));print('RIG_EXPORTED',json.dumps({k:v for k,v in report.items() if k not in ['public_joint_names','public_joint_parents']}),flush=True)
if __name__=='__main__':main()
