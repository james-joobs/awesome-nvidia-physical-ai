"""Observed-mask repair using two neighboring RGB flow warps.

Creates new training data and original-pixel edge crops. Never changes source
masks or RGB and never changes the renderer. Review the masks before training.
"""
import argparse,json,hashlib,shutil
from pathlib import Path
import cv2,numpy as np
from PIL import Image
def roi_joint_groups(names):
 if len(set(names))!=len(names):raise ValueError('The fitted rig has duplicate public joint names')
 face=['Head','HeadEnd','Jaw','LeftEye','RightEye']
 if not all(name in names for name in face):raise ValueError('Expected named SOMA head/face joints in rig.json')
 groups=[('face',[names.index(name) for name in face])]
 for side in ['Left','Right']:
  indices=[i for i,name in enumerate(names) if name.startswith(side+'Hand')]
  if len(indices)<2:raise ValueError(f'Missing named {side}Hand joints in rig.json')
  groups.append((side.lower()+'-hand',indices))
 return groups

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--frame',type=int,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--original-frames',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
r=a.root.expanduser().resolve();case=r/'multiview-prior'/a.name;out=a.out.expanduser().resolve();a.data=a.data.expanduser().resolve();a.original_frames=a.original_frames.expanduser().resolve()
if out.is_relative_to(Path(__file__).resolve().parents[2]/'site/public'):raise ValueError('Mask diagnostics contain local RGB and must stay outside site/public')
for protected in [a.data,a.original_frames,r/'frames',r/'masks',r/'rig']:
 if out.is_relative_to(protected):raise ValueError('Repair output must be separate from source RGB, masks, geometry and training data')
if out.exists() and any(out.iterdir()):raise ValueError('Use a new isolated mask-repair output folder')
g=np.load(r/'rig/geometry.npz',allow_pickle=False);meta=json.loads((r/'input.json').read_text());rig_path=r/'rig/rig.json';names=json.loads(rig_path.read_text())['public_joint_names'];groups=roi_joint_groups(names)
if g['joints'].ndim!=3 or g['joints'].shape[1]!=len(names):raise ValueError('Fitted joints and rig.json names disagree')
adapter=json.loads((case/'adapter.json').read_text());condition=np.load(case/'soma-conditioning.npz',allow_pickle=False);ids=condition['frame_ids']
if ids.shape!=(121,) or not np.issubdtype(ids.dtype,np.integer) or (ids<0).any() or (ids>=len(g['joints'])).any():raise ValueError('Expected 121 valid prepared-frame indices')
if not np.array_equal(ids,np.asarray(adapter['source_frames'])):raise ValueError('Adapter and fitted conditioning use different source-frame windows')
if not 0<a.frame<len(g['joints'])-1:raise ValueError('Two adjacent observed RGB frames are required')
local=np.flatnonzero(ids==a.frame)
if len(local)!=1:raise ValueError('Choose one unpadded source frame present exactly once in this interval')
t0=int(local[0]);source=a.frame
# The original-pixel cache must belong to this exact interval. A matching image
# size alone cannot distinguish the preceding interval from the selected one.
request_path=a.original_frames.parent/'frame-request.json'
if not request_path.is_file():raise ValueError('Original RGB cache needs fresh_roi.py frame-request.json; rebuild the cache before mask repair')
request=json.loads(request_path.read_text())
if request.get('source_frame_ids')!=ids.tolist() or request.get('size')!=[meta['width'],meta['height']] or request.get('source_sha256')!=hashlib.sha256((r/'input.mp4').read_bytes()).hexdigest():raise ValueError('Original RGB cache belongs to a different source/window')
rgb=cv2.imread(str(r/f'frames/{source+1:06d}.jpg'));original=cv2.imread(str(r/f'masks/{source+1:06d}.png'),cv2.IMREAD_GRAYSCALE)
if rgb is None or original is None or rgb.shape[:2]!=original.shape:raise ValueError('Missing or mismatched observed RGB/mask')
gray=cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY);H,W=gray.shape;yy,xx=np.mgrid[:H,:W].astype(np.float32);warps=[];inputs=[rig_path,request_path,case/'adapter.json',case/'soma-conditioning.npz']
out.mkdir(parents=True,exist_ok=True)
for neighbor in [source-1,source+1]:
 im=cv2.imread(str(r/f'frames/{neighbor+1:06d}.jpg'));
 if im is None or im.shape[:2]!=(H,W):raise ValueError('Missing or mismatched adjacent RGB frame')
 flow=cv2.calcOpticalFlowFarneback(gray,cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),None,.5,5,25,5,7,1.5,cv2.OPTFLOW_FARNEBACK_GAUSSIAN);mask=cv2.imread(str(r/f'masks/{neighbor+1:06d}.png'),cv2.IMREAD_GRAYSCALE);
 if mask is None or mask.shape!=(H,W):raise ValueError('Missing or mismatched adjacent mask')
 warps.append(cv2.remap(mask,xx+flow[...,0],yy+flow[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT));inputs += [r/f'frames/{neighbor+1:06d}.jpg',r/f'masks/{neighbor+1:06d}.png']
K=g['K'][source].copy();K[0]*=W/meta['width'];K[1]*=H/meta['height'];head=g['joints'][source,[names.index('Head'),names.index('HeadEnd')]].mean(0);uv=K@head;
if not np.isfinite(uv).all() or uv[2]<=0:raise ValueError('Head projects behind/outside the calibrated camera')
uv=uv[:2]/uv[2];region=((xx-uv[0])/(105*W/540))**2+((yy-uv[1])/(135*H/960))**2<=1;consensus=np.minimum(*warps);corrected=original.copy();corrected[region]=np.maximum(original[region],consensus[region]);mask_out=out/'corrected-mask';mask_out.mkdir();cv2.imwrite(str(mask_out/f'{source+1:06d}.png'),corrected)
# All six repeated observed cameras represent the same input; correct each copy
# with exactly the same calibrated crop as the original dataset.
data=out/'data';cameras=json.loads((a.data/'cameras.json').read_text());source_camera=cameras['cameras'][0]
def same_calibration(row):return np.allclose(row['camera_to_world'],source_camera['camera_to_world']) and np.allclose(row['K'],source_camera['K'])
if any('supervision' in row for row in cameras['cameras']):
 observed=[row['camera_id'] for row in cameras['cameras'] if row.get('supervision')=='observed']
 if source_camera.get('supervision')!='observed' or any(not same_calibration(row) for row in cameras['cameras'] if row.get('supervision')=='observed'):raise ValueError('Observed copies must share the calibrated source camera')
else:observed=[row['camera_id'] for row in cameras['cameras'] if same_calibration(row)]
if not observed:raise ValueError('No calibrated observed-camera mask copies were found')
data.mkdir();shutil.copytree(a.data/'images',data/'images',symlinks=True);shutil.copytree(a.data/'fmasks',data/'fmasks',symlinks=False)
c=adapter['source_crop'];patch=Image.fromarray(corrected).crop((c['left'],c['top'],c['left']+c['width'],c['top']+c['height'])).resize((int(source_camera['image_width']),int(source_camera['image_height'])),Image.Resampling.LANCZOS)
for cid in observed:patch.save(data/f'fmasks/{cid:02d}/{t0:06d}.png')
(data/'cameras.json').write_text(json.dumps(cameras,indent=2)+'\n');dm=json.loads((a.data/'metadata.json').read_text());dm['source_identity']+='; one observed head mask repaired from bidirectional adjacent-RGB foreground agreement';(data/'metadata.json').write_text(json.dumps(dm,indent=2)+'\n')
# Rebuild RGB from the untouched original-resolution PNG cache: the old
# premultiplied RGBA crop cannot recover pixels discarded by a broken alpha.
roi=out/'roi';roi.mkdir();rows=[];pixels=[];S=np.diag([1.,-1.,-1.]);C=np.eye(4);C[:3,:3]=S;C[:3,3]=-S@condition['world_origin'];IW,IH=meta['width'],meta['height'];edge_frames=sorted(set(list(range(8))+list(range(113,121))+[t0]))
for t in edge_frames:
 i=int(ids[t]);original_path=a.original_frames/f'{t+1:06d}.png';inputs.append(original_path);image=np.asarray(Image.open(original_path).convert('RGB'));assert image.shape==(IH,IW,3);mask=corrected if i==source else cv2.imread(str(r/f'masks/{i+1:06d}.png'),cv2.IMREAD_GRAYSCALE);alpha=np.asarray(Image.fromarray(mask).resize((IW,IH),Image.Resampling.BILINEAR));K=g['K'][i];q=g['joints'][i]@K.T;xy=q[:,:2]/q[:,2:]
 for part,joints in groups:
  center=np.median(xy[joints],axis=0)
  if not np.isfinite(center).all():continue
  x,y=np.clip(np.rint(center-128).astype(int),[0,0],[IW-256,IH-256]);m=alpha[y:y+256,x:x+256].astype(np.float32)/255
  if m[96:160,96:160].mean()<.3:continue
  k=K.copy();k[0,2]-=x;k[1,2]-=y;rows.append({'frame':t,'source_frame':i,'time':t/30,'part':part,'crop_xywh':[int(x),int(y),256,256],'split':'train','camera':{'name':f'{t}-{part}','K':k.tolist(),'w2c':np.linalg.inv(C).tolist(),'height':256,'width':256}});px=np.concatenate([image[y:y+256,x:x+256].astype(np.float32)/255*m[...,None],m[...,None]],-1);pixels.append(np.rint(px*255).astype('uint8').transpose(2,0,1))
assert any(row['frame']==t0 and row['part']=='face' for row in rows),'Corrected original face ROI is still missing'
np.savez_compressed(roi/'pixels.npz',pixels=np.stack(pixels));(roi/'crops.json').write_text(json.dumps(rows,indent=2)+'\n');inputs += [r/f'frames/{source+1:06d}.jpg',r/f'masks/{source+1:06d}.png',a.data/'cameras.json'];report={'schema':1,'source_frame':source,'local_frame':t0,'method':'Conservative intersection of both adjacent observed-RGB optical-flow warped masks, union within the head neighborhood only','changed_working_pixels':int((corrected!=original).sum()),'observed_cameras_corrected':observed,'head_joint_names':['Head','HeadEnd'],'manual_review_required':True,'roi_rows':len(rows),'roi_split':'train; final build, not held-out validation','rendering_changed':False,'original_masks_unchanged':True,'inputs':[{'path':str(x),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in inputs]};(out/'PREPARED.json').write_text(json.dumps(report,indent=2)+'\n');print('CORRECTED_DATA_READY',json.dumps(report),flush=True)
