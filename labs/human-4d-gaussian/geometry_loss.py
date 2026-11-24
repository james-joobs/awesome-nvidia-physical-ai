"""Real differentiable depth/normal supervision, not a placeholder normal tensor."""
import json,math
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from fdanyone.reconstruction.rasterizer import Camera

def render_geometry(model,camera,time,threshold,unit):
 from gsplat.cuda._wrapper import fully_fused_projection,isect_offset_encode,isect_tiles,rasterize_to_pixels
 H,W=camera.height,camera.width
 xyz,cov,rgb,opacity,_=model.evaluate(time,camera.center,threshold,visibility=camera.visible,packed=True)
 radii,means,depths,conics,_=fully_fused_projection(xyz,cov,None,None,camera.view[None],camera.k[None],W,H,packed=False,near_plane=camera.near,far_plane=camera.far)
 _,intersections,flatten=isect_tiles(means,radii,depths,16,math.ceil(W/16),math.ceil(H/16),packed=False,n_images=1)
 offsets=isect_offset_encode(intersections,1,math.ceil(W/16),math.ceil(H/16))
 # Additional feature channels are camera-space z and z squared; alpha is retained.
 features=torch.cat([rgb,depths[0,:,None]*unit,(depths[0,:,None]*unit).square()],-1)
 image,alpha=rasterize_to_pixels(means,conics,features[None],opacity[None],W,H,16,offsets,flatten,packed=False,absgrad=False)
 alpha=alpha[0,...,0];depth=image[0,...,3]/alpha.clamp_min(1e-5);var=(image[0,...,4]/alpha.clamp_min(1e-5)-depth.square()).clamp_min(0)
 return depth,alpha,var

def depth_normals(depth,K):
 H,W=depth.shape;y,x=torch.meshgrid(torch.arange(H,device=depth.device),torch.arange(W,device=depth.device),indexing='ij');xyz=torch.stack([(x+.5-K[0,2])/K[0,0]*depth,(y+.5-K[1,2])/K[1,1]*depth,depth],-1)
 dx=xyz[1:-1,2:]-xyz[1:-1,:-2];dy=xyz[2:,1:-1]-xyz[:-2,1:-1];normal=F.normalize(torch.linalg.cross(dy,dx),dim=-1,eps=1e-6)
 return normal

class GeometryLoss:
 def __init__(self,root,settings,device):
  self.root=Path(root);self.rows=json.loads((self.root/'index.json').read_text());self.settings=settings;self.rng=np.random.default_rng(621);self.cache=[]
  for row in self.rows:
   z=np.load(self.root/row['file']);self.cache.append({k:torch.tensor(z[k],device=device) for k in ['depth','mask','normal']})
  self.cameras=[Camera(row['camera'],device,far=settings['far'],near=settings['near'],space_scale=settings['space_scale'],image_scale=1.) for row in self.rows]
 def __call__(self,model,step):
  i=int(self.rng.integers(len(self.rows)));row=self.rows[i];prior=self.cache[i];camera=self.cameras[i]
  depth,alpha,var=render_geometry(model,camera,row['time'],self.settings['marginal_threshold'],self.settings['space_scale']);valid=prior['mask'].bool()&(alpha.detach()>.9)&torch.isfinite(depth.detach())
  depth_loss=(depth[valid]-prior['depth'][valid]).abs().clamp(max=.25).mean() if valid.any() else depth.sum()*0
  n=depth_normals(depth,camera.k);pm=valid[1:-1,1:-1]&valid[2:,1:-1]&valid[:-2,1:-1]&valid[1:-1,2:]&valid[1:-1,:-2];pn=prior['normal'][1:-1,1:-1];pm&=(pn.square().sum(-1)>.5)
  normal_loss=(1-(n[pm]*pn[pm]).sum(-1).abs().clamp(max=1)).mean() if pm.any() else depth.sum()*0
  loss=row.get('weight',1.)*(.06*depth_loss+.008*normal_loss)
  return loss,{'geometry_depth':depth_loss,'geometry_normal':normal_loss,'geometry_loss':loss}
