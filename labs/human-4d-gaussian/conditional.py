"""Stable factorization for pose-initialized conditional 4D refinement.

Spatial covariance can change without changing the prescribed temporal
variance or trajectory velocity. The saved model is converted back to the
standard native 4D Gaussian archive for the shared renderer/viewer.
"""
from pathlib import Path
import json
import numpy as np
import torch
from torch import nn
from scipy.spatial.transform import Rotation


def quaternion_matrix(q):
 q=torch.nn.functional.normalize(q,dim=-1);w,x,y,z=q.unbind(-1)
 return torch.stack([1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)],-1).reshape(-1,3,3)


class ConditionalGaussians(nn.Module):
 names=('xyz','time','scale','time_scale','left','right','opacity','dc','sh')
 def __init__(self,native):
  super().__init__();self.degree=native.degree
  with torch.no_grad():
   S,velocity,var=native.covariance();values,basis=np.linalg.eigh(S.cpu().double().numpy());values=np.maximum(values,1e-10);basis[:,:,0]*=np.linalg.det(basis)[:,None];q=Rotation.from_matrix(basis).as_quat()[:,[3,0,1,2]];value=torch.tensor(values,device=native.xyz.device,dtype=torch.float32);self.register_buffer('velocity',velocity.detach().clone())
   tensors={**native.tensors(),'scale':value.sqrt().log().float(),'left':torch.tensor(q,device=native.xyz.device,dtype=torch.float32),'time_scale':var.sqrt().log()}
  for name in self.names:self.register_parameter(name,nn.Parameter(tensors[name].detach().clone().float().contiguous(),requires_grad=name not in ('time','time_scale','right')))
 def __len__(self):return len(self.xyz)
 def covariance(self,packed=False):
  R=quaternion_matrix(self.left);S=(R*self.scale.exp().square()[:,None,:])@R.transpose(1,2)
  if packed:S=S[:,[0,0,0,1,1,2],[0,1,2,1,2,2]]
  return S,self.velocity,self.time_scale.mul(2).exp()
 def evaluate(self,time,camera_center,threshold,visibility=None,packed=False):
  from fdanyone.reconstruction.gaussian import evaluate_conditional
  return evaluate_conditional(self,self.covariance(packed),time,camera_center,threshold,visibility)
 def tensors(self):return {name:getattr(self,name).detach() for name in self.names}


def save_native(path,model,metadata):
 from warmstart import rotation_pair,save
 with torch.no_grad():
  S,v,var=model.covariance();S=S.cpu().double().numpy();v=v.cpu().double().numpy();var=var[:,0].cpu().double().numpy();C=np.zeros((len(model),4,4));C[:,:3,:3]=S+var[:,None,None]*v[:,:,None]*v[:,None,:];C[:,:3,3]=v*var[:,None];C[:,3,:3]=v*var[:,None];C[:,3,3]=var;values,R=np.linalg.eigh(C);R[:,:,0]*=np.linalg.det(R)[:,None];left,right,error=rotation_pair(R);logs=np.log(np.maximum(values,1e-12))*.5;arrays={k:v.cpu().numpy() for k,v in model.tensors().items()};arrays.update(scale=logs[:,:3],time_scale=logs[:,3:],left=left,right=right);save(path,arrays,metadata)
 return error
