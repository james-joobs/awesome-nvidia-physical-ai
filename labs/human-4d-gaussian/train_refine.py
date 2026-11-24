"""Controlled native 4DGS continuation. Each branch writes a new model only."""
import argparse,json,sys,time,hashlib
from pathlib import Path
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--out',type=Path);p.add_argument('--roi-root',type=Path);p.add_argument('--data',type=Path);p.add_argument('--base',type=Path);p.add_argument('--steps',type=int,default=3000);p.add_argument('--roi',action='store_true');p.add_argument('--allow-unstable-diagnostic',action='store_true');p.add_argument('--split-roi',action='store_true');p.add_argument('--roi-l1',type=float,default=.6);p.add_argument('--roi-vgg',type=float,default=.08);p.add_argument('--geometry',type=Path);a=p.parse_args()
 r=a.root;w=r/'multiview-prior';e=w/'refinement';out=a.out or e/a.name;out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(w/'4danyone'))
 import torch
 from fdanyone.reconstruction.checkpoint import load_render_model,save_render_model
 from fdanyone.reconstruction.data import TrainingData
 from fdanyone.reconstruction.train import make_camera,make_optimizer,make_objective
 from fdanyone.reconstruction.settings import training_settings
 from fdanyone.reconstruction.loader import Sampler,batches
 from fdanyone.reconstruction.rasterizer import render
 from fdanyone.reconstruction.losses import ssim
 from fdanyone.nerfstudio.perceptual import VGG19PerceptualLoss
 torch.set_num_threads(8);torch.manual_seed(42);torch.cuda.manual_seed(42);torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
 base=a.base or w/'final-4d.npz';data=TrainingData(a.data or w/'twelve-view-hires/data',image_scale=1.)
 if len(data.cameras)==1 and not a.allow_unstable_diagnostic:raise ValueError('Observed-only later intervals require fit_interval.py with the stable conditional factorization. Free SO(4) refinement is diagnostic-only here.')
 meta,model=load_render_model(base,'cuda')
 settings=training_settings({'steps':a.steps,'perceptual_weight':0.,'loader_workers':4,'bounds':((-1.2,-.1,-.7),(1.2,2.3,.7))});settings['densify_until']=0
 # A smaller continuation rate prevents detail supervision from moving the whole body.
 for k in ['xyz_lr','scale_lr','rotation_lr','opacity_lr','dc_lr','sh_lr','time_lr']:settings[k]*=.35
 optimizer=make_optimizer(model,settings)
 split_records=[]
 if a.split_roi:
  from fdanyone.reconstruction.gaussian import rotation4
  g=np.load(r/'rig/geometry.npz');j=g['joints'][:121];origin=np.load(w/'pilot/soma-conditioning.npz')['world_origin'];j=torch.tensor((j-origin)*np.array([1,-1,-1]),device='cuda',dtype=torch.float32)
  with torch.no_grad():
   for round_idx in range(2):
    cov,velocity,var=model.covariance();tau=model.time[:,0];ti=(tau*30).round().long().clamp(0,120);xyz=(model.xyz+velocity*(ti[:,None]/30-model.time))*.1
    hd=(xyz[:,None]-j[ti[:,None],torch.tensor([6,8,9,10],device='cuda')[None]]).norm(dim=-1).amin(-1)
    hands=(xyz[:,None]-j[ti[:,None],torch.tensor([14,42],device='cuda')[None]]).norm(dim=-1).amin(-1)
    footprint=cov.diagonal(dim1=-2,dim2=-1).sum(-1).clamp_min(0).sqrt()*.1
    select=((hd<.15)|(hands<.11))&(footprint>.005)&(model.opacity[:,0].sigmoid()>.03)
    ids=torch.where(select)[0]
    if len(ids)>60000:
     chosen=torch.topk(footprint[ids],60000).indices;select.zero_();select[ids[chosen]]=True
    count=int(select.sum());before=len(model)
    if count:
     additions={name:getattr(model,name)[select].repeat((2,)+(1,)*(getattr(model,name).ndim-1)) for name in model.names}
     std=torch.cat([additions['scale'],additions['time_scale']],-1).exp();samples=std*torch.randn_like(std);position=(rotation4(additions['left'],additions['right'])@samples[...,None])[...,0]+torch.cat([additions['xyz'],additions['time']],-1)
     additions['xyz'],additions['time']=position[:,:3],position[:,3:];logs=(std/1.6).clamp(1e-6,1e6).log();additions['scale'],additions['time_scale']=logs[:,:3],logs[:,3:];optimizer.resize(model,~select,additions)
    split_records.append({'round':round_idx,'selected':count,'before':before,'after':len(model)})
    print('ROI_4D_SPLIT',json.dumps(split_records[-1]),flush=True)
 objective=make_objective(settings,'cuda');cameras=[make_camera(c,settings,'cuda') for c in data.cameras];sampler=Sampler(len(data),42)
 roi_root=a.roi_root or e/'roi';rows=json.loads((roi_root/'crops.json').read_text());roi=torch.tensor(np.load(roi_root/'pixels.npz')['pixels'],device='cuda',dtype=torch.float32)/255
 rc=[make_camera(x['camera'],settings,'cuda') for x in rows];train_ids=[i for i,x in enumerate(rows) if x['split']=='train'];rng=np.random.default_rng(91)
 perceptual=VGG19PerceptualLoss(w/'models/perceptual/imagenet-vgg-verydeep-19-conv.safetensors',compute_dtype='bfloat16',include_rgb=False).to('cuda') if a.roi else None
 if a.geometry:
  from geometry_loss import GeometryLoss
  geometry=GeometryLoss(a.geometry,settings,'cuda')
 else:geometry=None
 provenance={'branch':a.name,'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'steps':a.steps,'roi_enabled':a.roi,'roi_loss':{'l1':a.roi_l1,'ssim':.15,'vgg19':a.roi_vgg,'alpha':.08} if a.roi else None,'full_frame_sampling':'6 observed copies : 11 generated','densification':split_records if a.split_roi else False,'optimizer_recipe':'Fixed topology after optional ROI 4D split; all existing degree-3 SH trainable, no SH activation gating or adaptive pruning','settings':settings,'seed':42,'generated_views_are_inferred':True,'geometry':str(a.geometry) if a.geometry else None}
 (out/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
 torch.cuda.reset_peak_memory_stats();started=time.monotonic();log=(out/'train.jsonl').open('w')
 for step,(pixels,indices) in enumerate(batches(data,sampler,0,a.steps,'cuda',batch_size=4,loader_workers=4,seed=42)):
  optimizer.zero_grad(set_to_none=True);ims=[];alphas=[]
  for index in indices:
   ci,ti=divmod(index,121);im,alpha,_=render(model,cameras[ci],ti/30,marginal_threshold=settings['marginal_threshold']);ims.append(im);alphas.append(alpha)
  loss,terms=objective(torch.stack(ims),torch.stack(alphas),pixels[:,:3],pixels[:,3:],step=step)
  if a.roi:
   ri=train_ids[int(rng.integers(len(train_ids)))];im,alpha,_=render(model,rc[ri],rows[ri]['time'],marginal_threshold=settings['marginal_threshold']);target=roi[ri,:3];mask=roi[ri,3:];bg=torch.rand((3,1,1),device='cuda');pred=im+(1-alpha)*bg;gt=target+(1-mask)*bg
   l1=(pred-gt).abs().mean();s=1-ssim(pred[None],gt[None]);v=perceptual(pred[None],gt[None]);al=(alpha-mask).square().mean();rl=a.roi_l1*l1+.15*s+a.roi_vgg*v+.08*al;loss=loss+rl;terms.update(roi_l1=l1,roi_ssim=s,roi_vgg=v,roi_loss=rl)
  if geometry is not None and step%2==0:
   gl,gterms=geometry(model,step);loss=loss+gl;terms.update(gterms)
  loss.backward();optimizer.step()
  if step%100==0 or step+1==a.steps:
   record={'step':step+1,'seconds':time.monotonic()-started,'points':len(model),'loss':float(loss.detach()),'peak_memory_bytes':torch.cuda.max_memory_allocated(),**{k:float(v.detach()) for k,v in terms.items()}}
   assert all(np.isfinite(x) for x in record.values());log.write(json.dumps(record)+'\n');log.flush();print(json.dumps(record),flush=True)
  if (step+1)%1500==0 or step+1==a.steps:
   payload={'model':{k:v.cpu() for k,v in model.tensors().items()},'degree':model.degree,'config':settings,'step':step+1,'cameras':data.cameras,'times':data.times.tolist(),'fps':'30'}
   save_render_model(out/f'model-{step+1}.npz',payload)
 log.close();(out/'DONE.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':main()
