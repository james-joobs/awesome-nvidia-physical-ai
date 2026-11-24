"""CPU foreground-mask coverage review; never modifies masks or training data."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path);p.add_argument('--threshold',type=float,default=.6);p.add_argument('--max-contacts',type=int,default=12);a=p.parse_args();r=a.root;out=a.out or r/'diagnostics/masks';out.mkdir(parents=True,exist_ok=True);meta=json.loads((r/'input.json').read_text());rig=json.loads((r/'rig/rig.json').read_text());names=rig['public_joint_names'];head_ids=[names.index('Head'),names.index('HeadEnd')];g=np.load(r/'rig/geometry.npz');T=meta['frames'];J=g['joints'];V=g['vertices'];K=g['K']
 if any(len(g[k])!=T for k in ['joints','vertices','K']):raise ValueError('Prepared RGB and fitted geometry frame counts differ')
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
 except OSError:font=ImageFont.load_default()
 records=[]
 for i in range(T):
  path=r/f'masks/{i+1:06d}.png';mask=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
  if mask is None:raise ValueError(f'Missing source mask at prepared frame{i}')
  H,W=mask.shape;k=K[i].copy();k[0]*=W/meta['width'];k[1]*=H/meta['height'];head=J[i,head_ids].mean(0);points=V[i][np.linalg.norm(V[i]-head,axis=-1)<.13];q=points@k.T
  if len(points)<3 or not np.isfinite(q).all() or (q[:,2]<=0).any():records.append({'frame':i,'flag':'invalid_head_projection'});continue
  xy=q[:,:2]/q[:,2:];region=np.zeros(mask.shape,np.uint8);cv2.fillConvexPoly(region,cv2.convexHull(np.rint(xy).astype(np.int32)),1);values=mask[region.astype(bool)].astype(np.float32)/255;uv=k@head;uv=uv[:2]/uv[2]
  if not len(values):records.append({'frame':i,'flag':'head_outside_image'});continue
  row={'frame':i,'time':i/30,'head_alpha_mean':float(values.mean()),'head_hole_fraction':float((values<.5).mean()),'head_xy':uv.tolist(),'mask':f'masks/{i+1:06d}.png','mask_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'flag':'review_low_coverage' if values.mean()<a.threshold else None};records.append(row)
 flags=[x for x in records if x.get('flag')];contacts=[]
 for flagged in flags[:a.max_contacts]:
  source=flagged['frame'];neighbors=sorted(set(max(0,min(T-1,source+d)) for d in [-1,0,1,2]));canvas=Image.new('RGB',(240*len(neighbors),750),'white');draw=ImageDraw.Draw(canvas)
  for ci,i in enumerate(neighbors):
   row=records[i];rgb=np.asarray(Image.open(r/f'frames/{i+1:06d}.jpg').convert('RGB'));mask=np.asarray(Image.open(r/f'masks/{i+1:06d}.png').convert('L'));uv=np.asarray(row.get('head_xy',[rgb.shape[1]/2,rgb.shape[0]/2]));x,y=np.rint(uv-[90,90]).astype(int);crop=(int(x),int(y),int(x+180),int(y+180));overlay=np.rint(rgb*.7+np.array([255,0,0])[None,None]*(1-mask[...,None]/255)*.3).clip(0,255).astype('uint8');overlay[mask>127]=rgb[mask>127]
   for ri,im in enumerate([Image.fromarray(rgb),Image.fromarray(mask).convert('RGB'),Image.fromarray(overlay)]):canvas.paste(im.crop(crop).resize((240,240)),(ci*240,ri*240+30))
   draw.text((ci*240+4,5),f'RGB / alpha / missing red {i/30:.3f}s',font=font,fill='#34454f')
  filename=f'mask-frame-{source:06d}.jpg';canvas.save(out/filename,quality=96);contacts.append(filename)
 report={'schema':1,'frames':T,'threshold':a.threshold,'flagged_frames':flags,'contacts':contacts,'measurements':records,'scope':'Estimated SOMA head-surface projection compared with predicted source foreground masks; review only, not ground truth or an automatic repair','source_masks_modified':False,'gpu_used':False};(out/'coverage.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'frames':T,'flagged_frames':[x['frame'] for x in flags],'report':str(out/'coverage.json'),'review_only':True}),flush=True)

if __name__=='__main__':main()
