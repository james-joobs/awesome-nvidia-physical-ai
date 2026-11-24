"""Align RGB-inferred depth scale, exclude uncertain boundaries/contradictions."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from scipy.ndimage import binary_erosion
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--raw',type=Path);p.add_argument('--out',type=Path);a=p.parse_args();w=a.root/'multiview-prior';e=w/'refinement';sys.path.insert(0,str(w/'4danyone'))
from fdanyone.reconstruction.checkpoint import load_render_model
from fdanyone.reconstruction.rasterizer import Camera
from geometry_loss import render_geometry
torch.set_num_threads(8);meta,model=load_render_model(a.model,'cuda');cfg=meta['config'];out=a.out or e/'moge-aligned';out.mkdir(parents=True,exist_ok=True);raw=a.raw or e/'moge-raw';rows=json.loads((raw/'index.json').read_text());records=[];stats=[]
with torch.no_grad():
 for row in rows:
  z=np.load(raw/row['file']);d=z['depth'];normal=z['normal'];source_mask=np.asarray(Image.open(row['data_mask']).resize((352,640),Image.Resampling.BILINEAR))>240
  camera=Camera(row['camera'],'cuda',far=cfg['far'],near=cfg['near'],space_scale=cfg['space_scale'],image_scale=1.)
  reference,alpha,var=render_geometry(model,camera,row['time'],cfg['marginal_threshold'],cfg['space_scale']);reference=reference.cpu().numpy();alpha=alpha.cpu().numpy()
  mask=source_mask & z['mask'] & np.isfinite(d) & (d>.05) & (alpha>.95) & np.isfinite(reference)
  mask=binary_erosion(mask,iterations=4)
  assert mask.sum()>500
  scale=float(np.median(reference[mask]/d[mask]));aligned=d*scale
  # Only shallow, locally coherent corrections; RGB remains the main objective.
  dy,dx=np.gradient(np.nan_to_num(aligned,nan=0,posinf=0,neginf=0));mask &= (np.abs(aligned-reference)<.2)&(np.hypot(dx,dy)<.04)&np.isfinite(normal).all(-1)
  mask=binary_erosion(mask,iterations=1)
  aligned=np.nan_to_num(aligned,nan=0,posinf=0,neginf=0).astype('float32');normal=np.nan_to_num(normal).astype('float32');normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-6)
  np.savez_compressed(out/row['file'],depth=aligned,normal=normal,mask=mask)
  record={k:v for k,v in row.items() if k!='data_mask'};record['depth_scale_to_model']=scale;record['valid_pixels']=int(mask.sum());record['reference_model']=a.model.name;records.append(record)
  stats.append({'file':row['file'],'scale':scale,'valid_pixels':int(mask.sum()),'mean_abs_depth_before':float(np.abs(aligned[mask]-reference[mask]).mean())})
  normvis=np.where(mask[...,None],(normal*.5+.5)*255,245).astype('uint8');Image.fromarray(normvis).save(out/row['file'].replace('.npz','-normal.png'))
(out/'index.json').write_text(json.dumps(records,indent=2)+'\n');(out/'alignment.json').write_text(json.dumps({'reference_model':str(a.model),'method':'Positive scale-only median ratio on eroded valid foreground, no LiDAR or true depth','normal':'MoGe-3 normal head when present, else finite differences of MoGe-3 point/depth maps','depth_gate_m':.2,'boundary_erosion_pixels':5,'stats':stats},indent=2)+'\n');print('GEOMETRY_ALIGNED',len(records),flush=True)
