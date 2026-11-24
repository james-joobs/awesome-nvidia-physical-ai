"""Build calibrated observed-camera data and original-resolution face/hand crops."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image


def window_ids(root,start,frames=121):
 meta=json.loads((root/'input.json').read_text());count=meta['frames']
 if start<0 or start>=count:raise ValueError('Interval starts outside prepared video')
 return np.minimum(np.arange(start,start+frames),count-1),min(frames,count-start),meta


def observed(root,start,out):
 work=root/'multiview-prior';sys.path.insert(0,str(work/'4danyone'))
 from fdanyone.geometry.crop import Crop,transform_intrinsics
 ids,valid,meta=window_ids(root,start);adapter=json.loads((work/'pilot/adapter.json').read_text());crop=Crop(**adapter['source_crop']);source=json.loads((work/'pilot/reconstruction/data/cameras.json').read_text())['cameras'][0]
 g=np.load(root/'rig/geometry.npz');K=g['K'];assert len(K)==meta['frames'],'GEM and prepared RGB frame counts differ'
 if not np.allclose(K[ids],K[ids[0]],rtol=1e-5,atol=1e-3):raise ValueError('This static-camera preset requires constant K within each interval')
 k=K[ids[0]].copy();k[0]*=540/meta['width'];k[1]*=960/meta['height'];k=transform_intrinsics(k,crop);source={**source,'K':k.tolist(),'camera_id':0}
 def cropped(image):return image.crop((crop.left,crop.top,crop.left+crop.width,crop.top+crop.height)).resize((704,1280),Image.Resampling.LANCZOS)
 for sub in ['images','fmasks']:(out/sub/'00').mkdir(parents=True,exist_ok=True)
 for t,i in enumerate(ids):
  cropped(Image.open(root/f'frames/{i+1:06d}.jpg').convert('RGB')).save(out/f'images/00/{t:06d}.jpg',quality=95)
  cropped(Image.open(root/f'masks/{i+1:06d}.png').convert('L')).save(out/f'fmasks/00/{t:06d}.png')
 (out/'cameras.json').write_text(json.dumps({'camera_model':'OPENCV','cameras':[source]},indent=2)+'\n')
 (out/'metadata.json').write_text(json.dumps({'fps':'30','frames':[f'{i:06d}' for i in range(121)],'source_identity':'Actual observed-camera RGB only; later intervals use pose-conditioned appearance initialization, not new multiview diffusion.'},indent=2)+'\n')
 (out/'interval.json').write_text(json.dumps({'start_frame':start,'training_frames':121,'valid_frames':valid,'source_frame_ids':ids.tolist()},indent=2)+'\n')


def roi(root,start,out):
 work=root/'multiview-prior';ids,valid,meta=window_ids(root,start);out.mkdir(parents=True,exist_ok=True);original=root/'original-resolution';original.mkdir(exist_ok=True)
 if len(list(original.glob('*.png')))!=meta['frames']:
  if any(original.iterdir()):raise ValueError('Incomplete original-resolution cache; remove only this cache before retrying')
  subprocess.run([str(root/'bin/ffmpeg'),'-hide_banner','-loglevel','error','-i',str(root/'input.mp4'),'-fps_mode','passthrough','-threads','4',str(original/'%06d.png')],check=True)
 assert len(list(original.glob('*.png')))==meta['frames']
 g=np.load(root/'rig/geometry.npz');j=g['joints'][ids];K=g['K'][ids];origin=np.load(work/'pilot/soma-conditioning.npz')['world_origin'];S=np.diag([1.,-1.,-1.]);C=np.eye(4);C[:3,:3]=S;C[:3,3]=-S@origin;rows=[];pixels=[]
 W,H=meta['width'],meta['height']
 if min(W,H)<256:raise ValueError('Original-resolution ROI preset requires width and height >=256')
 for t,i in enumerate(ids):
  rgb=np.asarray(Image.open(original/f'{i+1:06d}.png').convert('RGB'));assert rgb.shape==(H,W,3)
  alpha=np.asarray(Image.open(root/f'masks/{i+1:06d}.png').resize((W,H),Image.Resampling.BILINEAR));q=j[t]@K[t].T;xy=q[:,:2]/q[:,2:]
  for part,joint_ids in [('face',[6,7,8,9,10]),('left-hand',list(range(14,39))),('right-hand',list(range(42,67)))]:
   center=np.median(xy[joint_ids],axis=0)
   if not np.isfinite(center).all():continue
   x,y=np.clip(np.rint(center-128).astype(int),[0,0],[W-256,H-256]);mask=alpha[y:y+256,x:x+256].astype(np.float32)/255
   if mask[96:160,96:160].mean()<.3:continue
   k=K[t].copy();k[0,2]-=x;k[1,2]-=y;rows.append({'frame':t,'source_frame':int(i),'time':t/30,'part':part,'crop_xywh':[int(x),int(y),256,256],'split':'eval' if t%5==0 else 'train','camera':{'name':f'{t}-{part}','K':k.tolist(),'w2c':np.linalg.inv(C).tolist(),'height':256,'width':256}})
   px=np.concatenate([rgb[y:y+256,x:x+256].astype(np.float32)/255*mask[...,None],mask[...,None]],-1);pixels.append(np.rint(px*255).astype(np.uint8).transpose(2,0,1))
 if not pixels or not any(row['split']=='train' for row in rows):raise ValueError('No usable observed face/hand crops; inspect motion and foreground masks')
 np.savez_compressed(out/'pixels.npz',pixels=np.stack(pixels));(out/'crops.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'PROVENANCE.json').write_text(json.dumps({'source_resolution':[W,H],'start_frame':start,'valid_frames':valid,'cropped_rgb_resized':False,'mask':'Predicted SAM2 coverage resized to original resolution, not manual ground truth','scope':'ROI validation frames still participated in low-resolution conditioning/training'},indent=2)+'\n')


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--start',type=int,default=0);p.add_argument('--out',type=Path,required=True);p.add_argument('--kind',choices=['observed','roi'],required=True);a=p.parse_args();globals()[a.kind](a.root,a.start,a.out);print(json.dumps({'stage':a.kind,'start_frame':a.start,'output':str(a.out)}))
if __name__=='__main__':main()
