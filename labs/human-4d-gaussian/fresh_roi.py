"""Observed original-resolution crops for one fresh diffusion interval.

Default input is the pipeline's prepared 30 Hz video. The explicit stride
option also permits frame-indexed evaluation of a constant-rate local source;
it never downloads a video or infers a raw-variable-FPS correspondence.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,time
from pathlib import Path
import numpy as np
from PIL import Image

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--source-stride',type=int,default=1);p.add_argument('--source-offset',type=int,default=0);a=p.parse_args()
 if a.source_stride<1 or a.source_offset<0:raise ValueError('Frame stride must be positive and offset nonnegative')
 r=a.root;w=r/'multiview-prior';case=w/a.name;out=a.out;out.mkdir(parents=True,exist_ok=True);adapter=json.loads((case/'adapter.json').read_text());ids=np.asarray(adapter['source_frames'],dtype=int);valid=int(adapter.get('valid_frames',len(ids)));input_meta=json.loads((r/'input.json').read_text());W,H=input_meta['width'],input_meta['height']
 if len(ids)!=121 or valid<1 or valid>121:raise ValueError('Expected a 121-frame internal window with a valid observed count')
 raw_ids=ids*a.source_stride+a.source_offset;frames=out/'source-frames'
 request={'source_sha256':hashlib.sha256((r/'input.mp4').read_bytes()).hexdigest(),'source_frame_ids':ids.tolist(),'raw_frame_ids':raw_ids.tolist(),'size':[W,H]}
 request_path=out/'frame-request.json'
 if request_path.exists() and json.loads(request_path.read_text())!=request:raise ValueError('Original-resolution cache belongs to a different input/window; choose a fresh output directory')
 request_path.write_text(json.dumps(request,indent=2)+'\n')
 if not frames.exists():
  temp=out/f'source-frames.partial-{time.time_ns()}';temp.mkdir()
  select=f'select=between(n\\,{int(raw_ids[0])}\\,{int(raw_ids[valid-1])})*not(mod(n-{a.source_offset}\\,{a.source_stride}))'
  subprocess.run([str(r/'bin/ffmpeg'),'-hide_banner','-loglevel','error','-threads','4','-i',str(r/'input.mp4'),'-vf',select,'-fps_mode','vfr','-frames:v',str(valid),'-threads','4',str(temp/'%06d.png')],check=True)
  decoded=sorted(temp.glob('*.png'))
  if len(decoded)!=valid:raise ValueError(f'Only {len(decoded)}/{valid} indexed RGB frames decoded; partial files preserved in {temp}')
  for t in range(valid,121):shutil.copy2(decoded[-1],temp/f'{t+1:06d}.png')
  temp.replace(frames)
 if len(list(frames.glob('*.png')))!=121:raise ValueError('Incomplete original-resolution cache; preserve this run and choose a new output directory')
 g=np.load(r/'rig/geometry.npz');j=g['joints'][ids];K=g['K'][ids];origin=np.load(case/'soma-conditioning.npz')['world_origin'];S=np.diag([1.,-1.,-1.]);C=np.eye(4);C[:3,:3]=S;C[:3,3]=-S@origin;rows=[];pixels=[]
 for t,i in enumerate(ids):
  rgb=np.asarray(Image.open(frames/f'{t+1:06d}.png').convert('RGB'))
  if rgb.shape!=(H,W,3):raise ValueError('Input metadata and original-resolution RGB dimensions disagree')
  alpha=np.asarray(Image.open(r/f'masks/{i+1:06d}.png').resize((W,H),Image.Resampling.BILINEAR));q=j[t]@K[t].T;xy=q[:,:2]/q[:,2:]
  for part,joint_ids in [('face',[6,7,8,9,10]),('left-hand',list(range(14,39))),('right-hand',list(range(42,67)))]:
   center=np.median(xy[joint_ids],axis=0)
   if not np.isfinite(center).all():continue
   x,y=np.clip(np.rint(center-128).astype(int),[0,0],[W-256,H-256]);mask=alpha[y:y+256,x:x+256].astype(np.float32)/255
   if mask[96:160,96:160].mean()<.3:continue
   k=K[t].copy();k[0,2]-=x;k[1,2]-=y;rows.append({'frame':t,'source_frame':int(i),'time':t/30,'part':part,'crop_xywh':[int(x),int(y),256,256],'split':'eval' if t%5==0 else 'train','camera':{'name':f'{t}-{part}','K':k.tolist(),'w2c':np.linalg.inv(C).tolist(),'height':256,'width':256}})
   px=np.concatenate([rgb[y:y+256,x:x+256].astype(np.float32)/255*mask[...,None],mask[...,None]],-1);pixels.append(np.rint(px*255).astype(np.uint8).transpose(2,0,1))
 if not pixels or not any(x['split']=='train' for x in rows):raise ValueError('No usable observed face/hand crops; inspect foreground coverage and fitted joints')
 np.savez_compressed(out/'pixels.npz',pixels=np.stack(pixels));(out/'crops.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'PROVENANCE.json').write_text(json.dumps({**request,'valid_frames':valid,'roi_resolution':[256,256],'cropped_rgb_resized':False,'mask':'Predicted SAM2 coverage resized to original resolution, not manual ground truth','scope':'ROI validation times already participated in low-resolution conditioning/training'},indent=2)+'\n');print('FRESH_ORIGINAL_ROI',len(rows),flush=True)

if __name__=='__main__':main()
