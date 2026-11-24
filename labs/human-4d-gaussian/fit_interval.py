"""Full-clip observed RGB refinement of the selected posed 4D appearance prior."""
import argparse,json,sys,time,hashlib
from pathlib import Path
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--geometry',type=Path,required=True);p.add_argument('--steps',type=int,default=6000);a=p.parse_args();r=a.root;w=r/'multiview-prior';out=a.out;sys.path[:0]=[str(w/'4danyone'),str(Path(__file__).resolve().parent)]
 import torch
 from fdanyone.reconstruction.checkpoint import load_render_model
 from fdanyone.reconstruction.data import TrainingData
 from fdanyone.reconstruction.train import make_camera,make_optimizer,make_objective
 from fdanyone.reconstruction.settings import training_settings
 from fdanyone.reconstruction.loader import Sampler,batches
 from fdanyone.reconstruction.rasterizer import render
 from fdanyone.reconstruction.losses import ssim
 from fdanyone.nerfstudio.perceptual import VGG19PerceptualLoss
 from geometry_loss import GeometryLoss
 torch.set_num_threads(8);torch.manual_seed(42);torch.cuda.manual_seed(42);torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
 from conditional import ConditionalGaussians,save_native
 meta,native=load_render_model(out/'warm.npz','cuda');model=ConditionalGaussians(native);del native;_,teacher=load_render_model(out/'warm.npz','cuda')
 for param in teacher.parameters():param.requires_grad_(False)
 data=TrainingData(out/'data',image_scale=1.);settings=training_settings({'steps':a.steps,'perceptual_weight':0.,'loader_workers':4,'bounds':((-1.2,-.1,-.7),(1.2,2.3,.7))});settings['densify_until']=0
 for k in ['xyz_lr','scale_lr','rotation_lr','opacity_lr','dc_lr','sh_lr','time_lr']:settings[k]*=.3
 model.time.requires_grad_(False);settings['xyz_lr']=.0008;optimizer=make_optimizer(model,settings);objective=make_objective(settings,'cuda');camera=make_camera(data.cameras[0],settings,'cuda');sampler=Sampler(len(data),42);base={k:v.clone().detach() for k,v in model.tensors().items()};_,velocity0,var0=teacher.covariance();velocity0=velocity0.detach();var0=var0.detach()
 # The protected views render the pose-transferred prior, not new observations.
 protect=[]
 for i in [2,3,4]:
  c=meta['cameras'][i].copy();c['K']=np.asarray(c['K']).tolist();s={**settings,'image_scale':.25};protect.append(make_camera(c,s,'cuda'))
 rows=json.loads((out/'roi/crops.json').read_text());roi=torch.tensor(np.load(out/'roi/pixels.npz')['pixels'],device='cuda',dtype=torch.float32)/255;rc=[make_camera(x['camera'],settings,'cuda') for x in rows];ids=[i for i,x in enumerate(rows) if x['split']=='train'];rng=np.random.default_rng(91);perceptual=VGG19PerceptualLoss(w/'models/perceptual/imagenet-vgg-verydeep-19-conv.safetensors',compute_dtype='bfloat16',include_rgb=False).to('cuda');geometry=GeometryLoss(a.geometry,settings,'cuda')
 provenance={'start_frame':a.start,'steps':a.steps,'warm_start_sha256':hashlib.sha256((out/'warm.npz').read_bytes()).hexdigest(),'actual_observed_cameras':1,'new_multiview_diffusion':False,'appearance_seed':'Selected first-interval original ROI + MoGe-3 model; pose-transferred through SOMA','protected_views':'Render of pose-conditioned initialization, not observed RGB or new generated video','time_centers_frozen':True,'position_clamp_m':.06,'parameterization':'Spatial covariance learned independently; pose-derived velocities/time variances held fixed','full_precision_parameters':True,'input_source':'User-supplied local footage; no redistribution implied'};(out/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
 torch.cuda.reset_peak_memory_stats();started=time.time();log=(out/'train.jsonl').open('w')
 for step,(pixels,indices) in enumerate(batches(data,sampler,0,a.steps,'cuda',batch_size=4,loader_workers=4,seed=42)):
  optimizer.zero_grad(set_to_none=True);ims=[];alphas=[];metadata=[]
  for index in indices:
   im,alpha,md=render(model,camera,index/30,marginal_threshold=settings['marginal_threshold']);ims.append(im);alphas.append(alpha);metadata.append(md)
  ims=torch.stack(ims);alphas=torch.stack(alphas);loss,terms=objective(ims,alphas,pixels[:,:3],pixels[:,3:],step=step);fg=pixels[:,3:]>.5;loss=loss+.25*((ims-pixels[:,:3]).abs()*fg).sum()/(fg.sum()*3).clamp_min(1)
  ri=ids[int(rng.integers(len(ids)))];im,alpha,_=render(model,rc[ri],rows[ri]['time'],marginal_threshold=settings['marginal_threshold']);bg=torch.rand((3,1,1),device='cuda');pred=im+(1-alpha)*bg;target=roi[ri,:3]+(1-roi[ri,3:])*bg;rl1=(pred-target).abs().mean();rvgg=perceptual(pred[None],target[None]);roi_loss=.6*rl1+.15*(1-ssim(pred[None],target[None]))+.08*rvgg+.08*(alpha-roi[ri,3:]).square().mean();loss+=roi_loss
  if step%2==0:
   gl,gt=geometry(model,step);loss+=gl;terms.update(gt)
  if step%4==0:
   t=float(rng.integers(121))/30;c=protect[int(rng.integers(len(protect)))];pi,pa,_=render(model,c,t,marginal_threshold=settings['marginal_threshold'])
   with torch.no_grad():ti,ta,_=render(teacher,c,t,marginal_threshold=settings['marginal_threshold'])
   prior=.04*(pi-ti).abs().mean()+.04*(pa-ta).square().mean();loss+=prior;terms['posed_prior']=prior
  S,velocity,var=model.covariance();active=metadata[-1][0];anchor=.002*(model.xyz[active]-base['xyz'][active]).square().mean()+.00002*(velocity[active]-velocity0[active]).square().mean()+.001*(torch.log(var[active].clamp_min(1e-8))-torch.log(var0[active].clamp_min(1e-8))).square().mean()+.002*(model.left[active]-base['left'][active]).square().mean();loss+=anchor
  loss.backward();optimizer.step()
  with torch.no_grad():model.xyz.clamp_(base['xyz']-.6,base['xyz']+.6);model.scale.clamp_(base['scale']-.3,base['scale']+.3)
  if step%200==0 or step+1==a.steps:
   row={'step':step+1,'seconds':time.time()-started,'loss':float(loss.detach()),'roi_l1':float(rl1.detach()),'roi_vgg':float(rvgg.detach()),'anchor':float(anchor.detach()),'peak_memory_bytes':torch.cuda.max_memory_allocated(),**{k:float(v.detach()) for k,v in terms.items()}};assert all(np.isfinite(v) for v in row.values());log.write(json.dumps(row)+'\n');log.flush();print(json.dumps(row),flush=True)
  if (step+1)%3000==0 or step+1==a.steps:
   md={**meta,'step':step+1,'cameras':data.cameras,'times':data.times.tolist(),'fps':'30','config':{k:settings[k] for k in ['image_scale','space_scale','near','far','marginal_threshold']}};save_native(out/f'model-{step+1}.npz',model,md)

 log.close();(out/'DONE.json').write_text(json.dumps(row,indent=2)+'\n')
if __name__=='__main__':main()
