"""Pinned MoGe-3 inference; isolated environment, no change to reconstruction env."""
import argparse,json,sys,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import torch
import torch.nn.functional as F
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path);p.add_argument('--cameras',default='0,2,3,4');a=p.parse_args();r=a.root;w=r/'multiview-prior';e=w/'refinement';out=a.out or e/'moge-raw';out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(e/'moge-source'))
from moge.model.v3 import MoGeModel
torch.set_num_threads(8);model=MoGeModel.from_pretrained(e/'moge-model/model.pt').to('cuda').eval();cameras=json.loads((a.data/'cameras.json').read_text())['cameras'];records=[];started=time.monotonic()
for cid in [int(x) for x in a.cameras.split(',')]:
 row=cameras[cid];K=np.asarray(row['K']);c2w=np.asarray(row['camera_to_world']);H,W=row['image_height'],row['image_width'];sx,sy=352/W,640/H;k=K.copy();k[0]*=sx;k[1]*=sy;camera={'name':f'moge-{cid}','K':k.tolist(),'w2c':np.linalg.inv(c2w).tolist(),'height':640,'width':352};pad_left=max(0,int(round(W-2*K[0,2])));pad_right=max(0,int(round(2*K[0,2]-W)));pad_top=max(0,int(round(H-2*K[1,2])));pad_bottom=max(0,int(round(2*K[1,2]-H)));Wp=W+pad_left+pad_right;Hp=H+pad_top+pad_bottom;fov=float(np.rad2deg(2*np.arctan(Wp/(2*K[0,0]))))
 for t in [0,24,48,72,96,120]:
  path=out/f'{cid:02d}-{t:03d}.npz'
  if not path.exists():
   # Use the source file of the actual reconstruction camera, so K and crop agree.
   pil=Image.open(a.data/f'images/{cid:02d}/{t:06d}.jpg').convert('RGB');pil=ImageOps.expand(pil,border=(pad_left,pad_top,pad_right,pad_bottom),fill=(235,235,235));image=np.asarray(pil.resize((540,int(round(Hp*540/Wp))),Image.Resampling.LANCZOS)).copy();tensor=torch.tensor(image,device='cuda').permute(2,0,1).float()/255
   prediction=model.infer(tensor,resolution_level=5,refine_steps=3,fov_x=fov,use_fp16=True)
   def unpad(value,mode):
    resized=F.interpolate(value,(Hp,Wp),mode=mode,**({'align_corners':False} if mode=='bilinear' else {}));resized=resized[:,:,pad_top:pad_top+H,pad_left:pad_left+W];return F.interpolate(resized,(640,352),mode=mode,**({'align_corners':False} if mode=='bilinear' else {}))
   depth=unpad(prediction['depth'][None,None],'bilinear')[0,0];mask=unpad(prediction['mask'][None,None].float(),'nearest')[0,0]>.5
   normal=prediction.get('normal');normal_source='normal_head' if normal is not None else 'depth_finite_differences'
   if normal is not None:normal=F.normalize(unpad(normal.permute(2,0,1)[None],'bilinear')[0].permute(1,2,0),dim=-1)
   else:
    yy,xx=torch.meshgrid(torch.arange(640,device='cuda'),torch.arange(352,device='cuda'),indexing='ij');xyz=torch.stack([(xx+.5-k[0,2])/k[0,0]*depth,(yy+.5-k[1,2])/k[1,1]*depth,depth],-1);dx=xyz[1:-1,2:]-xyz[1:-1,:-2];dy=xyz[2:,1:-1]-xyz[:-2,1:-1];normal=torch.zeros_like(xyz);normal[1:-1,1:-1]=F.normalize(torch.linalg.cross(dy,dx),dim=-1)
   np.savez_compressed(path,depth=depth.cpu().numpy(),mask=mask.cpu().numpy(),normal=normal.cpu().numpy(),normal_source=np.asarray(normal_source))
   print('MOGE3_INFERENCE',cid,t,round(time.monotonic()-started,2),flush=True)
  records.append({'file':path.name,'camera':camera,'frame':t,'time':t/30,'camera_id':cid,'data_mask':str(a.data/f'fmasks/{cid:02d}/{t:06d}.png'),'weight':1. if cid==0 else .25,'fov_x_estimated':fov,'principal_point_padding_ltrb':[pad_left,pad_top,pad_right,pad_bottom],'normal_source':str(np.load(path)['normal_source'])})
(out/'index.json').write_text(json.dumps(records,indent=2)+'\n');(out/'PROVENANCE.json').write_text(json.dumps({'model':'Ruicheng/moge-3-vitl','model_revision':'184008f877d7ad1ad4c2cd2182a9bd1f63d0e5be','code':'74fbce054ebed49800de42d0ad0e83495065719a','license':'MIT','refine_steps':3,'resolution_level':5,'same_time_multiview':True,'fov':'Estimated SOMA/known virtual camera K, not physical camera calibration','scope':'RGB-inferred weak geometry. Generated camera depth is not ground truth. Metric scale will be aligned to existing model.'},indent=2)+'\n');print('MOGE3_RAW_DONE',flush=True)
