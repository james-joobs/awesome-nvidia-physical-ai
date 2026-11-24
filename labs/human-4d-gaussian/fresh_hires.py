"""High-resolution warm start with selected calibrated source/generated views."""
import argparse,importlib,json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from contextlib import closing

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--steps',type=int,default=6000);p.add_argument('--stop-after',type=int,default=6000);p.add_argument('--prepare-only',action='store_true');a=p.parse_args();r=a.root;work=r/'multiview-prior';sys.path.insert(0,str(work/'4danyone'))
 from fdanyone.video import iter_rgb_video
 from fdanyone.foreground import iter_foreground_masks
 from fdanyone.reconstruction.data import TrainingData,write_json
 from fdanyone.reconstruction.settings import training_settings,check_settings
 from fdanyone.reconstruction.checkpoint import load_render_model
 from fdanyone.reconstruction.pipeline import check_runtime
 import torch
 torch.set_num_threads(8)
 old=work/a.name/'reconstruction/data';out=a.out;out.mkdir(exist_ok=True);data=out/'data';data.mkdir(exist_ok=True);cameras=json.loads((old/'cameras.json').read_text())['cameras'];extra=json.loads((work/(a.name+'-offset')/'adapter.json').read_text());generation=json.loads((work/(a.name+'-offset')/'generation.json').read_text())
 for folder in ['images','fmasks']:
  (data/folder).mkdir(exist_ok=True)
  for i in [row['camera_id'] for row in cameras]:
   target=data/folder/f'{i:02d}'
   if not target.exists():target.symlink_to(old/folder/f'{i:02d}',target_is_directory=True)
 for j in range(6):
  cid=len(cameras);cameras.append({**extra['cameras'][j],'camera_id':cid,'supervision':'generated','generator_pass':'offset','original_generated_camera_id':j});images=data/f'images/{cid:02d}';masks=data/f'fmasks/{cid:02d}';images.mkdir(exist_ok=True);masks.mkdir(exist_ok=True)
  if len(list(images.glob('*.jpg')))!=121:
   for t,frame in enumerate(iter_rgb_video(generation['target_videos'][j])):Image.fromarray(frame).save(images/f'{t:06d}.jpg',quality=95)
  if len(list(masks.glob('*.png')))!=121:
   frames=(np.asarray(Image.open(path).convert('RGB')) for path in sorted(images.glob('*.jpg')))
   with closing(iter_foreground_masks(frames,work/'models/birefnet','cuda',batch_size=2)) as predictions:
    for t,mask in enumerate(predictions):Image.fromarray(mask).save(masks/f'{t:06d}.png')
  print('EXTRA_VIEW_READY',extra['cameras'][j]['yaw_degrees'],flush=True)
 for _copy in range(3):
  cid=len(cameras);cameras.append({**cameras[0],'camera_id':cid})
  for folder in ['images','fmasks']:
   target=data/folder/f'{cid:02d}'
   if not target.exists():target.symlink_to(old/folder/'00',target_is_directory=True)
 write_json(data/'cameras.json',{'camera_model':'OPENCV','cameras':cameras})
 write_json(data/'metadata.json',{'fps':'30','frames':[f'{i:06d}' for i in range(121)],'source_identity':f'Selected generated directions plus one observed camera; 6:{len(cameras)-6} real/generated sampling; copies are weighting only.'})
 if a.prepare_only:return
 settings=training_settings({'steps':a.steps,'batch_size':4,'image_scale':1.,'bounds':((-1.2,-.1,-.7),(1.2,2.3,.7)),'voxel_size':.025,'perceptual_weight':0.,'loader_workers':4,'save_every':3000,'log_every':100});settings['densify_until']=0;settings=check_settings(settings);check_runtime(settings,'cuda');training_data=TrainingData(data,image_scale=1.)
 base=a.base;resume=(out/'checkpoints/latest.pt').exists()
 if not resume:
  _,model=load_render_model(base,'cuda');module=importlib.import_module('fdanyone.reconstruction.train')
  # Warm start from the fitted model, with a new optimizer/data/recipe. The
  # original checkpoint and its training history are never rewritten.
  module.initialize_model=lambda *_args,**_kwargs:model
 fingerprint=training_data.fingerprint()
 class WarmStartPoints:
  metadata={'scene':fingerprint,'bounds':settings['bounds'],'voxel_size':settings['voxel_size']}
 provenance={'warm_start_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'warm_start':'Fitted source-preserving seed after documented teacher rejection and support culling','new_optimizer':True,'image_scale':1,'training_resolution':[704,1280],'densification_disabled':True,'observed_camera_copies':[c['camera_id'] for c in cameras if c.get('supervision')=='observed'],'generated_camera_ids':[row['camera_id'] for row in cameras if row.get('supervision')!='observed'],'loss_sampling':f'6 observed : {len(cameras)-6} generated; copies are not independent observations','extra_generator':'4DAnyone Turbo / Rank64 delta4','weight_terms':'See SOURCES.md for model and adapter terms; this flag does not grant source-video reuse rights','not_novel_view_ground_truth':True}
 write_json(out/'PROVENANCE.json',provenance)
 from fdanyone.reconstruction.train import train
 checkpoint=train(training_data,WarmStartPoints(),out,settings,'cuda',resume=resume,stop_after=a.stop_after);print('SELECTED_VIEW_HIRES_READY',checkpoint,flush=True)

if __name__=='__main__':main()
