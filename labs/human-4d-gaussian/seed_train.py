"""Reconstruct generated views + weighted observed RGB with native 4D Gaussians.

Uses the released 4DAnyone reconstruction implementation, with a separately
prepared dataset retaining the calibrated original source view. Not the
paper's FreeTimeGS implementation and not novel-view ground truth.
"""
import argparse,json,sys,time,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
def validate_data_plan(out,plan):
 """Reject changed slot mappings before touching a cached image or mask."""
 receipt=out/'data-plan.json'
 if receipt.exists():
  if json.loads(receipt.read_text())!=plan:raise ValueError('Cached seed data uses a different source/view selection; preserve it and choose a fresh interval name/output root')
  return
 prior=out/'PROVENANCE.json'
 if prior.is_file():
  saved=json.loads(prior.read_text())
  if saved.get('source_frames')!=plan['source_frames'] or sorted(saved.get('explicitly_rejected_generated_camera_ids',[]))!=plan['excluded_generated_camera_ids']:raise ValueError('Cached seed data has a different camera exclusion/slot mapping; it cannot be relabeled in place')
 elif (out/'data').exists() and any((out/'data').iterdir()):raise ValueError('Unknown existing seed data has no view-plan receipt; preserve it and choose a fresh interval name')
 out.mkdir(parents=True,exist_ok=True);temporary=receipt.with_suffix('.json.tmp');temporary.write_text(json.dumps(plan,indent=2)+'\n');temporary.replace(receipt)

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',default='pilot');p.add_argument('--steps',type=int,default=20000);p.add_argument('--stop-after',type=int,default=10000);p.add_argument('--exclude-generated-cameras',default='');p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
 excluded={int(x) for x in a.exclude_generated_cameras.split(',') if x}
 if not excluded <= set(range(1,6)):raise ValueError('Only synthetic base cameras1..5 may be excluded; observed copies stay intact')
 r=a.root.expanduser().resolve();work=r/'multiview-prior';source=work/a.name;out=source/'reconstruction'
 adapter=json.loads((source/'adapter.json').read_text());generated=json.loads((source/'generation.json').read_text());source_ids=adapter['source_frames']
 validate_data_plan(out,{'schema':1,'source_frames':source_ids,'excluded_generated_camera_ids':sorted(excluded),'adapter_sha256':hashlib.sha256((source/'adapter.json').read_bytes()).hexdigest(),'conditioning_sha256':hashlib.sha256((source/'soma-conditioning.npz').read_bytes()).hexdigest(),'generation_sha256':hashlib.sha256((source/'generation.json').read_bytes()).hexdigest()})
 sys.path.insert(0,str(work/'4danyone'))
 from fdanyone.video import iter_rgb_video
 from fdanyone.geometry.crop import Crop,transform_intrinsics
 from fdanyone.foreground import iter_foreground_masks
 from fdanyone.reconstruction.data import TrainingData,write_json
 from fdanyone.reconstruction.settings import training_settings
 from fdanyone.reconstruction.carve import carve
 from fdanyone.reconstruction.initialization import InitialPoints
 from fdanyone.reconstruction.train import train
 from fdanyone.reconstruction.pipeline import check_runtime
 from contextlib import closing
 import torch
 torch.set_num_threads(8)
 crop=Crop(**adapter['source_crop']);H,W=1280,704
 data=out/'data';data.mkdir(exist_ok=True)
 def cropped(im):return im.crop((crop.left,crop.top,crop.left+crop.width,crop.top+crop.height)).resize((W,H),Image.Resampling.LANCZOS)
 camrows=[]
 # Replace generated camera 0 with the actual source camera, and duplicate that
 # observed camera twice for explicit3:(5-rejected) loss sampling. No duplicate
 # is an independent camera measurement; this is loss weighting only.
 origin=np.load(source/'soma-conditioning.npz')['world_origin'];S=np.diag([1.,-1.,-1.]);c2w=np.eye(4);c2w[:3,:3]=S;c2w[:3,3]=-S@origin
 K=np.asarray(adapter['source_K']).copy();source_w,source_h=adapter.get('source_input_size',[1080,1920]);K[0]*=540/source_w;K[1]*=960/source_h;K=transform_intrinsics(K,crop)
 observed={**adapter['cameras'][0],'position':c2w[:3,3].tolist(),'K':K.tolist(),'world_to_camera':np.linalg.inv(c2w).tolist(),'camera_to_world':c2w.tolist(),'image_width':W,'image_height':H}
 for original_id in range(8):
  if original_id in excluded:continue
  cid=len(camrows);is_real=original_id in [0,6,7];cam={**(observed if is_real else adapter['cameras'][original_id]),'camera_id':cid,'supervision':'observed' if is_real else 'generated','original_generated_camera_id':None if is_real else original_id,'generator_pass':None if is_real else 'base'};camrows.append(cam)
  images=data/f'images/{cid:02d}';masks=data/f'fmasks/{cid:02d}';images.mkdir(parents=True,exist_ok=True);masks.mkdir(parents=True,exist_ok=True)
  if is_real:
   for t,i in enumerate(source_ids):
    rgbpath=images/f'{t:06d}.jpg';maskpath=masks/f'{t:06d}.png'
    if not rgbpath.exists():cropped(Image.open(r/f'frames/{i+1:06d}.jpg').convert('RGB')).save(rgbpath,quality=95)
    if not maskpath.exists():cropped(Image.open(r/f'masks/{i+1:06d}.png').convert('L')).save(maskpath)
  else:
   video=Path(generated['target_videos'][original_id])
   if len(list(images.glob('*.jpg')))!=121:
    for t,frame in enumerate(iter_rgb_video(video)):Image.fromarray(frame).save(images/f'{t:06d}.jpg',quality=95)
   if len(list(masks.glob('*.png')))!=121:
    paths=sorted(images.glob('*.jpg'))
    frames=(np.asarray(Image.open(path).convert('RGB')) for path in paths)
    with closing(iter_foreground_masks(frames,work/'models/birefnet','cuda',batch_size=2)) as predictions:
     for t,mask in enumerate(predictions):Image.fromarray(mask).save(masks/f'{t:06d}.png')
  print('MULTIVIEW_DATA_CAMERA',cid,'observed' if is_real else 'generated',flush=True)
 write_json(data/'cameras.json',{'camera_model':'OPENCV','cameras':camrows})
 write_json(data/'metadata.json',{'fps':'30','frames':[f'{i:06d}' for i in range(121)],'source_identity':f'SOMA-calibrated original RGB + selected 4DAnyone priors; 3:{5-len(excluded)} observed/generated sampling; rejected generated IDs {sorted(excluded)}'})
 write_json(out/'PROVENANCE.json',{'original_camera_ids':[c['camera_id'] for c in camrows if c['supervision']=='observed'],'duplicated_observations_for_loss_weighting':True,'synthetic_camera_ids':[c['camera_id'] for c in camrows if c['supervision']=='generated'],'original_view_to_contiguous_slot':[{k:c[k] for k in ['camera_id','supervision','original_generated_camera_id','generator_pass']} for c in camrows],'explicitly_rejected_generated_camera_ids':sorted(excluded),'generated_front_excluded':True,'not_independent_novel_view_ground_truth':True,'source_frames':source_ids,'method':'Native conditional 4D Gaussian implementation released with 4DAnyone, custom calibrated source-preserving dataset. Not FreeTimeGS paper reproduction.'})
 if a.prepare_only:raise SystemExit(0)
 options={'steps':a.steps,'batch_size':4,'image_scale':.5,'bounds':((-1.2,-.1,-.7),(1.2,2.3,.7)),'voxel_size':.025,'perceptual_weight':0.,'loader_workers':4,'log_every':100,'save_every':5000}
 settings=training_settings(options);check_runtime(settings,'cuda');training_data=TrainingData(data,image_scale=.5)
 if not (out/'initialization/metadata.json').exists():carve(training_data,out/'initialization','cuda',bounds=settings['bounds'],voxel_size=settings['voxel_size'],carve_chunk=settings['carve_chunk'])
 checkpoint=train(training_data,InitialPoints(out/'initialization'),out,settings,'cuda',resume=(out/'checkpoints/latest.pt').exists(),stop_after=a.stop_after)
 print('MULTIVIEW_4D_CHECKPOINT',str(checkpoint),flush=True)

if __name__ == "__main__":
 main()
